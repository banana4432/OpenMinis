#!/usr/bin/env python3
"""Static checks for the independent iOS study build identity."""

from pathlib import Path
import plistlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
IOS = ROOT / "src" / "ios"
PROJECT = IOS / "Minis.xcodeproj" / "project.pbxproj"
APP_ID = "com.banana4432.minis.study"
APP_GROUP = f"group.{APP_ID}"
ICLOUD = f"iCloud.{APP_ID}"
EXPECTED_BUNDLE_IDS = {
    APP_ID,
    f"{APP_ID}.ShareExtension",
    f"{APP_ID}.FileProvider",
    f"{APP_ID}.AgentWidget",
    f"{APP_ID}.MinisTests",
    f"{APP_ID}.MinisUITests",
}

errors: list[str] = []

def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

for path in IOS.rglob("*"):
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if "com.openminis" in text:
        errors.append(f"old identifier remains in {path.relative_to(ROOT)}")

project_text = PROJECT.read_text(encoding="utf-8")
actual_bundle_ids = set(re.findall(r"PRODUCT_BUNDLE_IDENTIFIER = ([^;]+);", project_text))
check(EXPECTED_BUNDLE_IDS <= actual_bundle_ids,
      f"missing bundle IDs: {sorted(EXPECTED_BUNDLE_IDS - actual_bundle_ids)}")
check(all(bundle_id == APP_ID or bundle_id.startswith(APP_ID + ".")
          for bundle_id in actual_bundle_ids),
      f"unexpected bundle IDs: {sorted(actual_bundle_ids - EXPECTED_BUNDLE_IDS)}")

with (IOS / "Info.plist").open("rb") as handle:
    info = plistlib.load(handle)
check(info.get("CFBundleDisplayName") == "Minis 学习", "main display name is not Minis 学习")
url_schemes = {
    scheme
    for item in info.get("CFBundleURLTypes", [])
    for scheme in item.get("CFBundleURLSchemes", [])
}
check(APP_ID in url_schemes, "OAuth callback URL scheme does not use the study app ID")

entitlement_files = [
    IOS / "Minis.entitlements",
    IOS / "ShareExtension" / "ShareExtension.entitlements",
    IOS / "FileProvider" / "FileProvider.entitlements",
    IOS / "AgentWidget" / "AgentWidget.entitlements",
]
for path in entitlement_files:
    with path.open("rb") as handle:
        entitlements = plistlib.load(handle)
    groups = entitlements.get("com.apple.security.application-groups", [])
    check(groups == [APP_GROUP], f"incorrect App Group in {path.relative_to(ROOT)}: {groups}")

with (IOS / "Minis.entitlements").open("rb") as handle:
    main_entitlements = plistlib.load(handle)
check(main_entitlements.get("com.apple.developer.icloud-container-identifiers") == [ICLOUD],
      "incorrect CloudKit container")
check(main_entitlements.get("com.apple.developer.ubiquity-container-identifiers") == [ICLOUD],
      "incorrect ubiquity container")

if errors:
    print("Study identity verification failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("Study identity verification passed")
print(f"Display name: Minis 学习")
print(f"Main bundle ID: {APP_ID}")
print(f"App Group: {APP_GROUP}")
print(f"iCloud container: {ICLOUD}")

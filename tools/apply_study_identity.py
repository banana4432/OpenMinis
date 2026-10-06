from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
IOS = ROOT / "src" / "ios"
OLD_APP_ID = "com.openminis.app"
OLD_NAMESPACE = "com.openminis"
NEW_APP_ID = "com.banana4432.minis.study"

changed = []
for path in IOS.rglob("*"):
    if not path.is_file():
        continue
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    # Replace the app identifier only at an identifier boundary. This avoids
    # turning the separate `com.openminis.applogger` namespace into a malformed
    # `...studylogger` value.
    updated = re.sub(
        re.escape(OLD_APP_ID) + r"(?![A-Za-z0-9_])",
        NEW_APP_ID,
        original,
    )
    updated = updated.replace(OLD_NAMESPACE, NEW_APP_ID)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed.append(path.relative_to(ROOT))

info_plist = IOS / "Info.plist"
text = info_plist.read_text(encoding="utf-8")
if "<key>CFBundleDisplayName</key>" not in text:
    marker = "<dict>\n"
    replacement = "<dict>\n\t<key>CFBundleDisplayName</key>\n\t<string>Minis 学习</string>\n"
    if marker not in text:
        raise SystemExit("Info.plist root dictionary marker not found")
    info_plist.write_text(text.replace(marker, replacement, 1), encoding="utf-8")
    if info_plist.relative_to(ROOT) not in changed:
        changed.append(info_plist.relative_to(ROOT))

project = IOS / "Minis.xcodeproj" / "project.pbxproj"
text = project.read_text(encoding="utf-8")
text = text.replace('INFOPLIST_KEY_CFBundleDisplayName = "Share to Minis";',
                    'INFOPLIST_KEY_CFBundleDisplayName = "Share to Minis 学习";')
text = text.replace('INFOPLIST_KEY_CFBundleDisplayName = "Minis Files";',
                    'INFOPLIST_KEY_CFBundleDisplayName = "Minis 学习 Files";')
text = text.replace('INFOPLIST_KEY_CFBundleDisplayName = "Agent Activity";',
                    'INFOPLIST_KEY_CFBundleDisplayName = "Minis 学习 Activity";')
project.write_text(text, encoding="utf-8")

print(f"Updated {len(changed)} iOS files")
for path in changed:
    print(path)

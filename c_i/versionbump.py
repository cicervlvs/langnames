import re
import sys
from datetime import datetime
from version_bump_chooser import versionBumpType


def num_to_change():
    ver_change = versionBumpType()

    if ver_change == "minor":
        return 1
    elif ver_change == "major":
        return 0
    else:
        return "no changes"


# Read the current version from the .dtx file
dtx_file = "langnames/langnames.dtx"

with open(dtx_file, "r") as f:
    docfile = f.read()
version_pattern = r"\[\d{4}/\d{2}/\d{2} (v((\d+\.{0,1}){1,2}\d*))"
current_version = re.search(version_pattern, docfile).group(2).split(".")

print(current_version)
# Get current date
today = datetime.today().strftime("%Y/%m/%d")

print(versionBumpType())

# Increment the version number in the third level (patch), accounting for difference in typing outs
if len(current_version) < 3:
    numbers_to_add = 3 - len(current_version)
    for i in range(numbers_to_add):
        current_version.append("0")

new_version = current_version


new_version[num_to_change()] = str(int(new_version[-1]) + 1)
new_version = ".".join(new_version)
print(new_version)

# Update the .dtx file with the new version
version_update = re.sub(
    version_pattern,
    rf"[{today} v{new_version}",
    docfile,
)

with open(dtx_file, "w") as f:
    f.write(version_update)

# Add changes to file
changes_pattern = r"\% \\changes\{v((\d+\.{0,1}){1,2}\d*)}"
changes_message = f"% \\changes{{v{new_version}}}{{{today}}}{{Updated database}}"
changelog_lines = []

# find lines where changelog is
with open(dtx_file, "r") as f:
    lines = f.readlines()
    line_num = 0
    for line in lines:
        line_num += 1
        match = re.search(changes_pattern, line)
        if match:
            changelog_lines.append(line_num)

lines.insert(changelog_lines[-1], changes_message + "\n")

with open(dtx_file, "w") as f:
    f.writelines(lines)

import re
import argparse
from datetime import datetime
import subprocess

def versionBumpType():
    # Command 1: ls -l
    cmd1 = ["git", "diff"]

    # Command 2: grep "file_name"
    cmd2 = ["grep", "-E", "^-\\\\|^\+\\\\"]

    # Command 3: sort
    cmd3 = ["awk", "-F[@{]", "{print $1, " " $4}"]

    # Run the commands chained together with pipes
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)

    # Read the final output
    changes = p3.communicate()[0].decode("utf-8")

    cmd1 = ["echo", changes]

    # Command 2: grep "file_name"
    cmd2 = ["grep", "^-"]

    # Command 3: sort
    cmd3 = ["cut", "-c2-"]

    # Run the commands chained together with pipes
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)

    # Read the final output
    removals = set(p3.communicate()[0].decode("utf-8").split("\n"))

    cmd2 = ["grep", "^+"]

    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)

    # Read the final output
    additions = set(p3.communicate()[0].decode("utf-8").split("\n"))

    actual_removals = set([lang for lang in removals if lang not in additions])
    actual_additions = set([lang for lang in additions if lang not in removals])
    actual_changes = set([lang for lang in additions if lang in removals])

    if not changes:
        ver_change = "no change"
    elif not actual_removals:
        ver_change = "minor"
    else:
        ver_change = "major"

    return ver_change, actual_changes, actual_additions, actual_removals


# Read the current version from the .dtx file
dtx_file = "langnames/langnames.dtx"

parser = argparse.ArgumentParser()
parser.add_argument("--current_version", action="store_true")
args = parser.parse_args()

with open(dtx_file, "r") as f:
    docfile = f.read()
version_pattern = r"\[\d{4}/\d{2}/\d{2} (v((\d+\.{0,1}){1,2}\d*))"

current_version = re.search(version_pattern, docfile).group(2)
current_version_nums = current_version.split(".")

if args.current_version:
    print(current_version)
    exit(0)

# Get current date
today = datetime.today().strftime("%Y/%m/%d")

# Increment the version number in the third level (patch), accounting for difference in typing outs
if len(current_version_nums) < 3:
    numbers_to_add = 3 - len(current_version_nums)
    for i in range(numbers_to_add):
        current_version_nums.append("0")

versionBumpType, actual_changes, actual_additions, actual_removals = versionBumpType()

if versionBumpType == "major":
    first_number = int(current_version_nums[0]) + 1
    new_version = f"{first_number}.0.0"
elif versionBumpType == "minor":
    second_number = int(current_version_nums[1]) + 1
    new_version = f"{current_version_nums[0]}.{second_number}.0"
else:
    new_version = current_version


print(versionBumpType)
print(new_version)
print(len(actual_changes))
print(len(actual_additions))
print(len(actual_removals))

# Update the .dtx file with the new version
if new_version != current_version:
    version_update = re.sub(
        version_pattern,
        rf"[{today} v{new_version}",
        docfile,
    )

    with open(dtx_file, "w") as f:
        f.write(version_update)

    # find lines where changelog is
    changes_pattern = r"\% \\changes\{v((\d+\.{0,1}){1,2}\d*)}"
    changes_message = (
        f"% \\changes{{v{new_version}}}{{{today}}}{{Updated the database}}"
    )
    changelog_lines = []

    # Add changes to file
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

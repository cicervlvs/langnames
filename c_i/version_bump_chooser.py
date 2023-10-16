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

    if len(changes) == 0:
        ver_change = "no change"
    elif len(actual_removals) == 0:
        ver_change = "minor"
    else:
        ver_change = "major"

    print(ver_change)


if __name__ == "__main__":
    versionBumpType()

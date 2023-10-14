import subprocess


def versionBumpType():

    # Command 1: ls -l
    cmd1 = ["git", "diff"]

    # Command 2: grep "file_name"
    cmd2 = ["grep", "-E", "^-\\\\|^\+\\\\"]

    # Command 3: sort
    cmd3 = ["awk", "-F[\\\\\@{]", "{print $1 $6}"]

    # Run the commands chained together with pipes
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)

    # Read the final output
    changes = p3.communicate()[0].decode('utf-8')

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
    removals = p3.communicate()[0].decode('utf-8')

    cmd2 = ["grep", "^\+"]
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=subprocess.PIPE)

    # Read the final output
    additions = p3.communicate()[0].decode('utf-8')



    print(changes)
    print(removals)
    print(additions)


    ## Convert removals and additions into sets, one element per line
    ## If removals and additions are empty -> Undetermined
    ## Substract removals from additions, if resulting Set > 0. Major bump else minor bump


if __name__ == "__main__":
    versionBumpType()

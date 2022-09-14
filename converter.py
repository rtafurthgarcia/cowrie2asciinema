from distutils.cmd import Command
from playlog import playlog
from asciinema import record

import getopt
import os
import sys

def help(brief=0):
    print(
        "\nUsage: %s <directory-to-watch> <output-directory>\n"
        % os.path.basename(sys.argv[0])
    )

    print("Converts Cowrie's UML compatible files to a format understood by ASCIInema.")
    print("Watches over a directory, output the converted records and dump em in a PostgreSQL database.\n")

    print("Positional arguments:\n")
    print(
        "directory-to-watch             path to the directory where uml files are gonna be dropped"
    )
    print(
        "output-directory               path to save the converted recordings to\n"
    )

    print("Options:")
    print("  -H, --host         PostgreSQL host")
    print("  -P, --port         PostgreSQL port")
    print("  -u, --username     PostgreSQL username")
    print("  -p, --password     PostgreSQL password")
    print("  -s, --schema       PostgreSQL schema\n")

    print("  -h, --help         display this help\n")

    sys.exit(1)


if __name__ == "__main__":

    settings = {
        "host": "localhost",
        "port": 5432,
        "username": "root",
        "password": "",
        "schema": "",
    }

    try:
        optlist, args = getopt.getopt(sys.argv[1:], "h:HPups:", ["help"])
    except getopt.GetoptError as error:
        print("Error: %s\n" % error)
        help()

    options = [x[0] for x in optlist]

    for argument, value in optlist:
        if argument in ["-H", "--host"]:
            settings["host"] = value
        elif argument in ["-P", "--port"]:
            settings["port"] = int(value) 
        elif argument in ["-u", "--username"]:
            settings["username"] = value
        elif argument in ["-p", "--port"]:
            settings["password"] = value
        elif argument in ["-s", "--schema"]:
            settings["schema"] = value
        elif argument in ["-h", "--help"]:
            help()

    if len(args) < 1:
        help()

    try:
        for directory in args:
            print(directory)
            #playlog(logfd, settings)
    except OSError:
        print("\n\n[!] Couldn't open log file (%s)!" % directory)
        sys.exit(2)

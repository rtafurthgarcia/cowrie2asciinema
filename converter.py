from asciinema import record

import pyinotify

import getopt
import os
import sys

import psycopg2
import random

RECORD_SETTINGS = {
    "tail": 0,
    "maxdelay": 3.0,
    "input_only": 0,
    "both_dirs": 0,
    "colorify": 0,
}

settings = {
    "host": "localhost",
    "port": 5432,
    "username": "root",
    "password": "",
    "schema": "",
    "id": 1,
    "directory_to_watch": "",
    "output_directory": "",
    "idle_time_limit": 15
}

class EventHandler(pyinotify.ProcessEvent):
    #def process_IN_CREATE(self, event):
    def process_default(self, event):
        print("Converting file %s\n" % event.pathname)
        converted_file_path = os.path.join(settings["output_directory"], os.path.basename(event.pathname) + ".cast")
        record(
            command="python3 playlog.py %s" % event.pathname, 
            path_=converted_file_path, 
            idle_time_limit=settings["idle_time_limit"],
        )

        if is_db_config_valid():
            insert_new_video(os.path.basename(event.pathname) + ".cast")

def help():
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
    print("  -s, --schema       PostgreSQL schema")
    print("  -i, --id           Primary key of the video's owner\n")

    print("  -l, --limit        Idle time limit in seconds\n")

    print("  -h, --help         display this help\n")

    sys.exit(1)

def is_db_config_valid():
    is_valid = True

    if len(settings["host"]) == 0:
        is_valid = False
    if settings["port"] < 1024:
        is_valid = False
    if len(settings["username"]) == 0:
        is_valid = False
    if len(settings["password"]) == 0:
        is_valid = False
    if len(settings["schema"]) == 0:
        is_valid = False
    if settings["id"] < 1:
        is_valid = False

    return is_valid

def insert_new_video(converted_file: str):
    db_connection = psycopg2.connect(
        database=settings["schema"], 
        user=settings["username"], 
        password=settings["password"], 
        host=settings["host"], 
        port=settings["port"]
    )
    db_connection.autocommit = False

    cursor = db_connection.cursor()

    query = "INSERT INTO video (sekundaerid, video, titel, beschreibung, benutzerid, istprivat, istkommentierbar, erstellungsdatum)\n" 
    query += "VALUES ({}, '{}' , '{}', '', {}, false, true, CURRENT_TIMESTAMP);".format(random.randint(100000, 999999), converted_file, converted_file[:49], settings["id"])
    cursor.execute(query=query)

    db_connection.close()

if __name__ == "__main__":
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "HPupsli:h", ["host=", "port=", "username=", "password=", "schema=", "limit=", "id="])
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
        elif argument in ["-p", "--password"]:
            settings["password"] = value
        elif argument in ["-s", "--schema"]:
            settings["schema"] = value
        elif argument in ["-i", "--id"]:
            settings["id"] = int(value)
        elif argument in ["-l", "--limit"]:
            settings["idle_time_limit"] = int(value)
        elif argument in ["-h", "--help"]:
            help()

    if len(args) < 2:
        help()

    try:
        for directory in args:
            if not os.path.isdir(directory): raise OSError()

        settings["directory_to_watch"] = args[0]
        settings["output_directory"] = args[1]

        wm = pyinotify.WatchManager()

        mask = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE

        handler = EventHandler()
        notifier = pyinotify.Notifier(wm, handler)
        wdd = wm.add_watch(settings["directory_to_watch"], mask, rec=True)

        notifier.loop()

    except OSError:
        print("\n[!] Directory (%s) doesn't exist !" % directory)
        sys.exit(2)
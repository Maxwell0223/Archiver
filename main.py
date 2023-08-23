# Incomaker Archiver
# 1.0.0
# Maxwell Wippich

import os
import tarfile
import time
from subprocess import call


LOCK_FILENAME = "inco.lock"
SKIP_FILENAME = "inco.skip"
GLOBAL_ARCHIVED_FILES_FILENAME = "archived_files.txt"

settings = dict([("WORKDIR", "/Users/maxwellwippich/Incomaker/data_to_process/data_to_process"),
                 ("SAFETY_CUSHION", 0),
                 ("ARCHIVER", "bz2"),
                 ("PROCESS_TIMEOUT", 86400)])

global_archived_files = set()


def main():
    #read_settings()

    for dir in [f for f in os.listdir(settings["WORKDIR"]) if os.path.isdir(settings["WORKDIR"] + "/" + f) and (
            int(time.time() - os.path.getmtime(settings["WORKDIR"] + "/" + f)) > settings["SAFETY_CUSHION"])]:
        campaign_dir = settings["WORKDIR"] + "/" + dir
        if not lock_exists(campaign_dir):
            write_sign(campaign_dir + "/" + LOCK_FILENAME)
            if parse_triggers(campaign_dir):
                write_sign(campaign_dir + "/" + SKIP_FILENAME)
            os.remove(campaign_dir + "/" + LOCK_FILENAME)
        else:
            exit()


def parse_triggers(dir):
    os.chdir(dir)
    for trigdir in [f for f in os.listdir(dir)
                    if (int(time.time() - os.path.getmtime(dir + "/" + f)) > settings["SAFETY_CUSHION"])]:
        archive_subdirectory(trigdir)


def load_global_archived_files():
    file_path = os.path.join(settings["WORKDIR"], GLOBAL_ARCHIVED_FILES_FILENAME)
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            for line in f:
                file = line.strip()
                if file:
                    global_archived_files.add(file)
    else:
        # Create a new file if it doesn't exist
        with open(file_path, "w") as f:
            pass


def save_global_archived_files():
    file_path = os.path.join(settings["WORKDIR"], GLOBAL_ARCHIVED_FILES_FILENAME)
    with open(file_path, "w") as f:
        for file in global_archived_files:
            f.write(file + "\n")


def write_sign(sign_file):
    with open(sign_file, "w") as f:
        f.write(str(time.time()))
        f.close()


def skip_exists(workdir):
    return os.path.isfile(workdir + "/" + SKIP_FILENAME)


def lock_exists(workdir):
    try:
        file_name = workdir + "/" + LOCK_FILENAME
        with open(file_name, "r") as f:
            if int(f.read()) < time.time() - settings["PROCESS_TIMEOUT"]:
                os.remove(file_name)
                return False
    except Exception:
        return False
    return True


"""
def read_settings():
    global settings
    file_path = ""
    if platform.system() == "Linux":
        file_path = "/etc/"
    with open(file_path + "incoarchiver.yaml", "r") as f:
        settings = yaml.safe_load(f)
    settings_defaults()
"""


def settings_defaults():
    if "PROCESS_TIMEOUT" not in settings:
        settings["PROCESS_TIMEOUT"] = 86400
    if "SAFETY_CUSHION" not in settings:
        settings["SAFETY_CUSHION"] = 86400


def archive_subdirectory(directory):
    if directory.endswith(".skip"):
        return
    if not os.path.isdir(directory) and not directory.endswith(".tar.bz2"):
        null_dir = "null"
        os.makedirs(null_dir, exist_ok=True)
        null_archive_file = os.path.join(null_dir + '.tar.' + settings["ARCHIVER"])

        if os.path.isfile(null_archive_file):
            call(["tar", "-xJf", null_archive_file])
            call(["rm", "-r", null_archive_file])
        print(null_archive_file)
        print(null_dir)
        call(["mv", directory, null_dir])
        call(["tar", "-cvjSf", null_archive_file, null_dir])
        call(["rm", "-r", null_dir])
    else:
        archive_file = os.path.join(directory + '.tar.' + settings["ARCHIVER"])

        if os.path.isfile(archive_file):
            call(["tar", "-xJf", archive_file])
            call(["rm", "-r", archive_file])

        call(["tar", "-cvjSf", archive_file, directory])
        call(["rm", "-r", directory])

def get_global_archived_files(parent_directory):
    archived_files = set()
    for root, dirs, files in os.walk(parent_directory):
        for file in files:
            if file.endswith(".tar." + settings["ARCHIVER"]):
                with tarfile.open(os.path.join(root, file), 'r') as tar:
                    archived_files.update(tar.getnames())
    return archived_files


if __name__ == '__main__':
    #load_global_archived_files()
    main()
    #save_global_archived_files()

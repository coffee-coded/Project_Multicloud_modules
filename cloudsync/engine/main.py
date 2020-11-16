import time

from classes.files.files import Files
from classes.bcolors import bcolors
from classes.directory.directory import Directory


def input_path():
    p = []
    running = True
    print(bcolors.FAIL + bcolors.BOLD + "Input Path : " + bcolors.ENDC)
    while running:
        x = input()
        if x == "":
            break
        else:
            p.append(x)
    return p


if __name__ == '__main__':
    path = input_path()
    f = Files(path)
    d = Directory(path)
    print(bcolors.BOLD + bcolors.OKBLUE + "Instance Initiated" + bcolors.ENDC)
    print(bcolors.BOLD + bcolors.FAIL + "10 second clock cycle by default" + bcolors.ENDC)
    while True:
        f.scan_files()
        d.scan_direct()
        time.sleep(10)

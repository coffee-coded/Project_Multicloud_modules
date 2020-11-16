import os
from classes.bcolors import bcolors
from classes.upload import AwsUpload


class Directory:
    def __init__(self, path):
        self.path = path
        self.direct = []
        self.curr_direct = []
        self.first_run()
        self.aws = AwsUpload()

    def first_run(self):
        # r=root, d=directories, f = files
        for p in self.path:
            for r, d, f in os.walk(p):
                for dr in d:
                    self.direct.append(os.path.join(r, dr))

    def exist(self, num, arr):
        for i in arr:
            if i == num:
                return i
        return -1

    def check(self):
        if self.curr_direct == self.direct:
            return
        else:
            self.add_direct()
            self.remove_direct()

    def add_direct(self):
        for dr in self.curr_direct:
            if self.exist(dr, self.direct) == -1:
                print(bcolors.WARNING + "Directories added : " + bcolors.ENDC + dr)
                self.direct.append(dr)

    def scan_direct(self):
        self.curr_direct = []
        # r=root, d=directories, f = files
        for p in self.path:
            for r, d, f in os.walk(p):
                for dr in d:
                    self.curr_direct.append(os.path.join(r, dr))
            self.check()

    def print_directories(self):
        for d in self.direct:
            print(d)

    def remove_direct(self):
        dl = []
        for d in self.direct:
            if self.exist(d, self.curr_direct) == -1:
                dl.append(d)
        for d in dl:
            print(bcolors.FAIL + "Directories removed : " + bcolors.ENDC, d)
            self.direct.remove(d)

import os
from classes.bcolors import bcolors
from classes.upload import AwsUpload


class Files:
    def __init__(self, path):
        self.path = path
        self.files = []
        self.curr_files = []
        self.first_run()
        self.aws = AwsUpload()

    def first_run(self):
        # r=root, d=directories, f = files
        for p in self.path:
            for r, d, f in os.walk(p):
                for file in f:
                    self.files.append(os.path.join(r, file))

    @staticmethod
    def exist(num, arr):
        for i in arr:
            if i == num:
                return i
        return -1

    def check(self):
        if self.curr_files == self.files:
            return
        else:
            self.add_files()
            self.remove_files()

    def add_files(self):
        for file in self.curr_files:
            if self.exist(file, self.files) == -1:
                self.aws.upload_to_aws(file)
                print(bcolors.BOLD + bcolors.WARNING + "Files added : " + bcolors.ENDC + file)
                self.files.append(file)

    def scan_files(self):
        self.curr_files = []
        # r=root, d=directories, f = files
        for p in self.path:
            for r, d, f in os.walk(p):
                for file in f:
                    self.curr_files.append(os.path.join(r, file))
        self.check()

    def print_files(self):
        for f in self.files:
            print(f)
            print("\n")

    def remove_files(self):
        fl = list()
        for f in self.files:
            if self.exist(f, self.curr_files) == -1:
                fl.append(f)
        for f in fl:
            self.aws.remove_from_aws(f)
            print(bcolors.BOLD + bcolors.FAIL + "Files removed : " + bcolors.ENDC + f)
            self.files.remove(f)

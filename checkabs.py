#!/usr/bin/env python3

import subprocess
import sys
import os
import shutil

script, abs_package = sys.argv

class checkABS:
    def __init__(self):
        self.package = abs_package
        isUpdate = input("Would you like to update abs? (y/n) ").lower()
        if isUpdate == "y":
            try:
                print("\nUpdating ABS\n")
                subprocess.call(["/usr/bin/sudo", "/usr/bin/abs"])
                self.buildPackage()
            except OSError:
                print("\nYou do not have sudo/abs installed\n")
                sys.exit(1)
        else:
            self.buildPackage()
            
    def buildPackage(self):
        filePath = bytes.decode(subprocess.check_output(["/usr/bin/find", "/var/abs/", "-name", self.package]).rstrip())
        
        try:
            print("\nCopying", filePath, "to /tmp")
            subprocess.call(["/usr/bin/cp", "-r", filePath, "/tmp/"])
        except OSError:
            print("\nUnable to copy", filePath, "to /tmp\n")
            sys.exit(1)

        try:
            packageDir = "/tmp/" + self.package
            os.chdir(packageDir)
        except OSError:
            print("\nCouldn't change to the copied directory:", packageDir)
            sys.exit(1)

        try:
            print("\nBuilding the package now!\n")
            subprocess.call(["makepkg", "-rsi"])
        except OSError:
            print("\nCouldn't makepkg")
            sys.exit(1)

        try:
            print("\nRemoving build directory:", packageDir, "\n")
            shutil.rmtree(packageDir)
        except OSError:
            print("\nCouldn't remove the build directory:", packageDir)
            sys.exit(1)

checkABS()

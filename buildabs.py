#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil

package = None
editPKGBUILD = False
updateABS = False

class buildABS:
    def __init__(self, package, editPKGBUILD, updateABS):
        self.package = package
        try:
            self.packagePath = bytes.decode(subprocess.check_output(["/usr/bin/find", "/var/abs/", "-name", self.package]).rstrip())
        except:
            print("\nCan't find package in /var/abs/")
            print("Command: /usr/bin/find /var/abs/ -name " + self.package)
        self.editPKGBUILD = editPKGBUILD
        self.updateABS = updateABS
        self.repoVersion = self.repoInfo()

    def updateABSRepo(self):
        try:
            print("\nUpdating ABS repo...\n")
            subprocess.call(["/usr/bin/sudo", "abs"])
        except:
            print("\nError updating ABS repo. Check for sudo command or sudo privileges.")
            print("Command: /usr/bin/sudo abs")

    def doEditPKGBUILD(self):
        try:
            subprocess.call([os.getenv('EDITOR'), "/tmp/" + self.package + "/PKGBUILD"])
        except:
            print("\nFile not found")
            print("Command:", os.getevn('EDITOR'), "/tmp/" + self.package + "/PKGBUILD")

    def repoInfo(self):
        try:
            info = bytes.decode(subprocess.check_output(["/usr/bin/pacman", "-Si", self.package]).rstrip())
            info = info.split('\n')
            info = info[2].split(':')
            info = info[1].lstrip()
            return info
        except:
            print("\nError processing command. Check package name or arguments passed.")
            print("Command: /usr/bin/pacman -Si " + self.package)
            sys.exit(1)

    def absVersion(self):
        try:
            pkgver = bytes.decode(subprocess.check_output(["/usr/bin/grep", "pkgver=", self.packagePath + "/PKGBUILD"]).rstrip())
            pkgrel = bytes.decode(subprocess.check_output(["/usr/bin/grep", "pkgrel=", self.packagePath + "/PKGBUILD"]).rstrip())
            pkgver = pkgver.split('=')
            pkgver = pkgver[1]
            pkgrel = pkgrel.split('=')
            pkgrel = pkgrel[1]
            pkgver = pkgver + '-' + pkgrel
            return pkgver
        except:
            print("Can't find PKGBUILD / grep.")
            print("Command: /usr/bin/grep pkgver= " + self.packagePath + "/PKGBUILD")
            sys.exit(1)

    def copyFromABS(self):
        try:
            print("\nCopying files from", self.packagePath, "to /tmp/" + self.package)
            subprocess.call(["/usr/bin/cp", "-r", self.packagePath, "/tmp/"])
        except:
            print("\nError copying the file. I don't know what happened.")
            print("Command: /usr/bin/cp -r " + self.packagePath + " /tmp/")
            sys.exit(1)

    def buildPackage(self):
        try:
            os.chdir("/tmp/" + self.package)
            print("\nBuilding the package now...\n")
            subprocess.call(["/usr/bin/makepkg", "-rsi"])
        except:
            print("\nFile not found. Aborting!")
            print("Command: /usr/bin/makepkg -rsi")
            sys.exit(1)

    def removeBuildDir(self):
        try:
            print("\nRemoving the build directory: /tmp/" + self.package + "\n")
            shutil.rmtree("/tmp/" + self.package)
        except:
            print("Attempt to remove package directory failed: /tmp/" + self.package)
            print("Might require elevated privileges. You'll have to remove it manually.")
            sys.exit(1)

    def checkInstall(self):
        try:
            isInstalled = bytes.decode(subprocess.check_output(["/usr/bin/pacman", "-Qi", self.package]).rstrip())
            isInstalled = isInstalled.split("\n")
            isInstalled = isInstalled[1].split(":")
            if isInstalled[1].lstrip() == self.repoVersion:
                return True
            else:
                return False
        except:
            print("\nPacman not found or bad package name.")
            print("Command: /usr/bin/pacman -Qi", self.package)
            sys.exit(1)

class ArgumentParser:
    def __init__(self):
        self.args = sys.argv

    def parse(self):
        global package
        global editPKGBUILD
        global updateABS
        del self.args[0]
        package = self.args[len(self.args) - 1]
        del self.args[len(self.args) - 1]
        for index in range(len(self.args)):
            if self.args[index].lower() == '-u' or self.args[index].lower() == '--update':
                updateABS = True
            if self.args[index].lower() == '-e' or self.args[index].lower() == '--edit':
                editPKGBUILD = True
            #if self.args[index].lower() == '-h' or self.args[index].lower() == '--help':
            #    usage()

        return

def usage():
    print("buildabs  -- builds packages from ABS")
    print()
    print("Usage:")
    print("\t./buildabs.py [options] <package>")
    print()
    print("Options:")
    print("\t-u, --update\t Update the ABS before building. Requires sudo.")
    print("\t-e, --edit\t   Edit the PKGBUILD before building.")
    print("\t-h, --help\t   Show this help message.")
    print()
    print("buildabs will copy the package directory from the ABS tree.")
    print("into /tmp/<package>. It will install build/run dependencies")
    print("and remove the build dependencies after install. It will then")
    print("remove the build directory from /tmp on successful installation.")
    sys.exit(1)

if __name__ == "__main__":
    argp = ArgumentParser()
    argp.parse()

    pkg = buildABS(package, editPKGBUILD, updateABS)
    if pkg.updateABS == True:
        pkg.updateABSRepo()
    if pkg.repoInfo() == pkg.absVersion():
        pkg.copyFromABS()
        if pkg.editPKGBUILD == True:
            pkg.doEditPKGBUILD()
        pkg.buildPackage()
        if pkg.checkInstall() == True:
            pkg.removeBuildDir()
        else:
            print(pkg.package, "failed to install. You can install manually.")
            sys.exit
    else:
        continueBuild = input("\nRepo version is newer than ABS version. Would you like to contine? (y/n) ")
        if continueBuild == 'y':
            pkg.copyFromABS()
            pkg.buildPackage()
            if pkg.checkInstall() == True:
                pkg.removeBuildDir()
            else:
                print(pkg.package, "failed to install. You can install manually.")
                sys.exit
        else:
            sys.exit

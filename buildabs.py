#!/usr/bin/env python3

import subprocess
import os
import sys
import shutil

script, package = sys.argv

class buildABS:
      def __init__(self):
            self.package = package
            self.packagePath = bytes.decode(subprocess.check_output(["/usr/bin/find", "/var/abs/", "-name", self.package]).rstrip())
            self.continueBuild = ""
            self.repoVersion = ""

            self.repoInfo()
            print("Repo Version:", self.repoVersion)
            self.absVersion()
            if self.continueBuild == 'y':
                  self.copyFromABS()
                  self.buildPackage()
                  if self.checkInstall() == True:
                        self.removeBuildDir()
                  else:
                        print(self.package, "failed to install. You can install manually.")
                        sys.exit
            else:
                  sys.exit

      def repoInfo(self):
            try:
                  info = bytes.decode(subprocess.check_output(["/usr/bin/pacman", "-Si", self.package]).rstrip())
                  info = info.split('\n')
                  info= info[2].split(':')
                  self.repoVersion = info[1].lstrip()
                  return self.repoVersion
            except FileNotFoundError:
                  print("File not found.")
                  sys.exit(1)

      def absVersion(self):
            try:
                  pkgver = bytes.decode(subprocess.check_output(["/usr/bin/grep", "pkgver=", self.packagePath + "/PKGBUILD"]).rstrip())
                  pkgrel = bytes.decode(subprocess.check_output(["/usr/bin/grep", "pkgrel=", self.packagePath + "/PKGBUILD"]).rstrip())
                  print("\nABS Version:", pkgver)
                  print("ABS Release:", pkgrel)
                  self.continueBuild = input("\nWould you like to continue the build? (y/n) ").lower()
                  return self.continueBuild
            except FileNotFoundError:
                  print("Can't find PKGBUILD / grep.")
                  sys.exit(1)

      def copyFromABS(self):
            try:
                  print("\nCopying files from", self.packagePath, "to /tmp/" + self.package)
                  subprocess.call(["/usr/bin/cp", "-r", self.packagePath, "/tmp/"])
            except OSError as e:
                  print(e.code)
                  sys.exit(1)

      def buildPackage(self):
            try:
                  os.chdir("/tmp/" + self.package)
                  edit = input("\nWould you like to edit the PKGBUILD? (y/n) ").lower()
                  if edit == 'y':
                        try:
                              subprocess.call([os.getenv('EDITOR'), "/tmp/" + self.package + "/PKGBUILD"])
                        except OSError as e:
                              print(e.code)
                  print("\nBuilding the package now...\n")
                  subprocess.call(["/usr/bin/makepkg", "-rsi"])
            except OSError as e:
                  print(e.code)
                  sys.exit(1)
      
      def removeBuildDir(self):
            try:
                  print("\nRemoving the build directory: /tmp/" + self.package + "\n")
                  shutil.rmtree("/tmp/" + self.package)
            except OSError as e:
                  print(e.code)
                  print("\nMight require elevated privileges. You'll have to remove it manually.")
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
            except FileNotFoundError:
                  print("File not found")
                  sys.exit(1)

buildABS()

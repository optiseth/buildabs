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

            self.absVersion()
            if self.continueBuild == 'y':
                  self.copyFromABS()
                  self.buildPackage()
                  self.removeBuildDir()
            else:
                  sys.exit
            

      def absVersion(self):
            try:
                  pkgver = bytes.decode(subprocess.check_output(["/usr/bin/grep", "pkgver=", self.packagePath + "/PKGBUILD"]).rstrip())
                  pkgrel = bytes.decode(subprocess.check_output(["/usr/bin/grep", "pkgrel=", self.packagePath + "/PKGBUILD"]).rstrip())
                  print("\nABS Version:", pkgver)
                  print("ABS Release:", pkgrel)
                  self.continueBuild = input("\nWould you like to continue the build? (y/n) ").lower()
                  return self.continueBuild
            except OSError as e:
                  print(e.code)
                  sys.exit

      def copyFromABS(self):
            try:
                  print("\nCopying files from", self.packagePath, "to /tmp/" + self.package)
                  subprocess.call(["/usr/bin/cp", "-r", self.packagePath, "/tmp/"])
            except OSError as e:
                  print(e.code)
                  sys.exit

      def buildPackage(self):
            try:
                  os.chdir("/tmp/" + self.package)
                  edit = input("\nWould you like to edit the PKGBUILD? (y/n) ").lower()
                  if edit == 'y':
                        try:
                              subprocess.call([os.getenv('EDITOR'), "/tmp/" + self.package + "/PKGBUILD"])
                        except OSError as e:
                              print(e.code)
                  print("\nBuilding the package now...")
                  subprocess.call(["/usr/bin/makepkg", "-rsi"])
            except OSError as e:
                  print(e.code)
                  sys.exit
      
      def removeBuildDir(self):
            try:
                  print("\nRemoving the build directory: /tmp/" + self.package + "\n")
                  shutil.rmtree("/tmp/" + self.package)
            except OSError as e:
                  print(e.code)
                  print("\nMight require elevated privileges. You'll have to remove it manually.")
                  sys.exit

buildABS()

#!/usr/bin/env python3
# encoding: utf-8

import configparser
import os
import sys

from urllib.request import urlretrieve

# cdimage url
baseUrl = "http://cdimage/daily-live-next/desktop"

# factory dir
targetDir = "/var/lib/openqa/factory/iso"

def checkBuildNum(isoName, build):

    # check file exists
    isoPath = os.path.join(targetDir, isoName)
    if not os.path.exists(isoPath):
        return False

    # check iso build version
    isoConfigFile = os.path.join(targetDir, "iso.ini")
    if not os.path.exists(isoConfigFile):
        return False
    config = configparser.ConfigParser()
    config.read(isoConfigFile)
    if isoName not in config:
        return False
    date = config[isoName]["BuildDate"]
    if date != build:
        return False

    return True

def storeBuildNum(isoName, build):
    isoConfigFile = os.path.join(targetDir, "iso.ini")
    config = configparser.ConfigParser()
    if os.path.exists(isoConfigFile):
        config.read(isoConfigFile)
    if isoName not in config:
        config[isoName] = {}
    config[isoName]["BuildDate"] = build
    with open(isoConfigFile, "w") as f:
        config.write(f)

def downloadISO(arch, build):
    isoName = "deepin-desktop-%s.iso" % arch

    isoUrl = "%s/%s/%s" % (baseUrl, build, isoName)
    if not checkBuildNum(isoName, build):
        print ("Download iso: %s" % isoUrl)
        urlretrieve(isoUrl, os.path.join(targetDir, isoName))
        # write back after downloading
        storeBuildNum(isoName, build)
    else:
        print ("ISO is exist, skip downloading.")

if __name__ == "__main__":
    ver = "20150326"
    arch = "amd64"

    if len(sys.argv) > 1:
        arch = sys.argv[1]

    if len(sys.argv) > 2:
        ver = sys.argv[2]

    downloadISO(arch, ver)

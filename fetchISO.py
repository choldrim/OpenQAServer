#!/usr/bin/env python3
# encoding: utf-8

import configparser
import os
import sys

from urllib.request import urlretrieve
from urllib.error import URLError

import util

# cdimage url
desktopBaseUrl = "http://cdimage/daily-live-next/desktop/"
sidBaseUrl = "http://cdimage/daily-live-sid/"

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

def downloadISO(arch, build, flavor="DVD"):

    t = "desktop"
    baseUrl = desktopBaseUrl
    if flavor == "SID-DVD" or flavor == "SID-PXE":
        t = "sid"
        baseUrl = sidBaseUrl

    isoName = "deepin-%s-%s.iso" % (t, arch)
    isoNameForStore = "deepin-%s-%s_%s.iso" % (t, arch, build)

    isoPath = os.path.join(targetDir, isoNameForStore)
    if not os.path.exists(isoPath):
        isoUrl = "%s/%s/%s" % (baseUrl, build, isoName)
        print ("Download iso: %s ..." % isoUrl)
        try:
            urlretrieve(isoUrl, os.path.join(targetDir, isoNameForStore))
        except URLError as e:
            print (" ------------ Error ---------------")
            print (e)
            print ("url: ", isoUrl)
            raise e
    else:
        print ("ISO is exist, skip download.")

if __name__ == "__main__":
    arch = "amd64"
    flavor = "DVD"

    if len(sys.argv) > 1:
        arch = sys.argv[1]

    if len(sys.argv) > 2:
        flavor = sys.argv[2]

    if len(sys.argv) > 3:
        build = sys.argv[3]

    build = util.getLatestBuildDate(flavor, arch)

    downloadISO(arch, build, flavor)

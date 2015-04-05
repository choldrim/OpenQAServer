#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
from urllib.request import urlretrieve

baseUrl = "http://cdimage/daily-live-next/desktop"
targetDir = "/var/lib/openqa/factory/iso"

def downloadISO(arch, ver):
    isoName = "deepin-desktop-%s.iso" % arch

    isoUrl = "%s/%s/%s" % (baseUrl, ver, isoName)
    print ("Download iso: %s" % isoUrl)
    urlretrieve(isoUrl, os.path.join(targetDir, isoName))

if __name__ == "__main__":
    ver = "current"
    arch = "amd64"

    if len(sys.argv) > 1:
        arch = sys.argv[1]

    if len(sys.argv) > 2:
        ver = sys.argv[2]

    downloadISO(arch, ver)

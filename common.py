#!/usr/bin/env python3
# encoding: utf-8

import util

def initParams(testDir, rawParams):

    params = rawParams.strip()

    if "DISTRI" in params:
        print("You don't need set the DIRSTRI in params, please remove it and try again.")
        return None

    if len(params) > 0:
        params += ",DISTRI=%s" % testDir
    else:
        params += "DISTRI=%s" % testDir

    if "FLAVOR" not in params:
        params += ",FLAVOR=DVD"

    if "ARCH" not in params:
        params += ",ARCH=x86_64"

    if "VERSION" not in params:
        params += ",VERSION=2014.2"

    if "USERNAME" not in params:
        params += ",USERNAME=deepin"

    if "USERPWD" not in params:
        params += ",USERPWD=deepin"

    if "BUILD" not in params:
        params += ",BUILD=%s" % util.getLatestBuildDate()

    # this shuld be placed after BUILD init
    if "ISO" not in params:
        build = ""
        bStrs = [p for p in params.split(",") if p.strip().startswith("BUILD")]
        if len(bStrs) > 0:
            build = bStrs[0].split("=")[1]

        if build == "":
            params += ",ISO=deepin-desktop-amd64.iso"
        else:
            params += ",ISO=deepin-desktop-amd64_%s.iso" % ( build )

    params = params.strip()

    return params


#!/usr/bin/env python3
# encoding: utf-8

import util

def initParams(distri="deepin", rawParams=""):

    params = rawParams.strip()

    """
    if "DISTRI" in params:
        print("You don't need set the DIRSTRI in params, please remove it and try again.")
        return None

    if len(params) > 0:
        params += ",DISTRI=%s" % distri
    else:
        params += "DISTRI=%s" % distri
    """

    if len(params) > 0:
        if "DISTRI" not in params:
            params += ",DISTRI=%s" % distri
    else:
        if "DISTRI" not in params:
            params += "DISTRI=%s" % distri

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

        flavor = getParam(params, "FLAVOR")
        rawArch = getParam(params, "ARCH")

        if rawArch == "x86_64":
            arch = "amd64"
        elif rawArch == "i386":
            arch = "i386"
        else:
            arch = "amd64"

        params += ",BUILD=%s" % util.getLatestBuildDate(flavor, arch)

    # this shuld be placed after BUILD init
    if "ISO" not in params:
        t = "desktop"
        if getParam(params, "FLAVOR") == "SID-DVD":
            t = "sid"

        build = getParam(params, "BUILD")

        #bStrs = [p for p in params.split(",") if p.strip().startswith("BUILD")]
        #if len(bStrs) > 0:
        #    build = bStrs[0].split("=")[1]

        if build == "":
            params += ",ISO=deepin-%s-amd64.iso" %t
        else:
            params += ",ISO=deepin-%s-amd64_%s.iso" % ( t, build )

    params = params.strip()

    return params

def getParam(params, key):
    if params == "" or "," not in params or "=" not in params:
        return ""
    paramsDict = dict([p.strip().split("=") for p in params.split(",")])
    return paramsDict.get(key)


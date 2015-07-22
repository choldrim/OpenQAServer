#!/usr/bin/env python3
# encoding: utf-8

import util
import configparser

defaultParamsConfPath = "/etc/openqa/deepin.ini"

def initParams(distri="deepin", rawParams=""):

    params = rawParams.strip()

    if len(params) > 0:
        if "DISTRI" not in params:
            params += ",DISTRI=%s" % distri
    else:
        if "DISTRI" not in params:
            params += "DISTRI=%s" % distri

    if "FLAVOR" not in params:
        flavor = getDefaultParam("FLAVOR")
        if flavor:
            params += ",FLAVOR=%s" % flavor
        else:
            params += ",FLAVOR=SID-DVD"

    if "ARCH" not in params:
        arch = getDefaultParam("ARCH")
        if arch:
            params += ",ARCH=%s" % arch
        else:
            params += ",ARCH=x86_64"

    if "VERSION" not in params:
        version = getDefaultParam("VERSION")
        if version:
            params += ",VERSION=%s" % version
        else:
            params += ",VERSION=2015"

    if "USERNAME" not in params:
        username = getDefaultParam("USERNAME")
        if username:
            params += ",USERNAME=%s" % username
        else:
            params += ",USERNAME=deepin"

    if "USERPWD" not in params:
        userpwd = getDefaultParam("USERPWD")
        if userpwd:
            params += ",USERPWD=%s" % userpwd
        else:
            params += ",USERPWD=deepin"

    if "HDDSIZEGB" not in params:
        size = getDefaultParam("HDDSIZEGB")
        if size:
            params += ",HDDSIZEGB=%s" % size
        else:
            params += ",HDDSIZEGB=10"

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
        t = "sid"
        #if getParam(params, "FLAVOR") == "SID-DVD" or getParam(params, "FLAVOR") == "SID-PXE":
        if getParam(params, "FLAVOR") == "DVD":
            t = "desktop"

        build = getParam(params, "BUILD")

        if build == "":
            params += ",ISO=deepin-%s-amd64.iso" %t
        else:
            params += ",ISO=deepin-%s-amd64_%s.iso" % ( t, build )

    paramDict = getExtensionParams()
    for (k, v) in paramDict.items():
        k = k.upper()
        if k not in params:
            params += ",%s=%s" %(k, v)

    params = params.strip()
    return params


def getDefaultParam(key):

    defaultParamsConfig = configparser.ConfigParser()
    defaultParamsConfig.read(defaultParamsConfPath)

    if key in defaultParamsConfig["DEFAULT"]:
        return defaultParamsConfig["DEFAULT"][key]

    return ""


def getExtensionParams():

    params = {}

    config = configparser.ConfigParser()
    config.read(defaultParamsConfPath)

    section = "EXTENSION"
    if not config.has_section(section):
        return params
    items = config.items(section)
    for (k, v) in items:
        params[k] = v

    return params

def getParam(params, key):
    if params == "" or "," not in params or "=" not in params:
        return ""
    paramsDict = dict([p.strip().split("=") for p in params.split(",")])
    return paramsDict.get(key)


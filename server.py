#!/usr/bin/env python3
# encoding: utf-8

import logging
import subprocess
import time

from datetime import datetime

from bottle import route, run, template

import common
import fetchISO
import util

LOG_FILE = "server.log"
logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE, format="%(asctime)s - %(levelname)s - %(message)s")

@route("/hello")
@route('/hello/<t:int>')
def hello(t=0):
    time.sleep(t)
    return "Hello ( after %d second(s) )\n" %t


@route('/CL/<changeNum>')
@route('/CL/<changeNum>/')
@route('/CL/<changeNum>/<params:path>')
def ckeckCl(changeNum, params=""):

    tmpMsg = "One CL (%s) with params: \"%s\" was submitted, check it now." % (changeNum, params)
    print (tmpMsg)
    logging.debug(tmpMsg)

    params = common.initParams(changeNum, params)
    print ("after initing the params: ", params)
    readyISO(params)

    ret = 0

    try:
        cmds = []
        cmds.append("python3")
        cmds.append("clientForCL.py")
        cmds.append(changeNum)
        if len(params) > 0:
            cmds.append(params)
        result = subprocess.check_output(cmds)
    except subprocess.CalledProcessError as e:
        result = e.output
        ret = e.returncode

    result = result.decode("utf-8")

    logging.debug("%s\n%s" % (ret, result))

    return "%s\n%s" % (ret, result)

@route("/AutoMonitor")
@route("/AutoMonitor/")
@route("/AutoMonitor/<params:path>")
def autoMonitor(params = ""):
    print ()
    print ("======= %s =======" % str(datetime.now()))
    print ("One job is going to be scheduled with params: \"%s\"." % params)
    logging.debug("One job is going to be scheduled with params: \"%s\"." % params)

    params = common.initParams("deepin", params)
    print ("suply the params: ", params)
    readyISO(params)

    try:
        cmds = []
        cmds.append("python3")
        cmds.append("clientForAutoMonitor.py")
        if len(params) > 0:
            cmds.append(params)
        ret = 0
        result = subprocess.check_output(cmds)
    except subprocess.CalledProcessError as e:
        result = e.output
        ret = e.returncode

    result = result.decode("utf-8")

    print ("return code: ", ret);
    print ("result:")
    print (result)

    return result

def readyISO(params):

    arch = ""
    build = ""

    # arch
    rawArch = common.getParam(params, "ARCH")
    if rawArch == "x86_64":
        arch = "amd64"
    elif rawArch == "i386":
        arch = "i386"
    else:
        arch = "amd64"

    # build
    build = common.getParam(params, "BUILD")

    # flavor
    flavor = common.getParam(params, "FLAVOR")

    fetchISO.downloadISO(arch, build, flavor)


#run(host="0.0.0.0", port=8080)
run(server="cherrypy", host="0.0.0.0", port=8080)


#!/usr/bin/env python3
# encoding: utf-8

import subprocess
import time

from bottle import route, run, template

import fetchISO
import util

@route("/hello")
@route('/hello/<t:int>')
def hello(t=0):
    time.sleep(t)
    return "Hello ( after %d second(s) )\n" %t


@route('/CL/<changeNum>')
@route('/CL/<changeNum>/')
@route('/CL/<changeNum>/<params:path>')
def ckeckCl(changeNum, params=""):

    print ("One CL was submitted, check it now.")
    print ("change num:", changeNum, "---", "params: ", params)

    #return template("{{ret}}<p>{{tips}}, see <a href={{jobUrl}}>{{jobUrl}}</a>", ret = ret, tips=tips, jobUrl=jobUrl)

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

    print ("%s\n%s" % (ret, result))

    return "%s\n%s" % (ret, result)

@route("/AutoMonitor")
@route("/AutoMonitor/")
@route("/AutoMonitor/<params:path>")
def autoMonitor(params = ""):
    print ()
    print ("One job is going to be scheduled.")
    print ("Params: ", params)

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
    # default
    arch = "amd64"
    build = ""
    paramList = [p.strip() for p in params.split(",")]
    for p in paramList:
        if p.startswith("ARCH"):
            rawArch = p.split("=")[1]
            if rawArch == "x86_64":
                arch = "amd64"
            else:
                arch = "i386"
        if p.startswith("BUILD"):
            build = p.split("=")[1]
    if build == "":
        build = util.getLatestBuildDate()
    fetchISO.downloadISO(arch, build)


#run(host="0.0.0.0", port=8080)
run(server="cherrypy", host="0.0.0.0", port=8080)


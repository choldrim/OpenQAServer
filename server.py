#!/usr/bin/env python3
# encoding: utf-8

#
import subprocess
import time

#
from bottle import route, run, template


@route("/hello")
@route('/hello/<t:int>')
def hello(t=0):
    time.sleep(t)
    return "Hello ( after %d second(s) )\n" %t


@route('/CL/<changeNum>')
@route('/CL/<changeNum>/')
@route('/CL/<changeNum>/<params:path>')
def ckeckCl(changeNum, params=""):

    print ("change num:", changeNum, "---", "params: ", params)

    #(ret, tips, jobUrl) = client.run(changeNum, params)

    #return template("{{ret}}<p>{{tips}}, see <a href={{jobUrl}}>{{jobUrl}}</a>", ret = ret, tips=tips, jobUrl=jobUrl)

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

@route("/AutoMonitor/<params:path>")
def autoMonitor(params = ""):
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

    printBack = "%s\n%s\n" % (ret, result);
    print (printBack)

    return printBack

#run(host="0.0.0.0", port=8080)
run(server="cherrypy", host="0.0.0.0", port=8080)


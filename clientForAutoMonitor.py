#!/usr/bin/env python3
# coding=utf-8

import json
import os
import subprocess
import sys

import common

clientPath = "/usr/share/openqa/script/client"
host = "https://openqa.deepin.io"
#host = "http://localhost"
distriDir = "/var/lib/openqa/share/tests/deepin"

def resultToJsonStr(result):

    result = result.decode("utf-8")

    if"{" not in result or "}" not in result:  # at least "{}"
        return

    jsonStr = result.replace(r'\"', '"')[1:-2]

    return jsonStr

def syncWorkspace():
    os.chdir(distriDir)
    gitCmd = "git pull origin master:master"
    print (gitCmd)
    ret = os.system(gitCmd)

    return ret

def scheduledJobs(params):

    jobIds = []

    cmds = []
    cmds.append(clientPath)
    cmds.append("--host")
    cmds.append(host)
    cmds.append("--rawjson")
    cmds.append("isos")
    cmds.append("post")
    cmds += [ p.strip() for p in params.split(",") if len(p.strip()) > 0]

    try:
        result = subprocess.check_output(cmds, env={"OPENQA_CONFIG":"/etc/openqa"})
    except subprocess.CalledProcessError as e:
        print ("Error: ")
        print (e)
        print ("output: ", e.output)
        return jobIds

    jsonStr = resultToJsonStr(result)

    if (jsonStr != None):
        jsonData = json.loads(jsonStr)
        jobIds = jsonData.get("ids")

    else:
        print("Get a null json from server when scheduled jobs, abort.")

    return jobIds

def run(rawParams):

    syncRet = syncWorkspace()
    if syncRet != 0:
        print ("Sync(git pull) distri workspace fail, abort.")

    else:
        distriName = "deepin"
        params = common.initParams(distriName, rawParams)

        jobIds = scheduledJobs(params)

        print("Scheduled %d job: %s" %(len(jobIds), "  ".join([str(i) for i in jobIds])))

if __name__ == "__main__":

    rawParams = ""

    if len(sys.argv) == 2:
        rawParams = sys.argv[1]

    if len(sys.argv) > 2:
        rawParams = ",".join(sys.argv[2:])

    run(rawParams)

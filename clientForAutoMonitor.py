#!/usr/bin/env python3
# coding=utf-8

import json
import pprint
import os
import subprocess
import shutil
import tarfile
import time
import sys

from urllib import request

import common
import util

clientPath = "/usr/share/openqa/script/client"
host = "https://openqa.deepin.io"

def resultToJsonStr(result):

    result = result.decode("utf-8")

    if"{" not in result or "}" not in result:  # at least "{}"
        return

    jsonStr = result.replace(r'\"', '"')[1:-2]

    return jsonStr

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
    distriName = "deepin"
    params = common.initParams(distriName, rawParams)
    if params == None:
        return 1

    jobIds = scheduledJobs(params)

    print("Scheduled %d job: %s" %(len(jobIds), "  ".join(jobIds)))

if __name__ == "__main__":

    rawParams = ""

    if len(sys.argv) == 2:
        rawParams = sys.argv[1]

    if len(sys.argv) > 2:
        rawParams = ",".join(sys.argv[2:])

    run(rawParams)

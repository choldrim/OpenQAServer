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


clientPath = "/usr/share/openqa/script/client"
host = "https://openqa.deepin.io"
distriDir = "/var/lib/openqa/share/tests"
workingDir = os.path.join(os.getenv("HOME"), "Deepin-OpenQA-Commit-Test")

debug = False

def loadTemplates(templatesFile):
    cmds = []
    cmds.append("/usr/share/openqa/script/load_templates")
    cmds.append("--host")
    cmds.append(host)
    cmds.append(templatesFile)

    try:
        print("Loading templates...")
        result = subprocess.check_output(cmds)
        result = result.decode("utf-8")
        print ("Load_templates result: \n", result, "\n")
    except subprocess.CalledProcessError as e:
        print (e)
        print ("output: ", e.output)


def genTemplates(rawParams):

    print ("Generate template...")

    params = dict([tuple(kv.split("=")) for kv in rawParams.split(",")])

    arch = params["ARCH"]
    distri = params["DISTRI"]
    flavor = params["FLAVOR"]
    version = params["VERSION"]

    # JobTemplates
    JobTemplates = []
    if "ARCH=x86_64" in rawParams:
        machine = {"name" : "64bit"}
    else:
        machine = {"name" : "32bit"}
    product = {
            "arch" : arch,
            "distri" : distri,
            "flavor" : flavor,
            "version" : version
            }
    test_suite = {"name" : "deepin_installation"}
    JobTemplates.append({
        "machine":machine,
        "product":product,
        "test_suite":test_suite})

    # Machines
    # ...

    # Products
    Products = []
    settings = []
    # settings.append({"key":"VNC","value":""})
    # settings.append({"key":"USERNAME","value":"deepin"})
    # settings.append({"key":"USERPWD","value":"deepin"})
    Products.append({
            "arch" : arch,
            "distri" : distri,
            "flavor" : flavor,
            "version" : version,
            "settings" : settings
            })

    # combine templates
    templates = {"JobTemplates":JobTemplates, "Products":Products}

    templatesStr = str(templates).replace(":", "=>")

    templatesFile = "templates"
    with open(templatesFile, "w") as f:
        f.write(templatesStr)

    if debug:
        pprint.pprint (templates)
        print ()

    return templatesFile

def resultToJsonStr(result):

    result = result.decode("utf-8")

    if"{" not in result or "}" not in result:  # at least "{}"
        return

    jsonStr = result.replace(r'\"', '"')[1:-2]

    return jsonStr

def scheduledJobs(params):
    cmds = []
    cmds.append(clientPath)
    cmds.append("--host")
    cmds.append(host)
    cmds.append("--rawjson")
    cmds.append("isos")
    cmds.append("post")
    cmds += [ p.strip() for p in params.split(",") if len(p.strip()) > 0]

    # execute
    try:
        if debug:
            print ("scheduled job...")
            print (" cmd: ", " ".join(cmds))
        result = subprocess.check_output(cmds, env={"OPENQA_CONFIG":"/etc/openqa"})
    except subprocess.CalledProcessError as e:
        print ("Error:", e)
        print ("Output:", e.output)
        raise e

    #print ("scheduled job, result: \n", result)

    jsonStr = resultToJsonStr(result)

    if (jsonStr == None):
        print("Get a null result from server when scheduled jobs, abort.")
        return

    jsonData = json.loads(jsonStr)
    jobIds = jsonData.get("ids")

    if len(jobIds) == 0:
        print("No job has been created, please check your params for Startup")
        return

    print("Scheduled Result:", jsonStr)

    return jobIds

def waitForEnd(jobIds):

    """ for multi jobs
    jobsState = {}
    jobsResult = {}

    cmds = []
    cmds.append(clientPath)
    cmds.append("--host")
    cmds.append(host)

    cmds.append("jobs")
    result = subprocess.check_output(cmds)
    result = result.decode("utf-8")
    if '\"jobs\"' not in result:
        print("json data error.")
        return None
    result = result.replace(r'\"', '"')[1:-2]
    jsonData = json.loads(result)
    jobs = jsonData.get("jobs")
    for job in jobs:
        if job.get("id") in jobIds:
            jobsState[job.get("id")] = job.get("state")
            jobsResult[job.get("id")] = job.get("result")

    for jobId in jobIds:
        print ("jobs state: ")
        print ("job id: %d, state: %s , result: %s" %(
            jobId, jobsState[jobId], jobsResult[jobId]))
        # state: scheduled, running, cancelled, waiting, done
        if jobsState[jobId] == "done":
            # handle

            # result: none, passed, failed, incomplete
            if jobsResult[jobId] == "passed":
                pass

    time.sleep(2)
    """

    # just for one job
    if len(jobIds) > 1:
        print("scheduled %d jobs, it shuld be one job in normal, please check your params, abort." % len(jobIds))
    jobId = jobIds[0]
    cmds = []
    cmds.append(clientPath)
    cmds.append("--host")
    cmds.append(host)
    cmds.append("jobs/%s" %jobId)
    cmds.append("--rawjson")

    while(True):
        try:
            result = subprocess.check_output(cmds)
        except subprocess.CalledProcessError as e:
            # log it
            print (e)
            raise e

        jsonStr = resultToJsonStr(result)
        if jsonStr == None:
            print ("Get unexpect result when check job state, result: \n %s" % result)
            return None

        jsonData = json.loads(jsonStr)
        jobData = jsonData.get("job")
        jobState = jobData.get("state")
        jobResult = jobData.get("result")


        if debug:
            print ("\n---------------------------------------------")
            print ("job (%d) state: %s" % (jobId, jobState))
            print ()
            pprint.pprint(jsonData)
            print ("---------------------------------------------")

        if jobState == "done":
            if jobResult == "passed":
                return 0
            if jobResult == "failed":
                return 1
            if jobResult == "user_cancelled":
                return 2
            if jobResult == "incomplete":
                return 3

            break

        time.sleep(2)

def initParams(testDir, rawParams):
    #rawKVPair = [tuple(kv.strip().split("=")) for kv in rawParam.split(",")]
    #params = dict(rawKVPair)

    params = rawParams.strip()

    if "DISTRI" in params:
        print("You don't need set the DIRSTRI in params, please remove it and try again.")
        return None

    if len(params) > 0:
        params += ",DISTRI=%s" % testDir
    else:
        params += "DISTRI=%s" % testDir

    if "ISO" not in params:
        params += ",ISO=deepin-desktop-amd64.iso"

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

    params = params.strip()

    return params


def initWorkspace(reviewId):
    # ready testcase dir
    dirName = "%s" % (reviewId)
    dirPath = os.path.join(workingDir, dirName)
    linkName = os.path.join(distriDir, dirName)

    if os.path.exists(linkName):
        #print ("link exists, remove:", linkName)
        os.remove(linkName)

    if os.path.exists(dirPath):
        #print ("target exists, remove: %s" % dirPath)
        shutil.rmtree(dirPath)

    os.makedirs(dirPath)

    # link
    linkCmds = ["ln", "-s", dirPath, linkName]
    try:
        subprocess.check_call(linkCmds)
    except subprocess.CalledProcessError as e:
        # log it
        print (e)
        raise e

    # get revision id
    clId = reviewId
    res = request.urlopen("https://cr.deepin.io/changes/%s/?o=CURRENT_REVISION" % clId)
    data = res.read()
    data = data.decode("utf-8").split("\n", 1)[1]
    jsonData = json.loads(data)
    revisionId = jsonData.get("current_revision")

    # get source code
    sourceUrl = "https://cr.deepin.io/changes/%s/revisions/%s/archive?format=tar" % (clId, revisionId)
    res = request.urlopen(sourceUrl)
    print ("Downloading CL %s source code ..." % clId)
    print (sourceUrl)
    data = res.read()
    print ("Finish download")
    tarFilePath = "/tmp/%s.tar" % (reviewId)
    with open(tarFilePath, "wb") as f:
        f.write(data)

    # extract source code
    tarf = tarfile.open(tarFilePath)
    tarf.extractall(dirPath)
    tarf.close()

    # delete tar file
    os.remove(tarFilePath)

    return dirName

def run(reviewId, rawParams):

    distriName = initWorkspace(reviewId)
    params = initParams(distriName, rawParams)
    if params == None:
        return 1

    print ("Params: ", params)

    tempPath = genTemplates(params)
    loadTemplates(tempPath)

    ids = scheduledJobs(params)
    if ids == None:
        return 1, "", ""

    ret = waitForEnd(ids)

    jobUrl = "%s/tests/%d" % (host, ids[0])
    tips = "Job has been %s"

    if ret == 0:
        tips = tips % ("completed")
    elif ret == 1:
        tips = tips % ("failed")
    elif ret == 2:
        tips = tips % ("cancelled")
    elif ret == 3:
        tips = tips % ("failed with incomplete state")

    #print (tips)

    #html = "%s, see: <a href=%s>%s</a>" % (tips, jobUrl, jobUrl)

    return ret, tips, jobUrl

if __name__ == "__main__":
    # tmp
    #reviewId = "3467"
    #rawParams = "ISO=deepin-desktop-amd64.iso VERSION=2014.2 ARCH=x86_64"
    if len(sys.argv) < 2:
        print ("CLId must be set")
        quit (1)

    reviewId = sys.argv[1]
    rawParams = ",".join(sys.argv[2:])

    ret = 0
    ret, tips, jobUrl = run(reviewId, rawParams)

    output = "%s, see: %s" % (tips, jobUrl)
    print (output)

    print (ret)

    quit (ret)

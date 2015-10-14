#!/usr/bin/env python3
# coding=utf-8

import json
import logging
import pprint
import subprocess
import shutil
import tarfile
import time
import sys
import os

from urllib import request

import common

clientPath = "/usr/share/openqa/script/client"
showHost = "http://10.0.4.250"
host = "openqa-webui:9526"
distriDir = "/var/lib/openqa/share/tests"

LOG_FILE = "check_cl.log"
logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE, format="%(asctime)s - %(levelname)s - %(message)s")

debug = False

def loadTemplates(templatesFile):
    cmds = []
    cmds.append("/usr/share/openqa/script/load_templates")
    cmds.append("--host")
    cmds.append(host)
    cmds.append(templatesFile)

    try:
        #print("Loading templates...")
        logging.debug("Loading templates...")
        result = subprocess.check_output(cmds)
        result = result.decode("utf-8")
        #print ("Load_templates result: \n", result, "\n")
        logging.debug("Load_templates result: \n%s\n" %result)
    except subprocess.CalledProcessError as e:
        logging.error(e)


def genTemplates(rawParams):

    #print ("Generate template...")
    logging.debug("Generate template...")

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
    test_suite = {"name" : "deepin_cl"}
    group_name = "deepin-desktop"
    prio = 50
    JobTemplates.append({
        "machine":machine,
        "product":product,
        "test_suite":test_suite,
        "group_name":group_name,
        "prio":prio,
    })

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
        #print ("scheduled job with cmd:\n ", " ".join(cmds))
        logging.debug("scheduled job with cmd:\n %s" % " ".join(cmds))
        result = subprocess.check_output(cmds, env={"OPENQA_CONFIG":"/etc/openqa"})
    except subprocess.CalledProcessError as e:
        #print ("Error:", e)
        #print ("Output:", e.output)
        logging.error(e)
        #raise e

    #print ("scheduled job, result: \n", result)

    jsonStr = resultToJsonStr(result)

    if (jsonStr == None):
        #print("Get a null result from server when scheduled jobs, abort.")
        logging.error("Get a null result from server when scheduled jobs, abort.")
        return

    jsonData = json.loads(jsonStr)
    jobIds = jsonData.get("ids")

    if len(jobIds) == 0:
        #print("No job has been created, please check your params for Startup")
        logging.warn("No job has been created, please check your params for Startup")
        return

    print("Scheduled Result:", jsonStr)
    logging.debug("Scheduled Result: %s" % jsonData)

    return jobIds

def waitForEnd(jobIds):

    # just for one job
    if len(jobIds) > 1:
        logging.debug("scheduled %d jobs, it shuld be one job in normal, please check your params, abort." % len(jobIds))
        return -1
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
            logging.error(e)
            return -1

        jsonStr = resultToJsonStr(result)
        if jsonStr == None:
            logging.error("Get unexpect result when check job state, result: \n %s" % result)
            return -1

        jsonData = json.loads(jsonStr)
        jobData = jsonData.get("job")
        jobState = jobData.get("state")
        jobResult = jobData.get("result")


        waitingDebug = False
        if waitingDebug:
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


def initWorkspace(reviewId):
    # ready testcase dir
    dirName = "%s" % (reviewId)
    distriPath = os.path.join(distriDir, dirName)

    if os.path.exists(distriPath):
        shutil.rmtree(distriPath)

    os.makedirs(distriPath)

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
    logging.debug("Downloading CL %s source code, from url: %s" % (clId, sourceUrl))
    data = res.read()
    logging.debug("Finish download")
    tarFilePath = "/tmp/%s.tar" % (reviewId)
    with open(tarFilePath, "wb") as f:
        f.write(data)

    # extract source code
    tarf = tarfile.open(tarFilePath)
    tarf.extractall(distriPath)
    tarf.close()

    # delete tar file
    os.remove(tarFilePath)

    return dirName

def run(reviewId, params):

    distriName = initWorkspace(reviewId)

    tempPath = genTemplates(params)
    loadTemplates(tempPath)

    ids = scheduledJobs(params)
    if ids == None:
        return 1, "", ""

    ret = waitForEnd(ids)

    jobUrl = "%s/tests/%d" % (showHost, ids[0])
    tips = "Job has been %s"

    if ret == 0:
        tips = tips % ("completed")
    elif ret == 1:
        tips = tips % ("failed")
    elif ret == 2:
        tips = tips % ("cancelled")
    elif ret == 3:
        tips = tips % ("failed with incomplete state")
    else:
        tips = tips % ("other error, please check OpenQAServer log")

    #print (tips)

    #html = "%s, see: <a href=%s>%s</a>" % (tips, jobUrl, jobUrl)

    return ret, tips, jobUrl

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print ("CLId must be set")
        quit (1)

    reviewId = sys.argv[1]
    params = ",".join(sys.argv[2:])

    ret = 0
    ret, tips, jobUrl = run(reviewId, params)

    output = "%s, see: %s" % (tips, jobUrl)

    logging.debug(output)

    print (output)

    #print (ret)

    quit (ret)

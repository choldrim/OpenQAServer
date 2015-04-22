#!/usr/bin/env python3
# encoding: utf-8

import re
from urllib import request
from urllib.error import URLError

def getLatestBuildDate(flavor="DVD"):

    dailyLiveUrl = "http://cdimage/daily-live-next/desktop/"
    if flavor == "SID-DVD":
        dailyLiveUrl = "http://cdimage/daily-live-sid/"
    try:
        resp = request.urlopen(dailyLiveUrl)
        data = resp.read().decode("utf-8")
    except URLError as e:
        print (e)
        return "20150420"
        #raise e

    a = re.compile(">(\d+)/<")

    allDaily = a.findall(data)
    d = allDaily[-1:][0].strip()

    return d

import sys
if __name__ == "__main__":
    flavor = "DVD"
    if len(sys.argv) > 1:
        flavor = sys.argv[1]
    print (getLatestBuildDate(flavor))

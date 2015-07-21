#!/usr/bin/env python3
# encoding: utf-8

import re
from urllib import request
from urllib.error import URLError

def getLatestBuildDate(flavor="DVD", arch="amd64"):

    d = "20150420"

    t = "desktop"

    dailyLiveUrl = "http://cdimage/daily-live-next/desktop/"
    if flavor == "SID-DVD" or flavor == "SID-PXE":
        t = "sid"
        dailyLiveUrl = "http://cdimage/daily-live-sid/"
    try:
        resp = request.urlopen(dailyLiveUrl)
        data = resp.read().decode("utf-8")
    except URLError as e:
        print (e)

        # return an exist building date
        return d

    a = re.compile(">(\d+)/<")

    # get an available url
    allDaily = a.findall(data)
    allDaily.reverse()
    for i in allDaily:
        try:
            url = "%s%s/deepin-%s-%s.iso" % (dailyLiveUrl, i, t, arch)
            request.urlopen(url)
            d = i
            break
        except URLError as e:
            continue

    #d = allDaily[-1:][0].strip()

    return d

import sys
if __name__ == "__main__":
    flavor = "DVD"
    if len(sys.argv) > 1:
        flavor = sys.argv[1]
    print (getLatestBuildDate(flavor))

#!/usr/bin/env python3
# encoding: utf-8

import re
from urllib import request

def getLatestBuildDate():

    dailyLiveUrl = "http://cdimage/daily-live/desktop/"
    with request.urlopen(dailyLiveUrl) as resp:
        data = resp.read().decode("utf-8")

    a = re.compile(">(\d+)/<")

    allDaily = a.findall(data)
    d = allDaily[-1:][0].strip()

    return d

if __name__ == "__main__":
    print (getLatestBuildDate())

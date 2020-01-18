# Copied to Evernote:
# https://github.com/magicmonty/hltvdownloader
# Checked out on nas:
# https://github.com/renne/HLTVDLM

import urllib
import requests
import re
import wget as wget
import base64
import time
import os
import hashlib

outputpath = "/tmp/"
username = "volker@kettenbach.biz"
password = "4j9EJSAG"

APIuriPrefix = 'https://www.homeloadtv.com/api/'
limit = 100


def setstate(state, id = 0, listid = 0, filesize = 0, speed = 0.0, error = "", filename = ""):
    parameter = None
    if state == "processing":
        parameter = {
            'do': 'setstate',
            'state': state,
            'list': listid,
            'uid': username,
            'password': password
        }
    if state == "damaged":
        parameter = {
            'do': 'setstate',
            'state': state,
            'id': id,
            'uid': username,
            'password': password
        }
    if state == "finished":
        parameter = {
            'do': 'setstate',
            'state': state,
            'id': id,
            'uid': username,
            'password': password,
            'error': error,
            'filesize': filesize,
            'speed': speed,
            'file': base64.b64encode(filename)
        }
    return requests.get(APIuriPrefix, params=parameter)


params = {
    'do': 'getlinks',
    'uid': username,
    'password': password,
    'limit': limit,
    'protocnew': True,
    'onlyhh': False
}

response = requests.get(APIuriPrefix, params=params)

if response.status_code != 200:
    print("Error on getting data: " + response.status_code + " " + response.content)
else:
    i = 0
    for line in response.iter_lines():
        line = line.decode('utf-8')
        if i == 0:
            linkcount = 0
            try:
                m = re.search("INTERVAL=(.*);NUMBER_OF_LINKS=(.*);LIST=(.*);LINKCOUNT=(.*);HHSTART=(.*);HHEND=(.*);",
                              line)
                interval = int(m.group(1))
                number_of_lins = int(m.group(2))
                listid = int(m.group(3))
                linkcount = int(int(m.group(4)))
                hhstart = int(m.group(5))
                hhend = int(m.group(6))
            except Exception as e:
                print("Error parsing data: " + str(e))

            if linkcount > 0:
                print("Found " + str(linkcount) + " new links.")
        else:
            url = None
            id = 0
            try:
                m = re.search("(.*);(.*);", line)
                url = m.group(1)
                id = int(m.group(2))
            except Exception as e:
                print("Error parsing data: " + str(e))
            if url is not None:
                print("Downloading " + url)
                try:
                    start = time.time()
                    res = setstate("processing", listid=listid)
                    time.sleep(15)
                    filename = wget.download(url, out=outputpath)
                    end = time.time()
                    timeused = end - start
                    statinfo = os.stat(filename)
                    filesize = statinfo.st_size
                    speed = filesize / (timeused * 1024)
                    res = setstate("finished", id = id, filesize=round(filesize/1024), speed=speed, filename=filename)
                    print(res.status_code)
                except urllib.error.HTTPError as e:
                    print("\tError downloading link " + str(id) + ": " + str(e))
                    res = setstate("damaged", id = id)
                    if res.status_code == 200:
                        print("\tSet download link to damaged!!")
                    else:
                        print("\tError updating status of download link.")
        i = i + 1

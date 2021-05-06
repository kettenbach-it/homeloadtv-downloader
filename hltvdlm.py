# pylint: disable=line-too-long,redefined-builtin,redefined-outer-name,invalid-name
"""
Downloader for Homeload-TV (https://www.homeloadtv.com/)

Based on ides from:
    https://github.com/magicmonty/hltvdownloader
    https://github.com/renne/HLTVDLM

"""

import configparser
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

config = configparser.ConfigParser()

if os.path.exists("hltvdlm.conf"):
    config.read("hltvdlm.conf")

elif os.path.exists(str(Path.home()) + "/.hltvdlm.conf"):
    config.read(str(Path.home()) + "/.hltvdlm.conf")
else:
    print("No config file found.")

outputpath = config['DEFAULT']['outputpath']
username = config['DEFAULT']['username']
password = config['DEFAULT']['password']

API_URI_PREFIX = 'https://www.homeloadtv.com/api/'
LIMIT = 100
headers = {
    'User-Agent': 'HLTVDLM 1.0 https://github.com/renneb/HLTVDLM'
}


def setstate(state, id=0, listid=0, filesize=0, speed=0.0, error="", filename=""):  # pylint: disable=too-many-arguments
    """
    Set's state of download
    :param state:
    :param id:
    :param listid:
    :param filesize:
    :param speed:
    :param error:
    :param filename:
    :return:
    """
    parameter = None
    if state == "processing":
        parameter = {
            'do': 'setstate',
            'state': state,
            'list': listid,
            'uid': username,
            'password': password
        }
    elif state == "damaged":
        parameter = {
            'do': 'setstate',
            'state': state,
            'id': id,
            'uid': username,
            'password': password
        }
    elif state == "finished":
        parameter = {
            'do': 'setstate',
            'state': state,
            'id': id,
            'uid': username,
            'password': password,
            'error': error,
            'filesize': filesize,
            'speed': speed,
            'file': filename
        }
    else:
        return None
    return requests.get(API_URI_PREFIX, params=parameter, headers=headers)


response = requests.get(API_URI_PREFIX, headers=headers, params={
    'do': 'getlinks',
    'uid': username,
    'password': password,
    'limit': LIMIT,
    'protocnew': False,
    'onlyhh': False
})

if response.status_code != 200:
    print("Error on getting data: " + str(response.status_code) + " " + response.text)
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
                number_of_links = int(m.group(2))
                listid = int(m.group(3))
                linkcount = int(int(m.group(4)))
                hhstart = int(m.group(5))
                hhend = int(m.group(6))
            except Exception as e:  # pylint: disable=broad-except
                print("Error parsing data: " + str(e) + ". " + line)

            if linkcount > 0:
                print("Found " + str(linkcount) + " new links.")
        else:
            linkurl = None
            linkid = 0
            try:
                m = re.search("(.*);(.*);", line)
                linkurl = m.group(1)
                linkid = int(m.group(2))
            except Exception as e:  # pylint: disable=broad-except
                print("Error parsing url: " + str(e))
            if linkurl is not None:
                print("Downloading " + linkurl)
                try:
                    res = setstate("processing", listid=listid)
                    start = time.time()

                    filename = os.path.basename(urlparse(linkurl).path)
                    with requests.get(linkurl, stream=True) as r:
                        # Throw an error for bad status codes
                        r.raise_for_status()
                        with open(outputpath + filename, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:  # filter out keep-alive new chunks
                                    f.write(chunk)

                    end = time.time()
                    timeused = round(end - start, 1)
                    filesize = os.stat(outputpath + filename).st_size
                    speed = round(filesize / (timeused), 1)
                    res = setstate("finished", id=linkid, filesize=round(filesize / 1024),
                                   speed=round((speed*8)/1024,0), filename=filename)
                    if res.status_code == 200:
                        print("\tDownload successful! Filesize: " + str(round(filesize / (1024 * 1024), 1))
                              + "MB, Speed: " + str(round(speed/1024, 1)) + " kB/s, Time: " + str(timeused) + "s.")
                    else:
                        print("\tFile was downloaded but its state could not be set!")

                except requests.exceptions.HTTPError as e:
                    print("\tError downloading link " + str(linkid) + ": " + str(e), end=". ")
                    res = setstate("damaged", id=linkid)
                    if res.status_code == 200:
                        print("Download link was set to damaged!!")
                    else:
                        print("Error updating status of download link. Something seems to be terribly wrong.")
        i = i + 1

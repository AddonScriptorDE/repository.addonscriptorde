#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import base64
import xbmc
import xbmcaddon
import urllib
import urllib2
import shutil


def download(videoID, title, year):
    filename = (''.join(c for c in unicode(videoID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    content = opener.open("http://api.themoviedb.org/3/search/"+videoType+"?api_key="+data+"&query="+urllib.quote_plus(title.strip())+"&year="+urllib.quote_plus(year)+"&language=en").read()
    match = re.compile('"poster_path":"(.+?)"', re.DOTALL).findall(content)
    if match:
        coverUrl = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/original"+match[0]
        contentJPG = opener.open(coverUrl).read()
        fh = open(coverFile, 'wb')
        fh.write(contentJPG)
        fh.close()
    match = re.compile('"backdrop_path":"(.+?)"', re.DOTALL).findall(content)
    if match:
        fanartUrl = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/original"+match[0]
        contentJPG = opener.open(fanartUrl).read()
        fh = open(fanartFile, 'wb')
        fh.write(contentJPG)
        fh.close()

addonID = 'plugin.video.netflixbmc'
addon = xbmcaddon.Addon(id=addonID)
data = base64.b64decode("NDc2N2I0YjJiYjk0YjEwNGZhNTUxNWM1ZmY0ZTFmZWM=")
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
cacheFolder = os.path.join(addonUserDataFolder, "cache")
cacheFolderCoversTMDB = os.path.join(cacheFolder, "covers")
cacheFolderFanartTMDB = os.path.join(cacheFolder, "fanart")
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0"
opener.addheaders = [('User-agent', userAgent)]

videoType = urllib.unquote_plus(sys.argv[1])
videoID = urllib.unquote_plus(sys.argv[2])
title = urllib.unquote_plus(sys.argv[3])
year = urllib.unquote_plus(sys.argv[4])

try:
    download(videoID, title, year)
except:
    pass

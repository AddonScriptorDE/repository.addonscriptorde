#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import random
import sqlite3
import xbmcgui
import xbmcaddon
import xbmcplugin


addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
xbox = xbmc.getCondVisibility("System.Platform.xbox")

socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0"
opener.addheaders = [('User-Agent', userAgent)]

playRandom = addon.getSetting("playRandom") == "true"

filterMode = int(addon.getSetting("filterMode"))
filterMode = ["all", "unwatched", "custom"][filterMode]
filterCustom = int(addon.getSetting("filterCustom"))

searchSort = int(addon.getSetting("searchSort"))
searchSort = ["relevance", "viewCount", "rating", "published"][searchSort]
searchTime = int(addon.getSetting("searchTime"))
searchTime = ["all_time", "today", "this_week", "this_month"][searchTime]

addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
historyFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/search.history")
if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)


def getDbPath():
    path = xbmc.translatePath("special://userdata/Database")
    files = os.listdir(path)
    latest = ""
    for file in files:
        if file[:8] == 'MyVideos' and file[-3:] == '.db':
            if file > latest:
                latest = file
    return os.path.join(path, latest)


def getPlayCount(url):
    c.execute('SELECT playCount FROM files WHERE strFilename=?', [url])
    result = c.fetchone()
    if result:
        result = result[0]
        if result:
            return int(result)
        return 0
    return -1


def newSearch():
    keyboard = xbmc.Keyboard('', translation(30016))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        query = keyboard.getText().replace(" ", "+")
        alreadyIn = False
        if os.path.exists(historyFile):
            fh = open(historyFile, 'r')
            content = fh.readlines()
            fh.close()
            for line in content:
                if line.lower()==query.lower()+"\n":
                    alreadyIn = True
        if not alreadyIn:
            fh = open(historyFile, 'a')
            fh.write(query+'\n')
            fh.close()
        autoPlay(query)


def removeSearch(query):
    fh = open(historyFile, 'r')
    content = fh.readlines()
    fh.close()
    contentNew = ""
    for line in content:
        if line!=query+'\n':
            contentNew+=line
    fh = open(historyFile, 'w')
    fh.write(contentNew)
    fh.close()
    xbmc.executebuiltin("Container.Refresh")


def removeHistory():
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('Info:', translation(30018)+"?")
    if ok==True:
        os.remove(historyFile)
        xbmc.executebuiltin("Container.Refresh")


def index():
    addDir("[B]- "+translation(30016)+"[/B]", "", 'newSearch', "")
    entries = []
    if os.path.exists(historyFile):
        fh = open(historyFile, 'r')
        content = fh.read()
        fh.close()
        spl = content.split('\n')
        for i in range(0, len(spl), 1):
            if spl[i]:
                query = spl[i].strip()
                entries.append(query)
    entries.sort()
    for entry in entries:
        addDirR(entry.replace("+", " ").title(), entry, 'autoPlay', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def autoPlay(query):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+query+"&racy=include&max-results=50&start-index=1&orderby="+searchSort+"&time="+searchTime+"&v=2").read()
    spl=content.split('<entry')
    for i in range(1,len(spl),1):
        try:
            entry=spl[i]
            match=re.compile('<yt:videoid>(.+?)</yt:videoid>', re.DOTALL).findall(entry)
            id=match[0]
            match=re.compile("<media:title type='plain'>(.+?)</media:title>", re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            url = sys.argv[0]+"?url="+urllib.quote_plus(getYoutubeUrl(id))+"&mode=playVideo"
            if filterMode=="all":
                listitem = xbmcgui.ListItem(title)
                entries.append([title, url])
            elif filterMode=="unwatched" and getPlayCount(url) < 0:
                listitem = xbmcgui.ListItem(title)
                entries.append([title, url])
            elif filterMode=="custom" and getPlayCount(url) < filterCustom:
                listitem = xbmcgui.ListItem(title)
                entries.append([title, url])
        except:
            pass
    if playRandom:
        random.shuffle(entries)
    for title, url in entries:
        listitem = xbmcgui.ListItem(title)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def getYoutubeUrl(id):
    if xbox:
        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id
    return url


def playVideo(url):
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def cleanTitle(title):
        title = title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"")
        return title.strip()


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDirR(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems([(translation(30017), 'RunPlugin(plugin://'+addonID+'/?mode=removeSearch&url='+urllib.quote_plus(url)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


dbPath = getDbPath()
conn = sqlite3.connect(dbPath)
c = conn.cursor()

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'playVideo':
    playVideo(url)
elif mode == 'newSearch':
    newSearch()
elif mode == 'removeSearch':
    removeSearch(url)
elif mode == 'removeHistory':
    removeHistory()
elif mode == 'autoPlay':
    autoPlay(url)
else:
    index()

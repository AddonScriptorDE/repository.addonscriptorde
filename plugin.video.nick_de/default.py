#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import random
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.nick_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
jrOnly = addon.getSetting("jrOnly") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
iconJr = xbmc.translatePath('special://home/addons/'+addonID+'/iconJr.png')
urlMain = "http://www.nick.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    if jrOnly:
        nickJrMain()
    else:
        addDir(translation(30001), "", 'nickMain', icon)
        addDir(translation(30002), "", 'nickJrMain', iconJr)
        xbmcplugin.endOfDirectory(pluginhandle)


def nickMain():
    addDir(translation(30003), urlMain+"/videos", 'listEntries', icon)
    addDir(translation(30004), urlMain+"/shows?active_tab=0&ajax", 'listEntries', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def nickJrMain():
    addDir(translation(30003), "http://www.nickjr.de/videos", 'listEntries', iconJr)
    addDir(translation(30004), urlMain+"/shows?active_tab=1&ajax", 'listEntries', iconJr)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listEntries(url):
    content = opener.open(url).read()
    content = content[:content.find('<!-- all shows -->')]
    spl = content.split("teaser_item")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match1 = re.compile('title="(.*?)"', re.DOTALL).findall(entry)
        match2 = re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
        title = ""
        if match1 and match1[0]:
            title = match1[0]
        elif match2:
            title = match2[0]
        title = cleanTitle(title).strip(" -")
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("140x105","640x")
        match1 = re.compile('href="/videos/show/(.+?)"', re.DOTALL).findall(entry)
        match2 = re.compile('href="/videos/(.+?)"', re.DOTALL).findall(entry)
        if match1:
            url = urlMain+"/videos/show/"+match1[0]
            addDir(title, url, 'listEntries', thumb)
        elif match2:
            url = urlMain+"/videos/"+match2[0]
            addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = opener.open(url).read()
    match = re.compile("flashvars =.+?mrss.+?: '(.+?)'", re.DOTALL).findall(content)
    content = opener.open(match[0]).read()
    match = re.compile("<media:content.+?url='(.+?)'", re.DOTALL).findall(content)
    content = opener.open(match[0]).read()
    match = re.compile('type="video/mp4" bitrate="(.+?)">.+?<src>(.+?)</src>', re.DOTALL).findall(content)
    bitrate = 0
    for br, urlTemp in match:
        if int(br) > bitrate:
            bitrate = int(br)
            finalUrl = urlTemp
    listitem = xbmcgui.ListItem(path=finalUrl+" swfVfy=1 swfUrl=http://player.mtvnn.com/g2/g2player_2.1.7.swf")
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&#x27;", "'")
    title = title.strip()
    return title


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage!=icon and iconimage!=iconJr:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and iconimage!=icon and iconimage!=iconJr:
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listEntries':
    listEntries(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'nickMain':
    nickMain()
elif mode == 'nickJrMain':
    nickJrMain()
else:
    index()

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
addonID = 'plugin.video.checkeins_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
urlMain = "http://www.checkeins.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    addDir(translation(30001), urlMain+"/videos.html", 'listVideos', icon)
    addDir(translation(30002), "", 'listShows', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    content = opener.open(url).read()
    spl = ""
    if '<div class="videolist_hl">' in content:
        spl = content.split('<div class="videolist_hl">')
    elif '<div class="medialist' in content:
        spl = content.split('<div class="medialist')
    if spl:
        for i in range(1, len(spl), 1):
            entry = spl[i]
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = urlMain+"/"+match[0]
            match1 = re.compile('<h2>(.+?)</h2>', re.DOTALL).findall(entry)
            match2 = re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
            if match1:
                title = match1[0]
            if match2:
                title += " - "+match2[0]
            title = cleanTitle(title)
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = urlMain+"/"+match[0].replace(" ", "%20")
            addLink(title, url, 'playVideo', thumb)
    elif 'dataURL:' in content:
        content = content[content.find('dataURL:'):]
        match = re.compile("dataURL:'(.+?)'", re.DOTALL).findall(content)
        url = urlMain+"/"+match[0]
        match = re.compile("<h2>(.+?)</h2>", re.DOTALL).findall(content)
        title =match[0]
        title = cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(content)
        thumb = urlMain+"/"+match[0].replace(" ", "%20")
        addLink(title, url, 'playVideoDirect', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows():
    content = opener.open(urlMain+"/ajax.php?action=fmd&id=25").read()
    spl = content.split('<sendung>')
    for i in range(1, len(spl), 1):
        entry = spl[i].replace("<![CDATA[","").replace("]]>","")
        match = re.compile('<seite>(.+?)</seite>', re.DOTALL).findall(entry)
        url = urlMain+"/"+match[0]
        match = re.compile('<name>(.+?)</name>', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('<logoSrc>(.+?)</logoSrc>', re.DOTALL).findall(entry)
        thumb = urlMain+"/"+match[0].replace(" ", "%20")
        addDir(title, url, 'listShowVideos', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def listShowVideos(url):
    content = opener.open(url).read()
    match = re.compile('<div class="sub_navigation_entry"><a href="(.+?)".+?>(.+?)<', re.DOTALL).findall(content)
    videoURL = ""
    for url, title in match:
        if title=="Videos":
            videoURL = urlMain+"/"+url
    if videoURL:
        listVideos(videoURL)
    else:
        xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    content = opener.open(url).read()
    match = re.compile("dataURL:'(.+?)'", re.DOTALL).findall(content)
    url = urlMain+"/"+match[0]
    content = opener.open(url).read()
    match = re.compile("<streamingUrlIPad>(.+?)</streamingUrlIPad>", re.DOTALL).findall(content)
    finalURL = match[0].strip()
    listitem = xbmcgui.ListItem(path=finalURL)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playVideoDirect(url):
    content = opener.open(url).read()
    match = re.compile("<streamingUrlIPad>(.+?)</streamingUrlIPad>", re.DOTALL).findall(content)
    finalURL = match[0].strip()
    listitem = xbmcgui.ListItem(path=finalURL)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
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
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc="", audioUrl=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&audioUrl="+urllib.quote_plus(audioUrl)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
audioUrl = urllib.unquote_plus(params.get('audioUrl', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listShows':
    listShows()
elif mode == 'listShowVideos':
    listShowVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playVideoDirect':
    playVideoDirect(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()

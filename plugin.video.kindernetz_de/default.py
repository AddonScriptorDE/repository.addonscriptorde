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
addonID = 'plugin.video.kindernetz_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
iconClub = xbmc.translatePath('special://home/addons/'+addonID+'/iconClub.png')
iconGurke = xbmc.translatePath('special://home/addons/'+addonID+'/iconGurke.png')
iconHeld = xbmc.translatePath('special://home/addons/'+addonID+'/iconHeld.png')
iconPlosion = xbmc.translatePath('special://home/addons/'+addonID+'/iconPlosion.png')
iconTiere = xbmc.translatePath('special://home/addons/'+addonID+'/iconTiere.png')
urlMain = "http://www.kindernetz.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    addDir(translation(30001), urlMain+"/videobox/", 'listVideosLatest', icon)
    addDir(translation(30002), urlMain+"/tigerentenclub/tv/folgen/", 'listVideos', iconClub)
    addDir(translation(30003), urlMain+"/motzgurketv/allefolgen/", 'listVideos', iconGurke)
    addDir(translation(30004), urlMain+"/schmecksplosion/allefolgen/", 'listVideos', iconPlosion)
    addDir(translation(30005), urlMain+"/tiere/folgen/", 'listVideos', iconTiere)
    addDir(translation(30006), "", 'heldMain', iconHeld)
    xbmcplugin.endOfDirectory(pluginhandle)


def heldMain():
    addDir(translation(30008)+" 1", urlMain+"/helden/allefolgen1staffel/-/id=298480/ki2tmu/index.html", 'listVideosLatest', iconHeld)
    addDir(translation(30008)+" 2", urlMain+"/helden/allefolgen2staffel/-/id=298476/auskn0/index.html", 'listVideosLatest', iconHeld)
    addDir(translation(30008)+" 3", urlMain+"/helden/allefolgen3staffel/-/id=298472/903mn9/index.html", 'listVideosLatest', iconHeld)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosLatest(url):
    content = opener.open(url).read()
    spl = content.split('sources:')
    for i in range(1, len(spl), 1):
        entry = spl[i].replace('\\"','')
        match = re.compile('title:"(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('description:"(.+?)"', re.DOTALL).findall(entry)
        desc = ""
        if match:
            desc = match[0]
            desc = cleanTitle(desc)
        match = re.compile('file:"(.+?)"', re.DOTALL).findall(entry)
        url = match[len(match)-1]
        match = re.compile('image:"(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addLink(title, url, 'playVideoDirect', thumb, desc)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(url):
    content = opener.open(url).read()
    spl = content.split('rowspan="1" colspan="1"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        if match:
            url = match[0]
            match1 = re.compile('align="left"><a class="titel".+?>(.+?)<', re.DOTALL).findall(entry)
            match2 = re.compile('<a class="titel".+?>(.+?)<', re.DOTALL).findall(entry)
            match3 = re.compile('<a href=.+?>(.+?)<', re.DOTALL).findall(entry)
            if match1:
                title = match1[0]
            elif match2:
                title = match2[0]
            elif match3:
                title = match3[0]
            title = cleanTitle(title)
            match1 = re.compile('<div class="imagebox">.+?src="(.+?)"', re.DOTALL).findall(entry)
            match2 = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = ""
            if match1:
                thumb = match1[0]
            elif match2:
                thumb = match2[0]
            addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideoDirect(url):
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playVideo(url):
    content = opener.open(url).read()
    match = re.compile('file:"(.+?)"', re.DOTALL).findall(content)
    finalURL = match[len(match)-1]
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
    liz.addContextMenuItems([(translation(30007), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
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

if mode == 'heldMain':
    heldMain()
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosLatest':
    listVideosLatest(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playVideoDirect':
    playVideoDirect(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()

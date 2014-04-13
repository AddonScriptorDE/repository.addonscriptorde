#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.tele5_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
xbox = xbmc.getCondVisibility("System.Platform.xbox")
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
baseUrl = "http://www.tele5.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    listEntries(baseUrl+"/videos.html")  
    xbmcplugin.endOfDirectory(pluginhandle)


def listEntries(urlMain):
    content = opener.open(urlMain).read()
    content = content[content.find('<div class="videosGesamt">'):]
    content = content[:content.find('</section>')]
    spl = content.split('<a ')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
        title = match[0].replace("<br>",": ")
        match = re.compile('<p>(.+?)</p>', re.DOTALL).findall(entry)
        desc = match[0]
        desc = desc[:desc.find('<')]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        if urlMain==baseUrl+"/videos.html":
            addDir(title, url, 'listEntries', thumb, desc)
        else:
            addLink(title, url, 'playVideo', thumb, desc)
    xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    content = opener.open(url).read()
    matchID = re.compile('/entry_id/(.+?)"', re.DOTALL).findall(content)
    match2 = re.compile('resource="http://(.+?)/.+?/wid/_(.+?)/', re.DOTALL).findall(content)
    matchYT = re.compile('youtube.com/embed/(.+?)"', re.DOTALL).findall(content)
    if match2:
        url = "http://"+match2[0][0]+"/p/"+match2[0][1]+"/sp/"+match2[0][1]+"00/playManifest/entryId/"+matchID[0]+"/format/rtmp/protocol/rtmp/cdnHost/medianac.nacamar.de/ks/"
        content = opener.open(url).read()
        matchBase = re.compile('<baseURL>(.+?)</baseURL>', re.DOTALL).findall(content)
        matchStream = re.compile('<media url="(.+?)" bitrate="(.+?)"', re.DOTALL).findall(content)
        max = 0
        finalUrl = ""
        for stream, bitrate in matchStream:
            if int(bitrate)>max:
                finalUrl = matchBase[0]+"/"+stream[stream.find(':')+1:]
                max = int(bitrate)
    elif matchYT:
        ytID = matchYT[0]
        ytID = ytID[:ytID.find('?')]
        if xbox:
            finalUrl = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + ytID
        else:
            finalUrl = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + ytID
    listitem = xbmcgui.ListItem(path=finalUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
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
    liz.addContextMenuItems([(translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
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
else:
    index()

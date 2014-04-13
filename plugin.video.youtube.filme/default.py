#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcaddon
import xbmcplugin
import xbmcgui
import json
import sys
import re

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.youtube.filme'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
forceViewMode = addon.getSetting("forceView") == "true"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
viewMode = str(addon.getSetting("viewID"))
urlMain = "http://www.youtube.com"
mainChannelID = "UCAJ2KpG4wVeLbrJk4fAkI1Q"


def index():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = getUrl(urlMain+"/channel/"+mainChannelID+"/about")
    addDir("- "+translation(30006), urlMain+"/c4_browse_ajax?action_load_more_videos=1&flow=list&live_view=500&paging=1&channel_id="+mainChannelID+"&view=26", "listVideos", icon)
    spl = content.split('<div class="yt-lockup clearfix  yt-lockup-channel yt-lockup-grid vve-check"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="/channel/(.+?)"', re.DOTALL).findall(entry)
        id = match[0]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        addDir(title, id, "listVideosMain", icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosMain(channelID):
    addDir(translation(30002), urlMain+"/c4_browse_ajax?action_load_more_videos=1&flow=list&live_view=500&paging=1&channel_id="+channelID+"&view=11", "listVideos", icon)
    addDir(translation(30003), urlMain+"/c4_browse_ajax?action_load_more_videos=1&flow=list&live_view=500&paging=1&channel_id="+channelID+"&view=14", "listVideos", icon)
    addDir(translation(30001), urlMain+"/c4_browse_ajax?action_load_more_videos=1&flow=list&live_view=500&paging=1&channel_id="+channelID+"&view=10", "listVideos", icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUrl(url)
    jsonContent = json.loads(content).replace("\\n","").replace("\\","")
    spl = jsonContent.split("channels-browse-content-list-item")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('data-context-item-id="(.+?)"', re.DOTALL).findall(entry)
        id = match[0]
        match = re.compile('data-context-item-time="(.+?)"', re.DOTALL).findall(entry)
        duration = ""
        if match:
            duration = match[0]
            splDuration = duration.split(":")
            if len(splDuration)==2:
                duration = int(splDuration[0])
            elif len(splDuration)==3:
                duration = int(splDuration[0])*60+int(splDuration[1])
        match = re.compile('<div class="yt-lockup-description.+?>(.+?)</div>', re.DOTALL).findall(entry)
        desc = ""
        if match:
            desc = cleanTitle(match[0].encode('utf-8'))
        match = re.compile('</li><li>(.+?)<', re.DOTALL).findall(entry)
        year = ""
        if match:
            year = match[0]
        match = re.compile('data-context-item-title="(.+?)"', re.DOTALL).findall(entry)
        title = cleanTitle(match[0].encode('utf-8'))
        match = re.compile('data-thumb="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addLink(title, id, "playVideo", thumb, desc, duration, year)
    if 'class=\\"load-more-text\\"' in content:
        match = re.compile('paging=(.+?)&', re.DOTALL).findall(url)
        currentPage = match[0]
        nextPage = str(int(currentPage)+1)
        nextUrl = url.replace("paging="+currentPage,"paging="+nextPage)
        addDir(translation(30004)+" ("+nextPage+")", nextUrl, "listVideos", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(id):
    if xbox:
        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'BestOfYoutube XBMC Addon v2.1.1')
    response = urllib2.urlopen(req)
    content = response.read()
    response.close()
    return content


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def addLink(name, url, mode, iconimage, desc, duration, year):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year})
    liz.addContextMenuItems([(translation(30005), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosMain':
    listVideosMain(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()

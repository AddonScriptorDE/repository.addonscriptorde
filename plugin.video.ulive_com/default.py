#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import json
import xbmcplugin
import xbmcaddon
import xbmcgui

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = "plugin.video.ulive_com"
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceView") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewID = str(addon.getSetting("viewID"))
xbox = xbmc.getCondVisibility("System.Platform.xbox")
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
addonUserDataFolder = xbmc.translatePath(addon.getAddonInfo('profile'))
channelFavsFile = os.path.join(addonUserDataFolder ,'favourites')
icon = os.path.join(addonDir ,'icon.png')
iconCC = os.path.join(addonDir ,'iconCC.png')
iconDIY = os.path.join(addonDir ,'iconDIY.png')
iconFN = os.path.join(addonDir ,'iconFN.png')
iconHGTV = os.path.join(addonDir ,'iconHGTV.png')
iconTC = os.path.join(addonDir ,'iconTC.png')
baseUrl = "http://www.ulive.com"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)


def index():
    addDir(translation(30001), "", "listVideos", icon)
    addDir(translation(30002), "", "listPopular", icon)
    addDir(translation(30003), "", "listShowsFavs", icon)
    addDir(translation(30004), baseUrl+"/ulive-originals", "listShows", icon)
    addDir(translation(30005), baseUrl+"/hgtv", "listShows", iconHGTV)
    addDir(translation(30006), baseUrl+"/food-network", "listShows", iconFN)
    addDir(translation(30007), baseUrl+"/travel-channel", "listShows", iconTC)
    addDir(translation(30008), baseUrl+"/cooking-channel", "listShows", iconCC)
    addDir(translation(30009), baseUrl+"/diy-network", "listShows", iconDIY)
    addDir(translation(30017), "", "search", icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(urlMain):
    if not urlMain:
        urlMain = baseUrl+"/shows"
    content = opener.open(urlMain).read()
    spl = content.split('<div class="module media-module placeholder-container">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        match = re.compile('<h2><a.+?>(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        if urlMain==baseUrl+"/shows":
            match = re.compile('class="channel-data">(.+?)<', re.DOTALL).findall(entry)
            titleShow = cleanTitle(match[0])
            title = titleShow+" - "+title
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        thumb = urllib.unquote_plus(thumb[thumb.rfind("http"):]).replace("/resizes/500/","/")
        match = re.compile('class="icon-time"></i>(.+?)<', re.DOTALL).findall(entry)
        duration = match[0].strip()
        if duration.startswith("00:"):
            duration = "1"
        addLink(title, url, 'playVideo', thumb, "", duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listPopular(urlMain):
    if not urlMain:
        urlMain = baseUrl+"/shows"
    content = opener.open(urlMain).read()
    content = content[content.find('data-ulive-module="orderedList"'):]
    content = content[:content.find('<div class="pagination">')]
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        match = re.compile('class="video-title">(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        thumb = urllib.unquote_plus(thumb[thumb.rfind("http"):]).replace("/resizes/500/","/")
        match = re.compile('class="icon-time"></i>(.+?)<', re.DOTALL).findall(entry)
        duration = match[0].strip()
        addLink(title, url, 'playVideo', thumb, "", duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listShows(url, thumb):
    if url!=baseUrl+"/ulive-originals":
        addDir("- "+translation(30002), url, "listPopular", thumb)
    content = opener.open(url).read()
    spl = content.split('<div data-xhr=')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        match = re.compile('<h2><a.+?>(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        addShowDir(title, url, 'listVideosMain', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosMain(url, thumb):
    content = opener.open(url).read()
    match = re.compile('"DetailId" : "(.+?)"', re.DOTALL).findall(content)
    urlClips = baseUrl+"/ajax/showPageLoadMore.jsp?id="+match[0]+"&type=short&offset=0&limit=100"
    urlEpisodes = baseUrl+"/ajax/showPageLoadMore.jsp?id="+match[0]+"&type=long&offset=0&limit=100"
    if '<section id="long">' in content and '<section id="short">' not in content:
        listVideos(urlEpisodes)
    elif '<section id="long">' not in content and '<section id="short">' in content:
        listVideos(urlClips)
    else:
        if '<section id="long">' in content:
            addDir(translation(30010), urlEpisodes, "listVideos", thumb)
        if '<section id="short">' in content:
            addDir(translation(30011), urlClips, "listVideos", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def search(type):
    keyboard = xbmc.Keyboard('', translation(30017))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listSearch(baseUrl+"/search/?q="+search_string+"&i=1&state=1")


def listSearch(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<section class="module search-media-module theme-grey')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        match = re.compile('<h3><a.+?>(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        thumb = urllib.unquote_plus(thumb[thumb.rfind("http"):]).replace("/resizes/500/","/")
        match = re.compile('class="icon-time"></i>(.+?)<', re.DOTALL).findall(entry)
        duration = match[0].strip()
        if duration.startswith("00:"):
            duration = "1"
        addLink(title, url, 'playVideo', thumb, "", duration)
    match = re.compile('<link rel="next" href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30012), match[0], 'listSearch', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def playVideo(url):
    content = opener.open(url).read()
    matchUUID = re.compile('\'playerUUID\'.+?: "(.+?)"', re.DOTALL).findall(content)
    matchVideoID = re.compile('\'videoId\'.+?: "(.+?)"', re.DOTALL).findall(content)
    content = opener.open("http://mediacast.realgravity.com/vs/3/players/single/"+matchUUID[0]+"/"+matchVideoID[0]+".json").read()
    if '"geographically_blocked":true' in content:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30016))+',10000)')
    else:
        content = json.loads(content)
        max = 0
        streamURL = ""
        for item in content['playlists'][0]['videos'][0]['media']:
            bitRate = item['bitrate']
            if bitRate>=max:
                streamURL = item['file']
                max = bitRate
        listitem = xbmcgui.ListItem(path=streamURL)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def listShowsFavs():
    xbmcplugin.setContent(pluginhandle, "movies")
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if os.path.exists(channelFavsFile):
        fh = open(channelFavsFile, 'r')
        all_lines = fh.readlines()
        for line in all_lines:
            title = line[line.find("###TITLE###=")+12:]
            title = title[:title.find("#")]
            url = line[line.find("###URL###=")+10:]
            url = url[:url.find("#")]
            thumb = line[line.find("###THUMB###=")+12:]
            thumb = thumb[:thumb.find("#")]
            addShowFavDir(title, urllib.unquote_plus(url), "listVideosMain", thumb)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def favs(param):
    mode = param[param.find("###MODE###=")+11:]
    mode = mode[:mode.find("###")]
    channelEntry = param[param.find("###TITLE###="):]
    if mode == "ADD":
        if os.path.exists(channelFavsFile):
            fh = open(channelFavsFile, 'r')
            content = fh.read()
            fh.close()
            if content.find(channelEntry) == -1:
                fh = open(channelFavsFile, 'a')
                fh.write(channelEntry+"\n")
                fh.close()
        else:
            fh = open(channelFavsFile, 'a')
            fh.write(channelEntry+"\n")
            fh.close()
    elif mode == "REMOVE":
        refresh = param[param.find("###REFRESH###=")+14:]
        refresh = refresh[:refresh.find("#")]
        fh = open(channelFavsFile, 'r')
        content = fh.read()
        fh.close()
        entry = content[content.find(channelEntry):]
        fh = open(channelFavsFile, 'w')
        fh.write(content.replace(channelEntry+"\n", ""))
        fh.close()
        if refresh == "TRUE":
            xbmc.executebuiltin("Container.Refresh")


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace('\\"', '"').strip()
    return title


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def getPluginUrl():
    if xbox:
        return "plugin://video/"+addon.getAddonInfo('name')+"/"
    else:
        return "plugin://"+addonID+"/"


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
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30013), 'RunPlugin('+getPluginUrl()+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30014), 'RunPlugin('+getPluginUrl()+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowFavDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30015), 'RunPlugin('+getPluginUrl()+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosMain':
    listVideosMain(url, thumb)
elif mode == 'listPopular':
    listPopular(url)
elif mode == 'listSearch':
    listSearch(url)
elif mode == 'listShows':
    listShows(url, thumb)
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'search':
    search(url)
elif mode == 'favs':
    favs(url)
else:
    index()

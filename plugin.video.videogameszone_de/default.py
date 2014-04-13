#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import json
import datetime
import xbmcplugin
import xbmcaddon
import xbmcgui

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = "plugin.video.videogameszone_de"
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceView") == "true"
viewID = str(addon.getSetting("viewID"))
maxVideoQuality = addon.getSetting("maxVideoQuality")
maxVideoQuality = [800, 1200][int(maxVideoQuality)]
xbox = xbmc.getCondVisibility("System.Platform.xbox")
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
addonUserDataFolder = xbmc.translatePath(addon.getAddonInfo('profile'))
channelFavsFile = os.path.join(addonUserDataFolder ,'favourites')
icon = os.path.join(addonDir ,'icon.png')
baseUrl = "http://www.videogameszone.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)


def index():
    addDir(translation(30001), baseUrl+"/Videos/", "listVideos", icon)
    addDir(translation(30002), "", "archiv", icon)
    addDir(translation(30009), "videos", "search", icon)
    addDir(translation(30010), "games", "search", "")
    addDir(translation(30003), "", "listShowsFavs", icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<div class="articleticker_item')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find("<!-- end item -->")]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        match = re.compile('<div class="headline_box.*?">.+?<a.+?>(.+?)</a>', re.DOTALL).findall(entry)
        title = match[0]
        match = re.compile('<span class="videoArticleIcon">(.+?)</span>', re.DOTALL).findall(title)
        if match:
            title = title.replace(match[0], "")
        match = re.compile('<span(.+?)>', re.DOTALL).findall(title)
        for span in match:
            title = title.replace("<span"+span+">","")
        title = cleanTitle(title.replace("</span>",""))
        if "\n" in title:
            title = title[:title.find("\n")]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = ""
        if match:
            thumb = baseUrl+match[0]
        match = re.compile('<div class="degree degree_flame.+?>(.+?)</div>', re.DOTALL).findall(entry)
        if match:
            degree = match[0].replace("&deg;","°").strip()
            if degree!="0°" and degree!="Neu":
                title = title+" ("+degree+")"
        addLink(title, url, 'playVideo', thumb)
    match1 = re.compile("<a onClick=\"setSearchtypeSubmit\\('Videos', (.+?)\\)", re.DOTALL).findall(content)
    match2 = re.compile('<div class="onsitenavigation_right">.+?<a href="(.+?)"', re.DOTALL).findall(content)
    if match1:
        currentPage = urlMain[urlMain.find("page=")+5:]
        nextUrl = urlMain.replace("page="+currentPage, "page="+match1[0])
        addDir(translation(30005), nextUrl, 'listVideos', "")
    elif match2:
        addDir(translation(30005), baseUrl+"/Suche/"+match2[0], 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listGames(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<div class="top">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        if match:
            url = baseUrl+match[0]+"/Videos"
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0].strip()
            match = re.compile('<span class="search_platform">(.+?)</span>', re.DOTALL).findall(entry)
            platform = match[0].strip()
            title = cleanTitle(title+" "+platform)
            addShowDir(title, url, 'listVideos', "")
    match1 = re.compile("<a onClick=\"setSearchtypeSubmit\\('entity', (.+?)\\)", re.DOTALL).findall(content)
    match2 = re.compile('<div class="onsitenavigation_right">.+?<a href="(.+?)"', re.DOTALL).findall(content)
    if match1:
        currentPage = urlMain[urlMain.find("page=")+5:]
        nextUrl = urlMain.replace("page="+currentPage, "page="+match1[0])
        addDir(translation(30005), nextUrl, 'listGames', "")
    elif match2:
        addDir(translation(30005), baseUrl+"/Suche/"+match2[0], 'listGames', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def archiv():
    for i in range(1, 1001, 1):
        addDir((datetime.date.today()-datetime.timedelta(days=i)).strftime("%b %d, %Y"), baseUrl+"/Artikel-Archiv/Videos/Artikel-vom-"+(datetime.date.today()-datetime.timedelta(days=i)).strftime("%d-%m-%Y")+"/", 'listVideos', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def search(type):
    keyboard = xbmc.Keyboard('', translation(30004))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        if type=="videos":
            listVideos(baseUrl+"/Suche/?DATE_FROM=&DATE_TO=&FORMARTICLETYPE=alle&SEARCHTYPE=Videos&strSearch="+search_string+"&FORMARTICLETYPETHREAD=&FORMARTICLETYPEUSER=&page=1")
        elif type=="games":
            listGames(baseUrl+"/Suche/?DATE_FROM=&DATE_TO=&FORMARTICLETYPE=alle&SEARCHTYPE=entity&strSearch="+search_string+"&FORMARTICLETYPETHREAD=&FORMARTICLETYPEUSER=&page=1")


def playVideo(url):
    content = opener.open(url).read()
    matchID = re.compile('id="ova-player_(.+?)"', re.DOTALL).findall(content)
    matchYT = re.compile('youtube.com/v/(.+?)\\?', re.DOTALL).findall(content)
    if matchID:
        matchTitle = re.compile('<span itemprop="video".+?</span>.+?<meta itemprop="name" content="(.+?)"', re.DOTALL).findall(content)
        matchThumb = re.compile('<span itemprop="video".+?</span>.+?<meta itemprop="image" content="(.+?)"', re.DOTALL).findall(content)
        content = opener.open(baseUrl+"/commoncfm/flowneu/config_emb_js.cfm?vid="+matchID[0]).read().strip()
        match = re.compile('"bitrates": \\[(.+?)\\]', re.DOTALL).findall(content)
        match = re.compile('"url": "(.+?)", "bitrate": (.+?),', re.DOTALL).findall(match[0])
        max = 0
        streamURL = ""
        for url, bitrate in match:
            bitrate = int(bitrate)
            if bitrate>=max and bitrate<=maxVideoQuality:
                streamURL = url
                max = bitrate
        if matchThumb:
            listitem = xbmcgui.ListItem(path=streamURL, thumbnailImage=matchThumb[0])
        else:
            listitem = xbmcgui.ListItem(path=streamURL, thumbnailImage=icon)
        if matchTitle:
            listitem.setInfo(type='Video', infoLabels={'Title': matchTitle[0]})
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    elif matchYT:
        if xbox:
            listitem = xbmcgui.ListItem(path="plugin://video/Youtube/?path=/root/video&action=play_video&videoid="+matchYT[0])
        else:
            listitem = xbmcgui.ListItem(path="plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid="+matchYT[0])
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
            addShowFavDir(title, urllib.unquote_plus(url), "listVideos", thumb)
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
    liz.addContextMenuItems([(translation(30006), 'RunPlugin('+getPluginUrl()+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
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
    liz.addContextMenuItems([(translation(30007), 'RunPlugin('+getPluginUrl()+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowFavDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30008), 'RunPlugin('+getPluginUrl()+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listGames':
    listGames(url)
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'search':
    search(url)
elif mode == 'archiv':
    archiv()
elif mode == 'favs':
    favs(url)
else:
    index()

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
addonID = 'plugin.video.kika_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
ab3Only = addon.getSetting("ab3Only") == "true"
playSound = addon.getSetting("playSound") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
urlMain = "http://kikaplus.net"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    if ab3Only:
        kikaninchen()
    else:
        addDir(translation(30001), "", 'kikaninchen', icon)
        addDir(translation(30002), urlMain+"/clients/kika/kikaplus/index.php?ag=3", 'listVideos', icon)
        addDir(translation(30003), urlMain+"/clients/kika/kikaplus/index.php?ag=4", 'listVideos', icon)
        addDir(translation(30004), "", 'listShowsAZ', icon)
        addLink(translation(30005), "", 'playLive', icon)
        xbmcplugin.endOfDirectory(pluginhandle)


def kikaninchen():
    content = opener.open("http://www.kikaninchen.de/kikaninchen/filme/filme100-flashXml.xml").read()
    content = content[content.find('<links id="program">'):]
    spl = content.split('<multiMediaLink id="">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<description><!\\[CDATA\\[(.+?)\\]\\]></description>', re.DOTALL).findall(entry)
        desc = match[0]
        desc = cleanTitle(desc)
        match = re.compile('<path type="intern" target="flashapp">(.+?)</path>', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('/kikaninchen/filme/(.+?)/', re.DOTALL).findall(url)
        showID = match[0]
        showTitles = {'augsburgerpuppenkiste':'Augsburger Puppenkiste: Schlupp vom grünen Stern', 'kikabaumhaus':'Baumhaus', 'beutolomaeusunddievergesseneweihnacht':'Beutolomäus und die vergessene Weihnacht', 'bummi':'Bummi', 'mitmachmuehle':'Mit-Mach-Mühle', 'zigbydaszebra':'Zigby das Zebra', 'einemoehrefuerzwei':'Sesamstraße präsentiert: Eine Möhre für Zwei', 'ernieundbertsongs':'Sesamstraße präsentiert: Ernie & Bert Songs', 'zoeszauberschrank':'Zoes Zauberschrank', 'dreizweieinskeinsdasoliquiz':'3, 2, 1... keins! - Das OLI-Quiz', 'unsersandmaennchen':'Unser Sandmännchen', 'enemenebuunddranbistdu':'ENE MENE BU - und dran bist du', 'oliswildewelt':'OLIs Wilde Welt', 'ichkenneeintier':'Ich kenne ein Tier', 'meinbruderundich':'Mein Bruder und ich', 'sesamstrasse':'Sesamstraße', 'singasmusikbox':'Singas Musik Box', 'tomunddaserdbeermarmeladebrot':'TOM und das Erdbeermarmeladebrot mit Honig', 'weihnachtenmiternieundbert':'Weihnachten mit Ernie und Bert'}
        title = showTitles.get(showID, showID.title())
        match = re.compile('<image>(.+?)</image>', re.DOTALL).findall(entry)
        thumb = match[0]
        match = re.compile('<audio>(.+?)</audio>', re.DOTALL).findall(entry)
        audioUrl = ""
        if match:
            audioUrl = match[0]
        #GetImageHash - unable to stat url
        #thumb = thumb[:thumb.find('_h')]+"_v-galleryImage_-fc0f89b63e73c7b2a5ecbe26bac10a07631d8c2f.jpg"
        if not "auswahlkikaninchenfilme" in url and not "kikaninchentrailer" in url:
            addDir(title, url, 'listVideosKN', thumb, desc, audioUrl)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosKN(url, audioUrl):
    if playSound and audioUrl and not xbmc.Player().isPlaying():
        xbmc.Player().play(audioUrl)
    if url.endswith("index.html"):
        content = opener.open(url).read()
        match = re.compile('flashvars.page = "(.+?)"', re.DOTALL).findall(content)
        url = match[0]
    content = opener.open(url).read()
    fh = open("d:\\html.txt", 'w')
    fh.write(content)
    fh.close()
    spl = content.split('<movie>')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<title>(.+?)</title>', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('<mediaType>F4V</mediaType>.+?<flashMediaServerURL>(.+?)<', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('<image>(.+?)</image>', re.DOTALL).findall(entry)
        thumb = match[0]
        #GetImageHash - unable to stat url
        #thumb = thumb[:thumb.find('_h')]+"_v-galleryImage_-fc0f89b63e73c7b2a5ecbe26bac10a07631d8c2f.jpg"
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(url):
    content = opener.open(url).read()
    spl = content.split('<a style="position:relative')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('title="(.+?)<br /><br />', re.DOTALL).findall(entry)
        title = match[0].replace("<label>","").replace("</label>","").replace("<br />",": ")
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = urlMain+"/clients/kika/kikaplus/index.php"+match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = urlMain+"/clients/kika"+match[0][2:].replace("/previewpic/","/previewpic_orig/")
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsAZ():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain+"/clients/kika/kikaplus/index.php?startpage=true").read()
    content = content[content.find('<div id="a_z_overlay_text">'):]
    content = content[:content.find('</div>')]
    match = re.compile('<a href="(.+?)" title="(.+?)" class="overlay_link".*?>(.+?)</a>', re.DOTALL).findall(content)
    for url, vids, title in match:
        if "/kikaninchen/" in url:
            addDir(title, url, 'listVideosKN', icon)
        else:
            addDir(title, urlMain+"/clients/kika/kikaplus/index.php"+url, 'listVideos', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    if url.startswith("http://"):
        content = opener.open(url).read()
        match1 = re.compile('"fullscreenPfad", "(.+?)"', re.DOTALL).findall(content)
        match2 = re.compile('"pfad", "(.+?)"', re.DOTALL).findall(content)
        if match1:
            url = match1[0]
        elif match2:
            url = match2[0]
    else:
        content = opener.open(urlMain+"/clients/kika/common/public/config/server.xml").read()
        servers = []
        spl = content.split('<server>')
        for i in range(1, len(spl), 1):
            entry = spl[i]
            match = re.compile('<ip>(.+?)</ip>', re.DOTALL).findall(entry)
            if "<activated>1</activated>" in entry and "<rtmp>1</rtmp>" in entry:
                servers.append(match[0])
        random.shuffle(servers)
        url = "rtmp://"+servers[0]+"/vod"+url
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playLive():
    content = opener.open(urlMain+"/clients/kika/player/tvplayer.php?cmd=status").read()
    matchServer = re.compile('"server":"(.+?)"', re.DOTALL).findall(content)
    matchStream = re.compile('"stream":"(.+?)"', re.DOTALL).findall(content)
    listitem = xbmcgui.ListItem(path=matchServer[0].replace("\\","")+"/"+matchStream[0].replace("\\",""))
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
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
audioUrl = urllib.unquote_plus(params.get('audioUrl', ''))

if mode == 'kikaninchen':
    kikaninchen()
elif mode == 'listShowsAZ':
    listShowsAZ()
elif mode == 'listVideosKN':
    listVideosKN(url, audioUrl)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'playLive':
    playLive()
else:
    index()

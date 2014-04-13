#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import re
import sys
import xbmcplugin
import xbmcaddon
import xbmcgui
import subprocess

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonId = 'plugin.video.watchever_de'
addon = xbmcaddon.Addon(id=addonId)
translation = addon.getLocalizedString
baseUrl = "http://www.watchever.de"
osWin = xbmc.getCondVisibility('system.platform.windows')
osOsx = xbmc.getCondVisibility('system.platform.osx')
osLinux = xbmc.getCondVisibility('system.platform.linux')
useCoverAsFanart = addon.getSetting("useCoverAsFanart") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
winBrowser = addon.getSetting("winBrowser")


def index():
    addDir(translation(30002), "", "listMovies", "")
    addDir(translation(30003), "", "listTvShows", "")
    addDir(translation(30009), "", 'search', "")
    if osOsx or osLinux or (osWin and winBrowser=="1"):
        addDir(translation(30010), "http://www.watchever.de/mein-programm/watchliste", 'openBrowser', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listMovies(url):
    content = getUrl(baseUrl+"/filme")
    content = content[content.find('</div></a><div class="clear"></div></div><div class="RightColumn-hiddenmenu"><div class="btn-submenu-center double"><div class="container3">'):]
    content = content[:content.find('<div class="clear"></div></div></div></div>')]
    match = re.compile('<a href="(.+?)" class=".+?" vkey=".+?"><div>(.+?)</div></a>', re.DOTALL).findall(content)
    for url, title in match:
        addDir(title, url, 'showSortList', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listTvShows(url):
    content = getUrl(baseUrl+"/serien")
    content = content[content.find('</div></div><div class="col1"><div class="clear"></div>'):]
    content = content[:content.find('<div class="clear"></div></div></div></div>')]
    match = re.compile('<a href="(.+?)" class=".+?" vkey=".+?"><div>(.+?)</div></a>', re.DOTALL).findall(content)
    for url, title in match:
        addDir(title, url, 'showSortList', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def showSortList(url):
    urlViewed = url
    urlNew = url.replace("/meistgesehen", "/neu-im-programm")
    urlRated = url.replace("/meistgesehen", "/am-besten-bewertet")
    urlYear = url.replace("/meistgesehen", "/erscheinungsjahr")
    urlAZ = url.replace("/meistgesehen", "/a-z")
    addDir(translation(30004), urlViewed, "listVideos", "")
    addDir(translation(30005), urlNew, "listVideos", "")
    addDir(translation(30006), urlRated, "listVideos", "")
    addDir(translation(30007), urlYear, "listVideos", "")
    addDir(translation(30008), urlAZ, "listVideos", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUrl(url)
    spl = content.split('<p class="titleVideo"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('>(.+?)</p>', re.DOTALL).findall(entry)
        title = match[0].replace("<br>", " - ")
        title = cleanTitle(title)
        match = re.compile('class="folderPath" value="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+"/player"+match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("165x235", "495x705")
        addDir(title, url, 'openBrowser', thumb)
    match = re.compile('<div class="bgO"><a href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), match[0], "listVideos", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def search():
    keyboard = xbmc.Keyboard('', translation(30009))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "%2B")
        listVideos(baseUrl+"/suchanfrage/"+search_string)


def openBrowser(url):
    xbmc.Player().stop()
    if osWin:
        if winBrowser=="0":
            xbmc.executebuiltin('RunPlugin(plugin://plugin.program.webbrowser/?url='+urllib.quote_plus(url)+'&mode=showSite&showScrollbar=no)')
        elif winBrowser=="1":
            xbmc.executebuiltin('RunPlugin(plugin://plugin.program.chrome.launcher/?url='+urllib.quote_plus(url)+'&mode=showSite)')
    elif osOsx or osLinux:
        xbmc.executebuiltin('RunPlugin(plugin://plugin.program.chrome.launcher/?url='+urllib.quote_plus(url)+'&mode=showSite)')
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:, OS not supported!,5000)')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#038;", "&").replace("&#39;", "'")
    title = title.replace("&#039;", "'").replace("&#8211;", "-").replace("&#8220;", "-").replace("&#8221;", "-").replace("&#8217;", "'")
    title = title.replace("&quot;", "\"").replace("&uuml;", "ü").replace("&auml;", "ä").replace("&ouml;", "ö")
    title = title.strip()
    return title


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useCoverAsFanart:
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listMovies':
    listMovies(url)
elif mode == 'showSortList':
    showSortList(url)
elif mode == 'listTvShows':
    listTvShows(url)
elif mode == 'openBrowser':
    openBrowser(url)
elif mode == 'search':
    search()
else:
    index()

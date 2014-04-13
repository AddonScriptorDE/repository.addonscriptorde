#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import xbmcplugin
import xbmcaddon
import xbmcgui

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = "plugin.video.prosiebensat1_media"
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
forceViewMode = addon.getSetting("forceView") == "true"
viewID = str(addon.getSetting("viewID"))
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
icon = os.path.join(addonDir ,'icon.png')
iconPro7 = os.path.join(addonDir ,'iconPro7.png')
iconSat1 = os.path.join(addonDir ,'iconSat1.png')
iconKabel1 = os.path.join(addonDir ,'iconKabel1.png')
iconMaxx = os.path.join(addonDir ,'iconMaxx.png')
iconSixx = os.path.join(addonDir ,'iconSixx.png')
baseUrlPro7 = "http://www.prosieben.de"
baseUrlSat1 = "http://www.sat1.de"
baseUrlKabel1 = "http://www.kabel1.de"
baseUrlPro7Maxx = "http://www.prosiebenmaxx.de"
baseUrlSixx = "http://www.sixx.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    addDir("ProSieben", "", "mainPro7", iconPro7)
    addDir("Sat.1", "", "mainSat1", iconSat1)
    addDir("Kabel 1", "", "mainKabel1", iconKabel1)
    addDir("ProSiebenMaxx", "", "mainPro7Maxx", iconMaxx)
    addDir("Sixx", "", "mainSixx", iconSixx)
    xbmcplugin.endOfDirectory(pluginhandle)


def mainPro7():
    addDir("Neue Folgen", baseUrlPro7+"/video", "listVideosPro7", iconPro7)
    addDir("Schulz in the Box", baseUrlPro7+"/tv/schulz-in-the-box/playlists/ganze-folge", "listVideosPro7", iconPro7)
    addDir("Circus Halligalli", baseUrlPro7+"/tv/circus-halligalli/videos/playlist-alle-ganzen-folgen", "listVideosPro7", iconPro7)
    addDir("Joko gegen Klaas", baseUrlPro7+"/tv/joko-gegen-klaas/video/playlists/ganze-folgen", "listVideosPro7", iconPro7)
    addDir("Galileo", baseUrlPro7+"/tv/galileo/videos/playlists/ganze-folgen", "listVideosPro7", iconPro7)
    addDir("taff", baseUrlPro7+"/tv/taff/playlists/playlist-ganze-folgen-taff", "listVideosPro7", iconPro7)
    xbmcplugin.endOfDirectory(pluginhandle)


def mainSat1():
    addDir("Neue Folgen", baseUrlSat1+"/video", "listVideosSat1", iconSat1)
    #addDir("Alle Sendungen", "", "listShows", icon)
    listVideosSat1(baseUrlSat1+"/film/der-sat-1-filmfilm/video")


def mainKabel1():
    addDir("Neue Folgen", baseUrlKabel1+"/videos/ganze-folgen", "listVideosKabel1", iconKabel1)
    addDir("Sendungen", "", "listShowsKabel1", iconKabel1)
    xbmcplugin.endOfDirectory(pluginhandle)


def mainPro7Maxx():
    addDir("Serien & Dokus", baseUrlPro7Maxx+"/psdflow/ajaxblock/(block)/f47c1bfd15414eb4de06fa99816824dc/(offset)/0", "listVideosMaxx", iconMaxx)
    addDir("Yep", baseUrlPro7Maxx+"/psdflow/ajaxblock/(block)/d588a54972b4a74433a861e2e9980995/(offset)/0", "listVideosMaxx", iconMaxx)
    xbmcplugin.endOfDirectory(pluginhandle)


def mainSixx():
    addDir("Neue Folgen", baseUrlSixx+"/video", "listVideosSixx", iconSixx)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosPro7(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<div class="teaser-image">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrlPro7+match[0]
        match = re.compile('<span class="teaser-stats">(.+?)</span>', re.DOTALL).findall(entry)
        if match:
            duration = match[0]
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0].replace("Ganze Folge - ", "").replace("Ganze Folge: ", "")
            title = cleanTitle(title)
            match = re.compile("background-image:url\\('(.+?)'\\)", re.DOTALL).findall(entry)
            thumb = baseUrlPro7+match[0]
            if "/full/" in thumb:
                thumb = thumb[thumb.find("/full/"):]
                thumb = thumb[:thumb.rfind("-")]
                thumb = "http://thumbnails.sevenoneintermedia.de"+thumb+".jpg"
            if "/playlists/" in url:
                addDir(title, url, 'listVideosPro7', thumb)
            elif ("Preview:" not in title and "Highlight:" not in title and "Rückblick:" not in title and "Video" not in title) or "/playlists/" in urlMain:
                addLink(title, url, 'playVideoMobile', thumb, "", duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listVideosSat1(urlMain):
    content = opener.open(urlMain).read()
    spl = []
    if '<div class="class-clip' in content:
        spl = content.split('<div class="class-clip')
    elif '<article class="teaser' in content:
        spl = content.split('<article class="teaser')
    elif '<div class="video_teaser' in content:
        spl = content.split('<div class="video_teaser')
    elif 'class="teaser-image"' in content:
        spl = content.split('class="teaser-image"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "Ganze Folge - " in entry:
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = baseUrlSat1+match[0]
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            if match:
                title = match[0].replace("Ganze Folge - ","")
                title = cleanTitle(title)
                match = re.compile("background-image:url\\('(.+?)'\\)", re.DOTALL).findall(entry)
                thumb = match[0]
                if "/full/" in thumb:
                    thumb = thumb[thumb.find("/full/"):]
                    thumb = thumb[:thumb.rfind("-")]
                    thumb = "http://thumbnails.sevenoneintermedia.de"+thumb+".jpg"
                if not thumb.startswith("http"):
                    thumb = baseUrlSat1+thumb
                addLink(title, url, 'playVideoMobile', thumb, "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listVideosKabel1(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<figure class="class-clip">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrlKabel1+match[0]
        match = re.compile('<em>(.+?)</em>', re.DOTALL).findall(entry)
        duration = match[0]
        match = re.compile('<span class="subheadline" title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = title+" - "+match[0]
        title = cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = baseUrlKabel1+match[0]
        if "/full/" in thumb:
            thumb = thumb[thumb.find("/full/"):]
            thumb = thumb[:thumb.rfind("-")]
            thumb = "http://thumbnails.sevenoneintermedia.de"+thumb+".jpg"
        addLink(title, url, 'playVideoMobile', thumb, "", duration)
    spl = content.split('<li class="trackable_teaser"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrlKabel1+match[0]
        match = re.compile('<span class="subheadline">(.+?)</span>', re.DOTALL).findall(entry)
        if match:
            title = match[0].strip()
            match = re.compile('<span class="headline">(.+?)</span>', re.DOTALL).findall(entry)
            title = title+" "+match[0].strip()
            if "/full/" in thumb:
                thumb = thumb[thumb.find("/full/"):]
                thumb = thumb[:thumb.rfind("-")]
                thumb = "http://thumbnails.sevenoneintermedia.de"+thumb+".jpg"
            addLink(title, url, 'playVideoMobile', iconKabel1)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listShowsKabel1():
    content = opener.open(baseUrlKabel1+"/tv").read()
    spl = content.split('<li class="trackable_teaser"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "Videos" in entry or "Clips" in entry:
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = baseUrlKabel1+match[0]
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0]
            title = cleanTitle(title)
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = baseUrlKabel1+match[0]
            addDir(title, url, 'listShowKabel1', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def listShowKabel1(urlMain):
    content = opener.open(urlMain).read()
    if "/ganze-folgen" in content:
        addDir("Ganze Folgen", urlMain+"/ganze-folgen", "listVideosKabel1", iconKabel1)
    addDir("Clips", urlMain+"/videos", "listVideosKabel1", iconKabel1)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosMaxx(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<div class="teaser-image">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrlPro7Maxx+match[0]
        match = re.compile('<span class="teaser-stats">(.+?)</span>', re.DOTALL).findall(entry)
        if match:
            duration = match[0]
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0].replace("Ganze Folge - ", "").replace("Ganze Folge: ", "")
            title = cleanTitle(title)
            match = re.compile("background-image:url\\('(.+?)'\\)", re.DOTALL).findall(entry)
            thumb = baseUrlPro7Maxx+match[0]
            if "/full/" in thumb:
                thumb = thumb[thumb.find("/full/"):]
                thumb = thumb[:thumb.rfind("-")]
                thumb = "http://thumbnails.sevenoneintermedia.de"+thumb+".jpg"
            if "Preview:" not in title and "Highlight:" not in title and "Rückblick:" not in title and "Video" not in title:
                addLink(title, url, 'playVideoMobile', thumb, "", duration)
    match = re.compile('<li class="next">.+?data-href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), baseUrlPro7Maxx+match[0], 'listVideosMaxx', iconMaxx)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listVideosSixx(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<figure class="class-clip">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if ">Ganze Folge ansehen<" in entry:
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = baseUrlSixx+match[0]
            match = re.compile('<span class="subheadline" title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0]
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = title+" - "+match[0]
            title = cleanTitle(title)
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = baseUrlSixx+match[0]
            if "/full/" in thumb:
                thumb = thumb[thumb.find("/full/"):]
                thumb = thumb[:thumb.rfind("-")]
                thumb = "http://thumbnails.sevenoneintermedia.de"+thumb+".jpg"
            if "Preview:" not in title and "Highlight:" not in title and "Rückblick:" not in title and "Video" not in title:
                addLink(title, url, 'playVideoMobile', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listShows():
    content = opener.open(baseUrl).read()
    content = content[content.find('class="main_element"><span>Sendungen A-Z</span>'):]
    content = content[:content.find('</section>')]
    match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(content)
    for url, title in match:
        addDir(title, baseUrl+url, "listShow", icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listShow(url):
    addDir("Alle Videos", url+"/video", "listVideos", icon)
    content = opener.open(url).read()
    content = content[content.find('class="main_element">Video</a>'):]
    content = content[:content.find('</ul>')]
    match = re.compile('<a href="(.+?)".*?>(.+?)</a>', re.DOTALL).findall(content)
    for url, title in match:
        addDir(title, baseUrl+url, "listVideos", icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def playVideoMobile(url):
    content = opener.open(url).read()
    matchID = re.compile('"clip_id".*?:.*?"(.+?)"', re.DOTALL).findall(content)
    #content = opener.open("http://ws.vtc.sim-technik.de/video/video.jsonp?clipid="+matchID[0]+"&method=4").read()
    #match = re.compile('"VideoURL":"(.+?)"', re.DOTALL).findall(content)
    #streamURL = match[0].replace("\\","")
    streamURL = "http://ws.vtc.sim-technik.de/video/playlist.m3u8?ClipID="+matchID[0]
    listitem = xbmcgui.ListItem(path=streamURL)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playVideoDesktop(url):
    content = opener.open(url).read()
    match = re.compile('"clip_id" : "(.+?)"', re.DOTALL).findall(content)
    videoID = match[0]
    clientID = ""
    content = opener.open("http://vas.sim-technik.de/vas/live/v2/videos/"+videoID+"/sources?access_token=testclient&client_location="+urllib.quote_plus(url)+"&client_name=kolibri-1.2.5&client_id="+clientID).read()
    match = re.compile('"server_id":"(.+?)"', re.DOTALL).findall(content)
    serverID = match[0]
    content = opener.open("http://vas.sim-technik.de/vas/live/v2/videos/"+videoID+"/sources/url?access_token=testclient&client_location="+urllib.quote_plus(url)+"&client_name=kolibri-1.2.5&client_id="+clientID+"&server_id="+serverID+"&source_ids=1%2C3%2C4").read()
    streamURL = ""
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


def getPluginUrl(pluginID):
    plugin = xbmcaddon.Addon(id=pluginID)
    if xbmc.getCondVisibility("System.Platform.xbox"):
        return "plugin://video/"+plugin.getAddonInfo('name')
    else:
        return "plugin://"+plugin.getAddonInfo('id')


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
    liz.addContextMenuItems([(translation(30002), 'RunPlugin('+getPluginUrl(addonID)+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideosPro7':
    listVideosPro7(url)
elif mode == 'listVideosSat1':
    listVideosSat1(url)
elif mode == 'listVideosKabel1':
    listVideosKabel1(url)
elif mode == 'listVideosMaxx':
    listVideosMaxx(url)
elif mode == 'listVideosSixx':
    listVideosSixx(url)
elif mode == 'listShowsKabel1':
    listShowsKabel1()
elif mode == 'listShowKabel1':
    listShowKabel1(url)
elif mode == 'listShows':
    listShows()
elif mode == 'listShow':
    listShow(url)
elif mode == 'playVideoMobile':
    playVideoMobile(url)
elif mode == 'playVideoDesktop':
    playVideoDesktop(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'search':
    search(url)
elif mode == 'mainPro7':
    mainPro7()
elif mode == 'mainSat1':
    mainSat1()
elif mode == 'mainKabel1':
    mainKabel1()
elif mode == 'mainPro7Maxx':
    mainPro7Maxx()
elif mode == 'mainSixx':
    mainSixx()
else:
    index()

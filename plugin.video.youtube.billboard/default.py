#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcaddon
import xbmcplugin
import xbmcgui
import random
import sqlite3
import sys
import re
import os
import json

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
xbox = xbmc.getCondVisibility("System.Platform.xbox")
userDataFolder=xbmc.translatePath("special://profile/addon_data/"+addonID)
searchHistoryFolder=os.path.join(userDataFolder, "history")
socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
opener.addheaders = [('User-Agent', userAgent)]
urlMain = "http://www.billboard.com"

if not os.path.isdir(userDataFolder):
  os.mkdir(userDataFolder)
if not os.path.isdir(searchHistoryFolder):
  os.mkdir(searchHistoryFolder)


def getDbPath():
    path = xbmc.translatePath("special://userdata/Database")
    files = os.listdir(path)
    latest = ""
    for file in files:
        if file[:8] == 'MyVideos' and file[-3:] == '.db':
            if file > latest:
                latest = file
    if latest:
        return os.path.join(path, latest)
    else:
        return ""


def getPlayCount(url):
    if dbPath:
        c.execute('SELECT playCount FROM files WHERE strFilename=?', [url])
        result = c.fetchone()
        if result:
            result = result[0]
            if result:
                return int(result)
            return 0
    return -1


def index():
    addDir(translation(30005), urlMain+"/rss/charts/hot-100", "listCharts")
    addDir(translation(30006), "genre", "listChartsTypes")
    addDir(translation(30007), "country", "listChartsTypes")
    addDir(translation(30008), "other", "listChartsTypes")
    xbmcplugin.endOfDirectory(pluginhandle)


def listChartsTypes(type):
    if type=="genre":
        addDir(translation(30009), urlMain+"/rss/charts/pop-songs", "listCharts")
        addDir(translation(30010), urlMain+"/rss/charts/rock-songs", "listCharts")
        addDir(translation(30011), urlMain+"/rss/charts/alternative-songs", "listCharts")
        addDir(translation(30012), urlMain+"/rss/charts/r-b-hip-hop-songs", "listCharts")
        addDir(translation(30013), urlMain+"/rss/charts/r-and-b-songs", "listCharts")
        addDir(translation(30014), urlMain+"/rss/charts/rap-songs", "listCharts")
        addDir(translation(30015), urlMain+"/rss/charts/country-songs", "listCharts")
        addDir(translation(30016), urlMain+"/rss/charts/latin-songs", "listCharts")
        addDir(translation(30017), urlMain+"/rss/charts/jazz-songs", "listCharts")
        addDir(translation(30018), urlMain+"/rss/charts/dance-club-play-songs", "listCharts")
        addDir(translation(30019), urlMain+"/rss/charts/dance-electronic-songs", "listCharts")
        addDir(translation(30020), urlMain+"/rss/charts/heatseekers-songs", "listCharts")
    elif type=="country":
        addDir(translation(30021), urlMain+"/rss/charts/canadian-hot-100", "listCharts")
        addDir(translation(30022), urlMain+"/rss/charts/k-pop-hot-100", "listCharts")
        addDir(translation(30023), urlMain+"/rss/charts/japan-hot-100", "listCharts")
        addDir(translation(30024), urlMain+"/rss/charts/germany-songs", "listCharts")
        addDir(translation(30025), urlMain+"/rss/charts/france-songs", "listCharts")
        addDir(translation(30026), urlMain+"/rss/charts/united-kingdom-songs", "listCharts")
    elif type=="other":
        addDir(translation(30028), urlMain+"/rss/charts/radio-songs", "listCharts")
        addDir(translation(30029), urlMain+"/rss/charts/digital-songs", "listCharts")
        addDir(translation(30030), urlMain+"/rss/charts/streaming-songs", "listCharts")
        addDir(translation(30031), urlMain+"/rss/charts/on-demand-songs", "listCharts")
    xbmcplugin.endOfDirectory(pluginhandle)


def listCharts(url):
    xbmcplugin.setContent(pluginhandle, "episodes")
    addDir("[B]- "+translation(30001)+"[/B]", url, "autoPlay", "all")
    addDir("[B]- "+translation(30002)+"[/B]", url, "autoPlay", "random")
    if dbPath:
        addDir("[B]- "+translation(30003)+"[/B]", url, "autoPlay", "unwatched")
    content = opener.open(url).read()
    match = re.compile('<item>.+?<artist>(.+?)</artist>.+?<chart_item_title>(.+?)</chart_item_title>', re.DOTALL).findall(content)
    for artist, title in match:
        title = cleanTitle(artist+" - "+title[title.find(":")+1:]).replace("Featuring", "Feat.")
        fileTitle = (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip()
        cacheFile = os.path.join(searchHistoryFolder, fileTitle)
        thumb = ""
        if os.path.exists(cacheFile):
            fh = open(cacheFile, 'r')
            id = fh.read()
            fh.close()
            thumb = "http://img.youtube.com/vi/"+id+"/0.jpg"
        addLink(title, title, "playVideo", thumb, "", "", title)
    xbmcplugin.endOfDirectory(pluginhandle)


def cache(id, chartTitle):
    fileTitle = (''.join(c for c in unicode(chartTitle, 'utf-8') if c not in '/\\:?"*|<>')).strip()
    cacheFile = os.path.join(searchHistoryFolder, fileTitle)
    fh = open(cacheFile, 'w')
    fh.write(id)
    fh.close()
    listitem = xbmcgui.ListItem(path=getYoutubePluginUrl(id))
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playVideo(title):
    fileTitle = (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip()
    cacheFile = os.path.join(searchHistoryFolder, fileTitle)
    if os.path.exists(cacheFile):
        fh = open(cacheFile, 'r')
        id = fh.read()
        fh.close()
        listitem = xbmcgui.ListItem(path=getYoutubePluginUrl(id))
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    else:
        id = getYoutubeId(title)
        cache(id, title)


def getYoutubeId(title):
    #API sometimes delivers other results (when sorting by relevance) than site search!?!
    """content = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+urllib.quote_plus(title)+"&max-results=1&start-index=1&orderby=relevance&alt=json&time=all_time&v=2").read()
    match=re.compile(':video:(.+?)"', re.DOTALL).findall(content)"""
    content = opener.open("https://www.youtube.com/results?search_query="+urllib.quote_plus(title)+"&lclk=video").read()
    content = content[content.find('id="search-results"'):]
    match=re.compile('data-video-ids="(.+?)"', re.DOTALL).findall(content)
    return match[0]


def listVideos(chartTitle):
    #API sometimes delivers other results (when sorting by relevance) than site search!?!
    """content = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+urllib.quote_plus(chartTitle)+"&max-results=20&start-index=1&orderby=relevance&alt=json&time=all_time&v=2").read()
    content = json.loads(content)
    for entry in content['feed']['entry']:
        id=entry['media$group']['yt$videoid']['$t']
        title=entry['title']['$t'].encode('utf-8')
        views=str(entry['yt$statistics']['viewCount'])
        rUp=entry['yt$rating']['numLikes']
        rDown=entry['yt$rating']['numDislikes']
        rating=str(int((float(rUp)/(float(rUp)+float(rDown)))*100)) + " % like it"
        length= str(entry['media$group']['yt$duration']['seconds'])
        desc= entry['media$group']['media$description']['$t'].encode('utf-8')
        desc = views+" Views   |   "+rating+"\n"+desc
        thumb = "http://img.youtube.com/vi/"+id+"/0.jpg"
        addLink(title, id, "cache", thumb, desc, length, chartTitle)
    xbmcplugin.endOfDirectory(pluginhandle)"""
    content = opener.open("https://www.youtube.com/results?search_query="+urllib.quote_plus(chartTitle)+"&lclk=video").read()
    content = content[content.find('id="search-results"'):]
    spl=content.split('<li class="yt-lockup clearfix')
    for i in range(1, len(spl), 1):
        try:
            entry=spl[i]
            match=re.compile('data-video-ids="(.+?)"', re.DOTALL).findall(entry)
            id=match[0]
            match=re.compile('<h3 class="yt-lockup-title">.+?title="(.+?)"', re.DOTALL).findall(entry)
            title=match[0]
            title = cleanTitle(title)
            match=re.compile('data-name=.+?<li>(.+?)</li><li>(.+?)<', re.DOTALL).findall(entry)
            desc = ""
            if match:
                desc=match[0][0]+" - "+match[0][1]
            match=re.compile('class="video-time">(.+?)<', re.DOTALL).findall(entry)
            length=match[0]
            thumb = "http://img.youtube.com/vi/"+id+"/0.jpg"
            addLink(title, id, "cache", thumb, desc, length, chartTitle)
        except:
            pass
    xbmcplugin.endOfDirectory(pluginhandle)


def getYoutubePluginUrl(id):
    if xbox:
        return "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        return "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def autoPlay(url, type):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open(url).read()
    match = re.compile('<item>.+?<title>(.+?)</title>', re.DOTALL).findall(content)
    for title in match:
        title = cleanTitle(title[title.find(":")+1:]).replace("Featuring", "Feat.")
        url = sys.argv[0]+"?url="+urllib.quote_plus(title)+"&mode=playVideo&name="+str(title)+"&chartTitle="+str(title)
        if type in ["all", "random"]:
            listitem = xbmcgui.ListItem(title)
            entries.append([title, url])
        elif type=="unwatched" and getPlayCount(url) < 0:
            listitem = xbmcgui.ListItem(title)
            entries.append([title, url])
    if type=="random":
        random.shuffle(entries)
    for title, url in entries:
        listitem = xbmcgui.ListItem(title)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def addLink(name, url, mode, iconimage, desc="", length="", chartTitle=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)+"&chartTitle="+str(chartTitle)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": length})
    liz.setProperty('IsPlayable', 'true')
    entries = []
    entries.append((translation(30032), 'Container.Update(plugin://'+addonID+'/?mode=listVideos&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
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


dbPath = getDbPath()
if dbPath:
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
type = urllib.unquote_plus(params.get('type', ''))
chartTitle = urllib.unquote_plus(params.get('chartTitle', ''))

if mode == 'listCharts':
    listCharts(url)
elif mode == 'listChartsTypes':
    listChartsTypes(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'cache':
    cache(url, chartTitle)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name)
elif mode == 'autoPlay':
    autoPlay(url, type)
else:
    index()

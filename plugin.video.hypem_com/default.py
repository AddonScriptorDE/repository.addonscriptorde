#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import cookielib
import sys
import re
import os
import time
import json
import base64
import datetime
import xbmcplugin
import xbmcgui
import xbmcaddon

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
cj = cookielib.LWPCookieJar()
urlMain = "http://hypem.com"
urlMainApi = "http://api.hypem.com"
xbox = xbmc.getCondVisibility("System.Platform.xbox")
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0"
opener.addheaders = [('User-agent', userAgent)]
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
searchHistoryFolder=os.path.join(addonUserDataFolder, "history")
cookieFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cookies")
siteMode=addon.getSetting("siteMode")
username=addon.getSetting("username")
password=addon.getSetting("password")
showLatestRemix=addon.getSetting("showLatestRemix") == "true"
showLatestNoRemix=addon.getSetting("showLatestNoRemix") == "true"
showPopularRemix=addon.getSetting("showPopularRemix") == "true"
showPopularNoRemix=addon.getSetting("showPopularNoRemix") == "true"
showZeitgeist=addon.getSetting("showZeitgeist") == "true"

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(searchHistoryFolder):
    os.mkdir(searchHistoryFolder)
if os.path.exists(cookieFile):
    cj.load(cookieFile)


def index():
    if siteMode=="0":
        if username and password:
            login()
        addDir(translation(30006), "", 'myMain', "")
        addDir(translation(30002), urlMain+"/latest/1?ax=1", 'listSongs', "")
        addDir(translation(30028), urlMain+"/latest/fresh/1?ax=1", 'listSongs', "")
        if showLatestRemix:
            addDir(translation(30002) + " (" + translation(30010) + ")", urlMain+"/latest/remix/1?ax=1", 'listSongs', "")
        if showLatestNoRemix:
            addDir(translation(30002) + " (" + translation(30011) + ")", urlMain+"/latest/noremix/1?ax=1", 'listSongs', "")
        addDir(translation(30003), urlMain+"/popular/1?ax=1", 'listSongs', "")
        if showPopularRemix:
            addDir(translation(30003) + " (" + translation(30010) + ")", urlMain+"/popular/remix/1?ax=1", 'listSongs', "")
        if showPopularNoRemix:
            addDir(translation(30003) + " (" + translation(30011) + ")", urlMain+"/popular/noremix/1?ax=1", 'listSongs', "")
        addDir(translation(30004), urlMain+"/popular/lastweek/1?ax=1", 'listSongs', "")
        addDir(translation(30021), "", 'listTimeMachine', "")
        if showZeitgeist:
            addDir(translation(30019), "", 'listZeitgeist', "")
        addDir(translation(30005), "", 'listGenres', "")
        addDir(translation(30013), "", 'search', "")
    else:
        addDir("Latest", urlMainApi+"/api/experimental_video_latest", 'listVideos', "")
        addDir("Popular", urlMainApi+"/api/experimental_video_popular", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def myMain():
    if username:
        addDir(translation(30018), urlMain+"/"+username+"/feed/1?ax=1", 'listSongs', "")
        addDir(translation(30014), "", 'listMyArtists', "")
        addDir(translation(30007), urlMain+"/"+username+"/1?ax=1", 'listSongs', "")
        addDir(translation(30026), urlMain+"/"+username+"/shuffle/1?ax=1", 'listSongs', "")
        addDir(translation(30008), urlMain+"/"+username+"/history/1?ax=1", 'listSongs', "")
        addDir(translation(30009), urlMain+"/"+username+"/obsessed/1?ax=1", 'listSongs', "")
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30022)+',5000)')
        addon.openSettings()


def listSongs(url):
    parentUrl = url
    content = opener.open(url).read()
    cj.save(cookieFile)
    match = re.compile('id="displayList-data">(.+?)<', re.DOTALL).findall(content)
    jsonContent = json.loads(match[0].strip())
    for track in jsonContent['tracks']:
        url = "/serve/source/"+track['id']+"/"+track['key']
        titleRaw = (track['artist'].encode('utf-8')+" - "+track['song'].encode('utf-8')).strip()
        fileTitle = (''.join(c for c in unicode(titleRaw, 'utf-8') if c not in '/\\:?"*|<>')).strip()
        cacheFile = os.path.join(searchHistoryFolder, fileTitle)
        title = titleRaw
        if track['fav']==1:
            title = "[B]*[/B] " + title + " [B]*[/B]"
        thumb = ""
        if os.path.exists(cacheFile):
            fh = open(cacheFile, 'r')
            id = fh.read()
            fh.close()
            thumb = "http://img.youtube.com/vi/"+id+"/0.jpg"
        addLink(title, titleRaw, 'playVideo', thumb, track['time'], track['id'], track['artist'].encode('utf-8'), track['fav'], parentUrl)
    match = re.compile('"page_next":"(.+?)"', re.DOTALL).findall(content)
    if match:
        url = match[0].replace("\\","")
        addDir(translation(30001), urlMain+url+"?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    jsonContent = json.loads(opener.open(url).read())
    for video in jsonContent:
        id = video['url']
        site = video['hreftitle']
        title = video['posttitle']
        date = video['dateposted']
        thumb = "http://img.youtube.com/vi/"+id+"/0.jpg"
        url = ""
        if site=="YOUTUBE":
            url = getYoutubePluginUrl(id)
        elif site=="VIMEO":
            url = getVimeoPluginUrl(id)
        if url:
            addLinkSimple(title, url, 'playVideoDirect', thumb, date)
    xbmcplugin.endOfDirectory(pluginhandle)


def listGenres():
    content = opener.open(urlMain).read()
    match = re.compile('<li><a href="/tags/(.+?)">(.+?)<', re.DOTALL).findall(content)
    for id, title in match:
        addDir(title, urlMain+"/tags/"+id+"/1?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def cache(id, chartTitle, hypemID):
    fileTitle = (''.join(c for c in unicode(chartTitle, 'utf-8') if c not in '/\\:?"*|<>')).strip()
    cacheFile = os.path.join(searchHistoryFolder, fileTitle)
    fh = open(cacheFile, 'w')
    fh.write(id)
    fh.close()
    listitem = xbmcgui.ListItem(path=getYoutubePluginUrl(id))
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    if username and password:
        opener.open("http://hypem.com/inc/user_action.php?act=log_action&type=listen&session="+getSession()+"&val="+hypemID+"&playback_manual=1")


def playVideo(title, hypemID):
    fileTitle = (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip()
    cacheFile = os.path.join(searchHistoryFolder, fileTitle)
    if os.path.exists(cacheFile):
        fh = open(cacheFile, 'r')
        id = fh.read()
        fh.close()
        listitem = xbmcgui.ListItem(path=getYoutubePluginUrl(id))
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if username and password:
            opener.open("http://hypem.com/inc/user_action.php?act=log_action&type=listen&session="+getSession()+"&val="+hypemID+"&playback_manual=1")
    else:
        id = getYoutubeId(title)
        cache(id, title, hypemID)


def playVideoDirect(url):
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def getYoutubeId(title):
    #API sometimes delivers other results (when sorting by relevance) than site search!?!
    #content = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+urllib.quote_plus(title)+"&max-results=1&start-index=1&orderby=relevance&time=all_time&v=2").read()
    #match=re.compile('<yt:videoid>(.+?)</yt:videoid>', re.DOTALL).findall(content)
    content = opener.open("https://www.youtube.com/results?search_query="+urllib.quote_plus(title)+"&lclk=video").read()
    content = content[content.find('id="search-results"'):]
    match=re.compile('data-context-item-id="(.+?)"', re.DOTALL).findall(content)
    return match[0]


def getYoutubePluginUrl(id):
    if xbox:
        return "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        return "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id


def getVimeoPluginUrl(id):
    if xbox:
        url = "plugin://video/Vimeo/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.vimeo/?path=/root/video&action=play_video&videoid=" + id
    return url


def queueVideo(url, title):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(title)
    playlist.add(url, listitem)


def search():
    keyboard = xbmc.Keyboard('', translation(30013))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "%20")
        listSongs(urlMain+"/search/"+search_string+"/1?ax=1&sortby=fav")


def getSession():
    fh = open(cookieFile, 'r')
    cookies = fh.read()
    fh.close()
    match = re.compile('AUTH="03%3A(.+?)%', re.DOTALL).findall(cookies)
    return match[0]


def login():
    content = opener.open(urlMain+"/1?ax=1").read()
    if "show_lightbox('account')" not in content:
        cj.save(cookieFile)
        content = opener.open("https://hypem.com/inc/user_action.php", "act=login&session="+getSession()+"&user_screen_name="+username+"&user_password="+password).read()


def toggleLike(songID):
    opener.open("https://hypem.com/inc/user_action.php", "act=toggle_favorite&session="+getSession()+"&type=item&val="+songID)
    xbmc.executebuiltin("Container.Refresh")


def toggleFollow(artist):
    opener.open("https://hypem.com/inc/user_action.php", "act=toggle_favorite&session="+getSession()+"&type=query&val="+artist)
    xbmc.executebuiltin("Container.Refresh")


def listMyArtists():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain+"/"+username+"/list_artists").read()
    match = re.compile('<a href="/search/(.+?)">(.+?)<', re.DOTALL).findall(content)
    for id, title in match:
        addDirR(title.title(), urlMain+"/search/"+id+"/1?ax=1&sortby=fav", 'listSongs', "", title)
    xbmcplugin.endOfDirectory(pluginhandle)


def listZeitgeist():
    addDir("2011", urlMain+"/zeitgeist/2011/songs_list?ax=1", 'listSongs', "")
    addDir("2012", urlMain+"/zeitgeist/2012/tracks_list?ax=1", 'listSongs', "")
    addDir("2013", urlMain+"/zeitgeist/2013/tracks_list?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listTimeMachine():
    for i in range(1, 210, 1):
        dt = datetime.date.today()
        while dt.weekday()!=0:
            dt -= datetime.timedelta(days=1)
        dt -= datetime.timedelta(weeks=i)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        month = months[int(dt.strftime("%m"))-1]
        addDir(dt.strftime("%b %d, %Y"), urlMain+"/popular/week:"+month+"-"+dt.strftime("%d-%Y")+"/1?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def chooseVideo(chartTitle, hypemID):
    #API sometimes delivers other results (when sorting by relevance) than site search!?!
    content = opener.open("https://www.youtube.com/results?search_query="+urllib.quote_plus(chartTitle)+"&lclk=video").read()
    content = content[content.find('id="search-results"'):]
    spl=content.split('<li class="yt-lockup clearfix')
    for i in range(1, len(spl), 1):
        try:
            entry=spl[i]
            match=re.compile('data-context-item-id="(.+?)"', re.DOTALL).findall(entry)
            id=match[0]
            match=re.compile('data-context-item-title="(.+?)"', re.DOTALL).findall(entry)
            title=match[0]
            match=re.compile('data-context-item-views="(.+?)"', re.DOTALL).findall(entry)
            views=match[0]
            match=re.compile('data-context-item-time="(.+?)"', re.DOTALL).findall(entry)
            length=match[0]
            match=re.compile('<div class="yt-lockup-description.+?>(.+?)</div>', re.DOTALL).findall(entry)
            desc = ""
            if match:
                desc=match[0].replace("<b>","").replace("</b>","")
            desc = views+"\n"+desc
            thumb = "http://img.youtube.com/vi/"+id+"/0.jpg"
            addYTLink(title, id, "cache", thumb, desc, length, chartTitle, hypemID)
        except:
            pass
    xbmcplugin.endOfDirectory(pluginhandle)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, duration, songID, artist, fav, parentUrl):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&hypemID="+str(songID)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    liz.addStreamInfo('video', { 'duration': int(duration) })
    liz.setProperty('IsPlayable', 'true')
    entries = []
    if "/popular/" in parentUrl:
        entries.append((translation(30027), 'Container.Update(plugin://'+addonID+'/?mode=listSongs&url='+urllib.quote_plus(parentUrl+"&sortby=shuffle")+')',))
    if username and password:
        if fav==0:
            entries.append((translation(30015), 'RunPlugin(plugin://'+addonID+'/?mode=toggleLike&url='+urllib.quote_plus(songID)+')',))
        else:
            entries.append((translation(30020), 'RunPlugin(plugin://'+addonID+'/?mode=toggleLike&url='+urllib.quote_plus(songID)+')',))
    entries.append((translation(30025), 'Container.Update(plugin://'+addonID+'/?mode=listSongs&url='+urllib.quote_plus(urlMain+"/search/"+artist+"/1?ax=1&sortby=fav")+')',))
    if username and password:
        entries.append((translation(30016), 'RunPlugin(plugin://'+addonID+'/?mode=toggleFollow&url='+urllib.quote_plus(artist)+')',))
    entries.append((translation(30024), 'Container.Update(plugin://'+addonID+'/?mode=chooseVideo&url='+urllib.quote_plus(url)+"&hypemID="+str(songID)+')',))
    entries.append((translation(30023), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addYTLink(name, url, mode, iconimage, desc="", length="", chartTitle="", hypemID=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)+"&chartTitle="+str(chartTitle)+"&hypemID="+str(hypemID)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": length})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addLinkSimple(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDirR(name, url, mode, iconimage, artist):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    entries = []
    if username and password:
        entries.append((translation(30017), 'RunPlugin(plugin://'+addonID+'/?mode=toggleFollow&url='+urllib.quote_plus(artist)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
hypemID = urllib.unquote_plus(params.get('hypemID', ''))
chartTitle = urllib.unquote_plus(params.get('chartTitle', ''))

if mode == 'listSongs':
    listSongs(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'listGenres':
    listGenres()
elif mode == 'myMain':
    myMain()
elif mode == 'toggleLike':
    toggleLike(url)
elif mode == 'toggleFollow':
    toggleFollow(url)
elif mode == 'listMyArtists':
    listMyArtists()
elif mode == 'listZeitgeist':
    listZeitgeist()
elif mode == 'listTimeMachine':
    listTimeMachine()
elif mode == 'playVideo':
    playVideo(url, hypemID)
elif mode == 'queueVideo':
    queueVideo(url, name)
elif mode == 'chooseVideo':
    chooseVideo(url, hypemID)
elif mode == 'cache':
    cache(url, chartTitle, hypemID)
elif mode == 'search':
    search()
else:
    index()

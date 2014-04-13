#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import urllib2
import sqlite3
import json
import re
import os
import random


class XBMCPlayer(xbmc.Player):
    def onPlayBackStopped(self):
        xbmc.sleep(exitDelay)
        myWindow.close()
        if setVolume and muted():
            xbmc.executebuiltin('XBMC.Mute()')
        elif setVolume:
            xbmc.executebuiltin('XBMC.SetVolume('+str(currentVolume)+')')
        if playbackInterrupted:
            xbmc.sleep(500)
            xbmc.Player().play(currentUrl)
            xbmc.Player().seekTime(currentPosition-jumpBack)
            xbmc.Player().pause()
        else:
            xbmc.Player().stop()

    def onPlayBackEnded(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        pos = playlist.getposition()
        if pos == len(playlist)-1:
            xbmc.sleep(5000)
            myWindow.close()
            if setVolume and muted():
                xbmc.executebuiltin('XBMC.Mute()')
            elif setVolume:
                xbmc.executebuiltin('XBMC.SetVolume('+str(currentVolume)+')')
            if playbackInterrupted:
                xbmc.sleep(500)
                xbmc.Player().play(currentUrl)
                xbmc.Player().seekTime(currentPosition-jumpBack)
                xbmc.Player().pause()
            else:
                xbmc.Player().stop()


class window(xbmcgui.WindowXMLDialog):
    def onInit(self):
        if content=="video":
            try:
                addVideos()
            except:
                pass
            if playlist:
                if setVolume and not muted():
                    if volume==0:
                        xbmc.executebuiltin('XBMC.Mute()')
                    else:
                        xbmc.executebuiltin('XBMC.SetVolume('+str(volume)+')')
                myPlayer.play(playlist)
            else:
                xbmc.executebuiltin('XBMC.Notification(Video Screensaver:,'+translation(30005)+'!,5000)')
                myPlayer.stop()
                myWindow.close()
        elif content=="image":
            playSlideshow()

    def onAction(self, action):
        if content=="image":
            myWindow.close()
        else:
            ACTION_STOP = 13
            ACTION_PREVIOUS_MENU = 10
            if action in [ACTION_PREVIOUS_MENU, ACTION_STOP]:
                myPlayer.stop()

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
urlMain = "http://www.reddit.com"
opener = urllib2.build_opener()
userAgent = "XBMC | "+addonID+" | "+addon.getAddonInfo('version')
opener.addheaders = [('User-Agent', userAgent)]
hosterQuery = urllib.quote_plus("site:youtu.be OR site:youtube.com OR site:vimeo.com OR site:liveleak.com OR site:dailymotion.com")
hosterQueryImages = urllib.quote_plus("site:imgur.com")
xbox = xbmc.getCondVisibility("System.Platform.xbox")
translation = addon.getLocalizedString
jumpBack = int(addon.getSetting("jumpBack"))
type = int(addon.getSetting("type"))
type = ["hot","top","new","comments"][int(type)]
content = int(addon.getSetting("content"))
content = ["video","image"][int(content)]
playUnwatched = addon.getSetting("playUnwatched") == "true"
setVolume = addon.getSetting("setVolume") == "true"
subreddit = addon.getSetting("subreddit")
volume = int(addon.getSetting("volume"))
currentVolume = xbmc.getInfoLabel("Player.Volume")
currentVolume = int((float(currentVolume.split(" ")[0])+60.0)/60.0*100.0)
exitDelay = int(addon.getSetting("exitDelay"))
myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
myPlayer = XBMCPlayer()
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
playlist.clear()
playbackInterrupted = False
currentUrl = ""
currentPosition = 0
if xbmc.Player().isPlayingVideo():
    currentUrl = xbmc.Player().getPlayingFile()
    currentPosition = xbmc.Player().getTime()
    xbmc.Player().stop()
    xbmc.sleep(1000)
    playbackInterrupted = True

def muted():
    return xbmc.getCondVisibility("Player.Muted")


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


def addVideos():
    entries = []
    if type=="new":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=new&restrict_sr=on&limit=100"
    elif type=="hot":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=hot&restrict_sr=on&limit=100&t=day"
    elif type=="top":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=top&restrict_sr=on&limit=100&t=week"
    elif type=="comments":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=comments&restrict_sr=on&limit=100&t=day"
    content = opener.open(url).read()
    content = json.loads(content.replace('\\"', '\''))
    for entry in content['data']['children']:
        try:
            title = cleanTitle(entry['data']['media']['oembed']['title'].encode('utf-8'))
            try:
                url = entry['data']['media']['oembed']['url']+'"'
            except:
                url = entry['data']['url']+'"'
            matchYoutube = re.compile('youtube.com/watch\\?v=(.+?)"', re.DOTALL).findall(url)
            matchVimeo = re.compile('vimeo.com/(.+?)"', re.DOTALL).findall(url)
            matchDailyMotion = re.compile('dailymotion.com/video/(.+?)_', re.DOTALL).findall(url)
            matchDailyMotion2 = re.compile('dailymotion.com/.+?video=(.+?)', re.DOTALL).findall(url)
            matchLiveLeak = re.compile('liveleak.com/view\\?i=(.+?)"', re.DOTALL).findall(url)
            url = ""
            if matchYoutube:
                url = getYoutubeUrl(matchYoutube[0])
            elif matchVimeo:
                url = getVimeoUrl(matchVimeo[0].replace("#", "").split("?")[0])
            elif matchDailyMotion:
                url = getDailyMotionUrl(matchDailyMotion[0])
            elif matchDailyMotion2:
                url = getDailyMotionUrl(matchDailyMotion2[0])
            elif matchLiveLeak:
                url = getLiveLeakUrl(matchLiveLeak[0])
            if url:
                url = "plugin://plugin.video.reddit_tv/?url="+urllib.quote_plus(url)+"&mode=playVideo"
                if playUnwatched:
                    if getPlayCount(url) < 0:
                        entries.append([title, url])
                else:
                    entries.append([title, url])
        except:
            pass
    random.shuffle(entries)
    for title, url in entries:
        listitem = xbmcgui.ListItem(title)
        playlist.add(url, listitem)


def playSlideshow():
    if type=="new":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQueryImages+"&sort=new&restrict_sr=on&limit=100"
    elif type=="hot":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQueryImages+"&sort=hot&restrict_sr=on&limit=100&t=day"
    elif type=="top":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQueryImages+"&sort=top&restrict_sr=on&limit=100&t=week"
    elif type=="comments":
        url = urlMain+"/r/"+subreddit+"/search.json?q="+hosterQueryImages+"&sort=comments&restrict_sr=on&limit=100&t=day"
    xbmc.executebuiltin("SlideShow(plugin://plugin.image.reddit_com/?mode=listImages&type="+subreddit+"&url="+urllib.quote_plus(url)+", random)")


def cleanTitle(title):
        title = title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"")
        return title.strip()


def getYoutubeUrl(id):
    if xbox:
        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id
    return url


def getVimeoUrl(id):
    if xbox:
        url = "plugin://video/Vimeo/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.vimeo/?path=/root/video&action=play_video&videoid=" + id
    return url


def getDailyMotionUrl(id):
    if xbox:
        url = "plugin://video/DailyMotion.com/?url=" + id + "&mode=playVideo"
    else:
        url = "plugin://plugin.video.dailymotion_com/?url=" + id + "&mode=playVideo"
    return url


def getLiveLeakUrl(id):
    if xbox:
        url = "plugin://video/Reddit.com/?url=" + id + "&mode=playLiveLeakVideo"
    else:
        url = "plugin://plugin.video.reddit_tv/?url=" + id + "&mode=playLiveLeakVideo"
    return url


dbPath = getDbPath()
if dbPath:
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()

param = ""
if len(sys.argv)>1:
    param = urllib.unquote_plus(sys.argv[1])
if param=="tv_mode":
    try:
        addVideos()
    except:
        pass
    if playlist:
        xbmc.Player().play(playlist)
    else:
        xbmc.executebuiltin('XBMC.Notification(Video Screensaver:,'+translation(30005)+'!,5000)')
elif not xbmc.Player().isPlayingAudio() or content=="image":
    myWindow.doModal()

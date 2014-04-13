#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import urllib2
import re
import os
import random
import time


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

    def onAction(self, action):
        ACTION_STOP = 13
        ACTION_PREVIOUS_MENU = 10
        if action in [ACTION_PREVIOUS_MENU, ACTION_STOP]:
            myPlayer.stop()

addon = xbmcaddon.Addon()
translation = addon.getLocalizedString
addonID = "script.screensaver.apple_itunes_trailer"
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
cacheFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cache")
exitDelay = int(addon.getSetting("exitDelay"))
jumpBack = int(addon.getSetting("jumpBack"))
setVolume = addon.getSetting("setVolume") == "true"
volume = int(addon.getSetting("volume"))
currentVolume = xbmc.getInfoLabel("Player.Volume")
currentVolume = int((float(currentVolume.split(" ")[0])+60.0)/60.0*100.0)
g_action = addon.getSetting("g_action") == "true"
g_comedy = addon.getSetting("g_comedy") == "true"
g_docu = addon.getSetting("g_docu") == "true"
g_drama = addon.getSetting("g_drama") == "true"
g_family = addon.getSetting("g_family") == "true"
g_fantasy = addon.getSetting("g_fantasy") == "true"
g_foreign = addon.getSetting("g_foreign") == "true"
g_horror = addon.getSetting("g_horror") == "true"
g_musical = addon.getSetting("g_musical") == "true"
g_romance = addon.getSetting("g_romance") == "true"
g_scifi = addon.getSetting("g_scifi") == "true"
g_thriller = addon.getSetting("g_thriller") == "true"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'iTunes')]
urlMain = "http://trailers.apple.com"
myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
myPlayer = XBMCPlayer()
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
playlist.clear()
playbackInterrupted = False
currentUrl = ""
currentPosition = 0
cacheLifetime = 24
if not os.path.isdir(addonUserDataFolder):
  os.mkdir(addonUserDataFolder)
if xbmc.Player().isPlayingVideo():
    currentUrl = xbmc.Player().getPlayingFile()
    currentPosition = xbmc.Player().getTime()
    xbmc.Player().stop()
    xbmc.sleep(1000)
    playbackInterrupted = True

def muted():
    return xbmc.getCondVisibility("Player.Muted")


def genreCheck(genres):
    passed = True
    if not g_action:
        if "Action and Adventure" in genres:
            passed = False
    if not g_comedy:
        if "Comedy" in genres:
            passed = False
    if not g_docu:
        if "Documentary" in genres:
            passed = False
    if not g_drama:
        if "Drama" in genres:
            passed = False
    if not g_family:
        if "Family" in genres:
            passed = False
    if not g_fantasy:
        if "Fantasy" in genres:
            passed = False
    if not g_foreign:
        if "Foreign" in genres:
            passed = False
    if not g_horror:
        if "Horror" in genres:
            passed = False
    if not g_musical:
        if "Musical" in genres:
            passed = False
    if not g_romance:
        if "Romance" in genres:
            passed = False
    if not g_scifi:
        if "Science Fiction" in genres:
            passed = False
    if not g_thriller:
        if "Thriller" in genres:
            passed = False
    return passed


def addVideos():
    entries = []
    if os.path.exists(cacheFile) and (time.time()-os.path.getmtime(cacheFile) < cacheLifetime*24*60):
        fh = open(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open(urlMain+"/trailers/home/feeds/studios.json").read()
        fh = open(cacheFile, 'w')
        fh.write(content)
        fh.close()
    spl = content.split('"title"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('"(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        match = re.compile('"genre":(.+?),', re.DOTALL).findall(entry)
        genres = match[0]
        match = re.compile('"poster":"(.+?)"', re.DOTALL).findall(entry)
        thumb = urlMain+match[0].replace("poster.jpg", "poster-xlarge.jpg")
        match = re.compile('"url":"(.+?)","type":"(.+?)"', re.DOTALL).findall(entry)
        for url, type in match:
            urlTemp = urlMain+url+"includes/"+type.replace('-', '').replace(' ', '').lower()+"/extralarge.html"
            url = "plugin://script.screensaver.apple_itunes_trailer/?url="+urllib.quote_plus(urlTemp)
            filter = ["- JP Sub","- UK","- BR Sub","- FR","- IT","- AU","- MX","- MX Sub","- BR","- RU","- DE","- ES","- FR Sub","- KR Sub","- Russian","- French","- Spanish","- German","- Latin American Spanish","- Italian"]
            filtered = False
            for f in filter:
                if f in type:
                    filtered = True
            if genreCheck(genres) and not filtered:
                entries.append([title+" - "+type, url, thumb])
    random.shuffle(entries)
    for title, url, thumb in entries:
        listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
        playlist.add(url, listitem)

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
elif not xbmc.Player().isPlayingAudio():
    myWindow.doModal()

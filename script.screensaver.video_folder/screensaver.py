#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib
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
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))) or addon.getSetting("videoDir") == "":
    addon.openSettings()

jumpBack = int(addon.getSetting("jumpBack"))
exitDelay = int(addon.getSetting("exitDelay"))
videoDir = addon.getSetting("videoDir")
setVolume = addon.getSetting("setVolume") == "true"
volume = int(addon.getSetting("volume"))
currentVolume = xbmc.getInfoLabel("Player.Volume")
currentVolume = int((float(currentVolume.split(" ")[0])+60.0)/60.0*100.0)
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

def addVideos():
    entries = []
    fileTypes = ('.mkv', '.avi', '.mp4', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ts', '.m2ts', '.m4v', '.m2v', '.rm', '.3gp', '.asf', '.asx', '.amv', '.divx', '.pls', '.strm', '.m3u', '.mp3', '.aac', '.flac', '.ogg', '.wma', '.wav')
    if videoDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')):
        dirs, files = xbmcvfs.listdir(videoDir)
        for file in files:
            if file.lower().endswith(fileTypes):
                entries.append(os.path.join(videoDir, file))
        for dir in dirs:
            dirs2, files = xbmcvfs.listdir(os.path.join(videoDir, dir))
            for file in files:
                if file.lower().endswith(fileTypes):
                    entries.append(os.path.join(videoDir, os.path.join(dir, file)))
    else:
        for root, dirs, files in os.walk(videoDir):
            for filename in files:
                if filename.lower().endswith(fileTypes):
                    entries.append(os.path.join(root, filename))
    random.shuffle(entries)
    for file in entries:
        playlist.add(file)


param = ""
if len(sys.argv) > 1:
    param = urllib.unquote_plus(sys.argv[1])
if param == "tv_mode":
    addVideos()
    if playlist:
        xbmc.Player().play(playlist)
    else:
        xbmc.executebuiltin('XBMC.Notification(Video Screensaver:,'+translation(30005)+'!,5000)')
elif not xbmc.Player().isPlayingAudio():
    myWindow.doModal()

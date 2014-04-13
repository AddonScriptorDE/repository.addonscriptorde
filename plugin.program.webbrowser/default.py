#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import subprocess
import xbmcplugin
import xbmcaddon
import xbmcgui

pluginhandle = int(sys.argv[1])
addonID = 'plugin.program.webbrowser'
addon = xbmcaddon.Addon(id=addonID)
translation = addon.getLocalizedString
isWin = xbmc.getCondVisibility('system.platform.windows')
userDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
browserPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/XBMC_WebBrowser/XBMC_WebBrowser.exe')
keyMapperPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/XBMC_WebBrowser/XBMC_WebBrowser_KeyMapper.exe')
siteFolder = os.path.join(userDataFolder, 'sites')
shortCutsFolder = os.path.join(userDataFolder, 'shortcuts')
minMouseSpeed = addon.getSetting("minimumMouseSpeed")
maxMouseSpeed = addon.getSetting("maximumMouseSpeed")
useCustomCursor = addon.getSetting("useCustomCursor")
customCursorSize = addon.getSetting("customCursorSize")
magnifierSize = addon.getSetting("magnifierSize")
scrollSpeed = addon.getSetting("scrollSpeed")

if not os.path.isdir(userDataFolder):
    os.mkdir(userDataFolder)
if not os.path.isdir(siteFolder):
    os.mkdir(siteFolder)


def index():
    files = os.listdir(siteFolder)
    for file in files:
        if file.endswith(".link"):
          fh = open(os.path.join(siteFolder, file), 'r')
          title = ""
          url = ""
          thumb = ""
          zoom = ""
          stopPlayback = "yes"
          showPopups = "no"
          showScrollbar = "yes"
          hideCursor = "no"
          userAgent = ""
          for line in fh.readlines():
              entry = line[:line.find("=")]
              content = line[line.find("=")+1:]
              if entry == "title":
                  title = content.strip()
              elif entry == "url":
                  url = content.strip()
              elif entry == "thumb":
                  thumb = content.strip()
              elif entry == "zoom":
                  zoom = content.strip()
              elif entry == "stopPlayback":
                  stopPlayback = content.strip()
              elif entry == "showPopups":
                  showPopups = content.strip()
              elif entry == "showScrollbar":
                  showScrollbar = content.strip()
              elif entry == "hideCursor":
                  hideCursor = content.strip()
              elif entry == "userAgent":
                  userAgent = content.strip()
          fh.close()
          addSiteDir(title, url, 'showSite', thumb, zoom, stopPlayback, showPopups, showScrollbar, userAgent, hideCursor)
    addDir("- "+translation(30001), "", 'addSite', "")
    addDir("- "+translation(30005), "", 'mapKeys', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def addSite():
    keyboard = xbmc.Keyboard('', translation(30003))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        title = keyboard.getText()
        keyboard = xbmc.Keyboard('http://', translation(30004))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            url = keyboard.getText()
            content = "title="+title+"\nurl="+url+"\nthumb=DefaultFolder.png\nzoom=100\nstopPlayback=yes\nshowPopups=no"
            fh = open(os.path.join(siteFolder, title+".link"), 'w')
            fh.write(content)
            fh.close()
    xbmc.executebuiltin("Container.Refresh")


def showSite(url, title, zoom, stopPlayback, showPopups, showScrollbar, userAgent, hideCursor):
    path = browserPath+' "'+userDataFolder+'" "'+title+'" '+urllib.quote_plus(url)+' '+zoom+' '+showPopups+' '+minMouseSpeed+' '+maxMouseSpeed+' '+magnifierSize+' '+useCustomCursor+' '+customCursorSize+' '+showScrollbar+' '+scrollSpeed+' '+hideCursor+' "'+userAgent+'"'
    if isWin:
        subprocess.Popen(path, shell=False)
    else:
        subprocess.Popen("wine "+path, shell=True)
    if stopPlayback == "yes":
        xbmc.Player().stop()


def removeSite(title):
    os.remove(os.path.join(siteFolder, title+".link"))
    xbmc.executebuiltin("Container.Refresh")


def editSite(title):
    file = os.path.join(siteFolder, title+".link")
    fh = open(file, 'r')
    title = ""
    url = ""
    thumb = "DefaultFolder.png"
    zoom = "100"
    stopPlayback = "yes"
    showPopups = "no"
    showScrollbar = "yes"
    hideCursor = "no"
    userAgent = ""
    for line in fh.readlines():
        entry = line[:line.find("=")]
        content = line[line.find("=")+1:]
        if entry == "title":
            title = content.strip()
        elif entry == "url":
            url = content.strip()
        elif entry == "thumb":
            thumb = content.strip()
        elif entry == "zoom":
            zoom = content.strip()
        elif entry == "stopPlayback":
            stopPlayback = content.strip()
        elif entry == "showPopups":
            showPopups = content.strip()
        elif entry == "showScrollbar":
            showScrollbar = content.strip()
        elif entry == "hideCursor":
            hideCursor = content.strip()
        elif entry == "userAgent":
            userAgent = content.strip()
    fh.close()
    
    oldTitle = title
    keyboard = xbmc.Keyboard(title, translation(30003))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        title = keyboard.getText()
        keyboard = xbmc.Keyboard(url, translation(30004))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            url = keyboard.getText()
            keyboard = xbmc.Keyboard(zoom, translation(30008))
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                zoom = keyboard.getText()
                keyboard = xbmc.Keyboard(stopPlayback, translation(30009))
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    stopPlayback = keyboard.getText()
                    keyboard = xbmc.Keyboard(showPopups, translation(30010))
                    keyboard.doModal()
                    if keyboard.isConfirmed() and keyboard.getText():
                        showPopups = keyboard.getText()
                        keyboard = xbmc.Keyboard(showScrollbar, translation(30011))
                        keyboard.doModal()
                        if keyboard.isConfirmed() and keyboard.getText():
                            showScrollbar = keyboard.getText()
                            if userAgent:
                              content = "title="+title+"\nurl="+url+"\nthumb="+thumb+"\nzoom="+zoom+"\nstopPlayback="+stopPlayback+"\nshowPopups="+showPopups+"\nshowScrollbar="+showScrollbar+"\nhideCursor="+hideCursor+"\nuserAgent="+userAgent
                            else:
                              content = "title="+title+"\nurl="+url+"\nthumb="+thumb+"\nzoom="+zoom+"\nstopPlayback="+stopPlayback+"\nshowPopups="+showPopups+"\nshowScrollbar="+showScrollbar+"\nhideCursor="+hideCursor
                            fh = open(os.path.join(siteFolder, title+".link"), 'w')
                            fh.write(content)
                            fh.close()
                            file = os.path.join(shortCutsFolder, oldTitle+".links")
                            fileNew = os.path.join(shortCutsFolder, title+".links")
                            if title!=oldTitle:
                              os.remove(os.path.join(siteFolder, oldTitle+".link"))
                            if os.path.exists(file):
                              os.rename(file, fileNew)
    xbmc.executebuiltin("Container.Refresh")


def mapKeys():
    if isWin:
        subprocess.Popen(keyMapperPath+' "'+userDataFolder+'"', shell=False)
    else:
        subprocess.Popen("wine "+keyMapperPath+' "'+userDataFolder+'"', shell=True)


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addSiteDir(name, url, mode, iconimage, zoom, stopPlayback, showPopups, showScrollbar, userAgent, hideCursor):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&name="+urllib.quote_plus(name)+"&zoom="+urllib.quote_plus(zoom)+"&stopPlayback="+urllib.quote_plus(stopPlayback)+"&showPopups="+urllib.quote_plus(showPopups)+"&showScrollbar="+urllib.quote_plus(showScrollbar)+"&hideCursor="+urllib.quote_plus(hideCursor)+"&userAgent="+urllib.quote_plus(userAgent)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=editSite&url='+urllib.quote_plus(name)+')',), (translation(30002), 'RunPlugin(plugin://'+addonID+'/?mode=removeSite&url='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
name = urllib.unquote_plus(params.get('name', ''))
url = urllib.unquote_plus(params.get('url', ''))
zoom = urllib.unquote_plus(params.get('zoom', '100'))
stopPlayback = urllib.unquote_plus(params.get('stopPlayback', 'no'))
showPopups = urllib.unquote_plus(params.get('showPopups', 'no'))
showScrollbar = urllib.unquote_plus(params.get('showScrollbar', 'yes'))
hideCursor = urllib.unquote_plus(params.get('hideCursor', 'no'))
userAgent = urllib.unquote_plus(params.get('userAgent', ''))

if mode == 'addSite':
    addSite()
elif mode == 'showSite':
    showSite(url, name, zoom, stopPlayback, showPopups, showScrollbar, userAgent, hideCursor)
elif mode == 'removeSite':
    removeSite(url)
elif mode == 'editSite':
    editSite(url)
elif mode == 'mapKeys':
    mapKeys()
else:
    index()

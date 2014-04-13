#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import json
import random
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.kinderkino_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]
apiUrl = "http://kostenlos-dyn.kinderkino.de/api/get_category_posts/?id=3&page=0&count=500&order_by=date&thumbnail_size=full&include=title,slug,thumbnail,custom_fields&custom_fields=Streaming,FSK,Jahr,IMDb-Bewertung,Highlight,Regisseur,Duration"


def index():
    addDir(translation(30001), "", 'listMovies', icon)
    addDir(translation(30002), "", 'listShows', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listMovies():
    xbmcplugin.setContent(pluginhandle, "movies")
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(apiUrl).read()
    content = json.loads(content)
    for item in content['posts']:
        title = cleanTitle(item['title'].encode('utf-8'))
        thumb = item['thumbnail']
        videoID = item['custom_fields']['Streaming'][0].encode('utf-8')
        try:
            duration = item['custom_fields']['Duration'][0].encode('utf-8')
            duration = str(int(float(duration)/60))
        except:
            duration = ""
        if "Folge" not in title and "Philipp die Maus -" not in title and "Superman -" not in title and "Ozeane dieser Welt -" not in title and "Wir Schildbürger -" not in title:
            addLink(title, videoID, 'playVideo', thumb, duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows():
    xbmcplugin.setContent(pluginhandle, "movies")
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(apiUrl).read()
    content = json.loads(content)
    titles = []
    entries = []
    for item in content['posts']:
        title = cleanTitle(item['title'].encode('utf-8'))
        if "Folge" in title or "Philipp die Maus -" in title or "Superman -" in title or "Ozeane dieser Welt -" in title or "Wir Schildbürger -" in title:
            if ' - ' in title:
                title = title[:title.find(' - ')]
            thumb = item['thumbnail']
            videoID = item['custom_fields']['Streaming'][0].encode('utf-8')
            try:
                duration = item['custom_fields']['Duration'][0].encode('utf-8')
                duration = str(int(float(duration)/60))
            except:
                duration = ""
            if title not in titles:
                titles.append(title)
                entries.append([title, videoID, thumb, duration])
    for title, videoID, thumb, duration in entries:
        addDir(title, title, 'listEpisodes', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listEpisodes(seriesTitle):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(apiUrl).read()
    content = json.loads(content)
    titles = []
    entries = []
    for item in content['posts']:
        title = cleanTitle(item['title'].encode('utf-8'))
        if seriesTitle in title:
            thumb = item['thumbnail']
            videoID = item['custom_fields']['Streaming'][0].encode('utf-8')
            try:
                duration = item['custom_fields']['Duration'][0].encode('utf-8')
                duration = str(int(float(duration)/60))
            except:
                duration = ""
            addLink(title, videoID, 'playVideo', thumb, duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(videoID):
    finalUrl = "rtmp://fms.edge.newmedia.nacamar.net/loadtv_vod/ playpath=mp4:kinderkino-kostenlos/"+videoID
    listitem = xbmcgui.ListItem(path=finalUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&#8211;", "-").replace("&#8230;", "…").replace("&#038;", "&")
    title = title.strip()
    return title


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


def addLink(name, url, mode, iconimage, duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    #liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listMovies':
    listMovies()
elif mode == 'listShows':
    listShows()
elif mode == 'listEpisodes':
    listEpisodes(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()

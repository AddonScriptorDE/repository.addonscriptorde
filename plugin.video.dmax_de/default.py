#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import os
import urllib
import urllib2
import httplib
import cookielib
import socket
import xbmcgui
import xbmcaddon
import xbmcplugin
from pyamf import remoting

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.dmax_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
translation = addon.getLocalizedString
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
userDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
forceViewMode = addon.getSetting("forceView") == "true"
autoPlay = addon.getSetting("autoPlay") == "true"
viewMode = str(addon.getSetting("viewID"))
maxBitRate = addon.getSetting("maxBitRate")
qual = [512000, 1024000, 1536000, 2048000, 2560000, 3072000]
maxBitRate = qual[int(maxBitRate)]
baseUrl = "http://www.dmax.de"
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0"
opener.addheaders = [('User-Agent', userAgent)]

if not os.path.isdir(userDataFolder):
    os.mkdir(userDataFolder)


def index():
    addDir(translation(30002), "", 'listAZ', icon, '')
    addDir(translation(30010), "", 'listShowsFavs', icon, '')
    addDir(translation(30003), "NEUESTE VIDEOS", 'listVideosLatest', icon, '')
    addDir(translation(30007), "CLIPS", 'listVideosLatest', icon, '')
    addDir(translation(30004), "BELIEBTE VIDEOS", 'listVideosLatest', icon, '')
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosMain(url, thumb):
    content = opener.open(url).read()
    matchShowID = re.compile('id="dni_listing_post_id" value="(.+?)"', re.DOTALL).findall(content)
    matchFE = re.compile('<h2>GANZE FOLGEN</h2>.+?id="listing-container-(.+?)"', re.DOTALL).findall(content)
    matchMV = re.compile('<h2>MEIST GESEHEN</h2>.+?id="listing-container-(.+?)"', re.DOTALL).findall(content)
    matchClips = re.compile('<h2>CLIPS</h2>.+?id="listing-container-(.+?)"', re.DOTALL).findall(content)
    matchEpisodes = re.compile('<a href="(.+?)"><span>(.+?)<', re.DOTALL).findall(content)
    showID = matchShowID[0]
    if matchFE:
        for url, title in matchEpisodes:
            if title=="Episoden":
                addDir(translation(30006), url, 'listSeasons', thumb, "")
                break
        addDir(translation(30008), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id="+matchFE[0]+"&post_id="+showID, 'listVideos', thumb, "")
    if matchMV:
        addDir(translation(30005), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id="+matchMV[0]+"&post_id="+showID, 'listVideos', thumb, "")
    if matchClips:
        addDir(translation(30007), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id="+matchClips[0]+"&post_id="+showID, 'listVideos', thumb, "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(urlMain):
    content = opener.open(urlMain).read()
    content = content.replace("\\", "")
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        if title.endswith("Teil 1"):
            title = title[:title.rfind("Teil 1")]
        if title.endswith(" 1") and not title.endswith("Episode 1"):
            title = title[:title.rfind(" 1")]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addDir(title, url, 'playVideo', thumb, title)
    try:
        matchCurrent = re.compile('"current_page":"(.+?)",', re.DOTALL).findall(content)
        matchTotal = re.compile('"total_pages":(.+?),', re.DOTALL).findall(content)
        currentPage = matchCurrent[0]
        nextPage = str(int(currentPage)+1)
        totalPages = matchTotal[0]
        if int(currentPage) < int(totalPages):
            addDir(translation(30001)+" ("+nextPage+")", urlMain.replace("page="+currentPage, "page="+nextPage), 'listVideos', icon, "")
    except:
        pass
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosLatest(type):
    content = opener.open(baseUrl+"/videos/").read()
    content = content[content.find('<div class="tab-module-header">'+type+'</div>'):]
    content = content[:content.find('</section>	</div>')]
    spl = content.split('<section class="pagetype-video">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        if title.endswith("Teil 1"):
            title = title[:title.rfind("Teil 1")]
        if title.endswith(" 1") and not title.endswith("Episode 1"):
            title = title[:title.rfind(" 1")]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addDir(title, url, 'playVideo', thumb, title)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listAZ():
    letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
    for letter in letters:
        url = baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter="+letter.upper()+"&page=1&id=1b0&post_id=2178"
        addDir(letter.upper(), url, 'listShows', icon, "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows(urlMain):
    content = opener.open(urlMain).read()
    content = content.replace("\\", "")
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        if title.endswith("Teil 1"):
            title = title[:title.rfind("Teil 1")]
        if title.endswith(" 1") and not title.endswith("Episode 1"):
            title = title[:title.rfind(" 1")]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addShowDir(title, url, 'listVideosMain', thumb, title)
    try:
        matchCurrent = re.compile('"current_page":"(.+?)",', re.DOTALL).findall(content)
        matchTotal = re.compile('"total_pages":(.+?),', re.DOTALL).findall(content)
        currentPage = matchCurrent[0]
        nextPage = str(int(currentPage)+1)
        totalPages = matchTotal[0]
        if int(currentPage) < int(totalPages):
            addDir(translation(30001)+" ("+nextPage+")", urlMain.replace("page="+currentPage, "page="+nextPage), 'listShows', icon, "")
    except:
        pass
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsFavs():
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
            addShowRDir(title, urllib.unquote_plus(url), "listVideosMain", thumb, title)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listSeasons(urlMain, thumb):
    content = opener.open(urlMain).read()
    matchIDs = re.compile('data-module-id="cfct-module-(.+?)" data-post-id="(.+?)"', re.DOTALL).findall(content)
    if '<select name="season"' in content:
        content = content[content.find('<select name="season"'):]
        content = content[:content.find('</select>')]
        matchSeasons = re.compile('<option value="(.+?)">(.+?)</option>', re.DOTALL).findall(content)
        for seasonID, title in matchSeasons:
            url = baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_episode_browser_get_season&post="+matchIDs[0][1]+"&module=cfct-module-"+matchIDs[0][0]+"&season="+seasonID
            addDir(title.replace("Season", "Staffel"), url, 'listEpisodes', thumb, "")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode:
            xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')
    else:
        listEpisodes(urlMain)


def listEpisodes(url):
    content = opener.open(url).read()
    spl = content.split('<a class="dni-episode-browser-item pagetype-video"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match1 = re.compile('<h3 class="item-title">(.+?)<', re.DOTALL).findall(entry)
        match2 = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        if match1:
            title = match1[0]
        elif match2:
            title = match2[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        if title.endswith("Teil 1"):
            title = title[:title.rfind("Teil 1")]
        if title.endswith(" 1") and not title.endswith("Episode 1"):
            title = title[:title.rfind(" 1")]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('<p>(.+?)</p>', re.DOTALL).findall(entry)
        desc = ""
        if match:
            desc = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addDir(title, url, 'playVideo', thumb, title, desc)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url, title, thumb):
    content = opener.open(url).read()
    matchMulti = re.compile('<li data-number="(.+?)" data-guid="(.+?)"', re.DOTALL).findall(content)
    matchSingle = re.compile('&playlist=(.+?)"', re.DOTALL).findall(content)
    if matchMulti:
        addDir(title+": Alle Teile", url, "playVideoAll", thumb, title)
        for part, videoID in matchMulti:
            addLink(title+": Teil "+part, videoID, "playBrightCoveStream", thumb, title, "no")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode:
            xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')
    elif matchSingle:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playBrightCoveStream(matchSingle[0], title, thumb, "yes")


def playVideoAll(url, title, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open(url).read()
    matchMulti = re.compile('<li data-number="(.+?)" data-guid="(.+?)"', re.DOTALL).findall(content)
    for part, videoID in matchMulti:
        listitem = xbmcgui.ListItem(title+": Teil "+part, thumbnailImage=thumb)
        if xbox:
            pluginUrl = "plugin://video/DMAX.de/?url="+videoID+"&mode=playBrightCoveStream&isSingle=no&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(thumb)
        else:
            pluginUrl = "plugin://plugin.video.dmax_de/?url="+videoID+"&mode=playBrightCoveStream&isSingle=no&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(thumb)
        playlist.add(pluginUrl, listitem)
    if playlist:
        xbmc.Player().play(playlist)


def playBrightCoveStream(bc_videoID, title, thumb, isSingle):
    bc_playerID = 586587148001
    bc_publisherID = 1659832546
    bc_const = "ef59d16acbb13614346264dfe58844284718fb7b"
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = remoting.Envelope(amfVersion=3)
    envelope.bodies.append(("/1", remoting.Request(target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", body=[bc_const, bc_playerID, bc_videoID, bc_publisherID], envelope=envelope)))
    conn.request("POST", "/services/messagebroker/amf?playerId=" + str(bc_playerID), str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    streamUrl = ""
    for item in sorted(response['renditions'], key=lambda item: item['encodingRate'], reverse=False):
        encRate = item['encodingRate']
        if encRate < maxBitRate:
            streamUrl = item['defaultURL']
    if not streamUrl:
        streamUrl = response['FLVFullLengthURL']
    if streamUrl:
        if isSingle:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            xbmc.Player().play(streamUrl, listitem)
        else:
            listitem = xbmcgui.ListItem(title, path=streamUrl, thumbnailImage=thumb)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if autoPlay:
            while True:
                if xbmc.Player().isPlaying() and xbmc.getCondVisibility("Player.Paused"):
                    xbmc.Player().pause()
                    break
                xbmc.sleep(100)
            xbmc.sleep(500)
            while xbmc.getCondVisibility("Player.Paused"):
                if xbmc.Player().isPlaying():
                    xbmc.Player().pause()
                    break
                xbmc.sleep(100)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


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
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace("u00c4", "Ä").replace("u00e4", "ä").replace("u00d6", "Ö").replace("u00f6", "ö").replace("u00dc", "Ü").replace("u00fc", "ü").replace("u00df", "ß").replace("u2013", "–")
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


def addLink(name, url, mode, iconimage, title, isSingle="no", desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&isSingle="+str(isSingle)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30009), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&title='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, title, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, title, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30011), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowRDir(name, url, mode, iconimage, title, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(title)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
isSingle = urllib.unquote_plus(params.get('isSingle', 'yes'))
thumb = urllib.unquote_plus(params.get('thumb', ''))
title = urllib.unquote_plus(params.get('title', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosLatest':
    listVideosLatest(url)
elif mode == 'listVideosMain':
    listVideosMain(url, thumb)
elif mode == 'listAZ':
    listAZ()
elif mode == 'listShows':
    listShows(url)
elif mode == 'listSeasons':
    listSeasons(url, thumb)
elif mode == 'listEpisodes':
    listEpisodes(url)
elif mode == 'playVideo':
    playVideo(url, title, thumb)
elif mode == 'queueVideo':
    queueVideo(url, title, thumb)
elif mode == 'playVideoAll':
    playVideoAll(url, title, thumb)
elif mode == 'playBrightCoveStream':
    playBrightCoveStream(url, title, thumb, isSingle == "yes")
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'favs':
    favs(url)
else:
    index()

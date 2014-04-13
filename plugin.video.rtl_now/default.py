#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import urllib
import urllib2
import xbmcplugin
import xbmcaddon
import xbmcgui
import random
import sys
import os
import re

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.rtl_now'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
addonUserDataFolder = xbmc.translatePath(addon.getAddonInfo('profile'))
channelFavsFile = os.path.join(addonUserDataFolder, addonID+".favorites")
iconRTL = os.path.join(addonDir, 'iconRTL.png')
iconRTL2 = os.path.join(addonDir, 'iconRTL2.png')
iconVOX = os.path.join(addonDir, 'iconVOX.png')
iconRTLNitro = os.path.join(addonDir, 'iconRTLNitro.png')
iconSuperRTL = os.path.join(addonDir, 'iconSuperRTL.png')
iconNTV = os.path.join(addonDir, 'iconNTV.png')
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:24.0) Gecko/20100101 Firefox/24.0"
opener.addheaders = [('User-Agent', userAgent)]
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
forceViewMode = addon.getSetting("forceView") == "true"
viewMode = str(addon.getSetting("viewID"))
site1 = addon.getSetting("site1") == "true"
site2 = addon.getSetting("site2") == "true"
site3 = addon.getSetting("site3") == "true"
site4 = addon.getSetting("site4") == "true"
site5 = addon.getSetting("site5") == "true"
site6 = addon.getSetting("site6") == "true"
urlMainRTL = "http://rtl-now.rtl.de"
urlMainRTL2 = "http://rtl2now.rtl2.de"
urlMainVOX = "http://www.voxnow.de"
urlMainRTLNitro = "http://www.rtlnitronow.de"
urlMainSuperRTL = "http://www.superrtlnow.de"
urlMainNTV = "http://www.n-tvnow.de"

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)


def index():
    addDir(translation(30023), "", 'listShowsFavs', '', '')
    if site1:
        addDir(translation(30002), urlMainRTL, "listChannel", iconRTL)
    if site2:
        addDir(translation(30003), urlMainRTL2, "listChannel", iconRTL2)
    if site3:
        addDir(translation(30004), urlMainVOX, "listChannel", iconVOX)
    if site4:
        addDir(translation(30005), urlMainRTLNitro, "listChannel", iconRTLNitro)
    if site5:
        addDir(translation(30006), urlMainSuperRTL, "listChannel", iconSuperRTL)
    if site6:
        addDir(translation(30007), urlMainNTV, "listChannel", iconNTV)
    xbmcplugin.endOfDirectory(pluginhandle)


def listChannel(urlMain, thumb):
    addDir(translation(30018), urlMain, "listVideosNew", thumb, "", "newlist")
    addDir(translation(30017), urlMain, "listVideosNew", thumb, "", "tipplist")
    addDir(translation(30019), urlMain, "listVideosNew", thumb, "", "top10list")
    addDir(translation(30020), urlMain, "listVideosNew", thumb, "", "topfloplist")
    if urlMain == urlMainRTL:
        addDir(translation(30016), urlMain+"/newsuebersicht.php", "listShowsThumb", thumb)
        addDir(translation(30015), urlMain+"/sendung_a_z.php", "listShowsThumb", thumb)
    elif urlMain in [urlMainVOX, urlMainNTV, urlMainRTLNitro]:
        addDir(translation(30014), urlMain+"/sendung_a_z.php", "listShowsThumb", thumb)
    else:
        addDir(translation(30014), urlMain, "listShowsNoThumb", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsThumb(urlMain):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain).read()
    spl = content.split('<div class="m03medium"')
    entries = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<h2>(.+?)</h2>', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        if url.startswith("http"):
            pass
        else:
            if url.startswith("/"):
                url = url[1:]
            if "/" in url:
                url = url[:url.find("/")]+".php"
            url = urlMain[:urlMain.rfind("/")+1]+url
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("/216x122/", "/864x488/")
        if 'class="m03date">FREE' in entry or 'class="m03date">NEW' in entry:
            if url not in entries:
                if url.endswith("gzsz.php"):
                    addShowDir(title, url, 'listSeasons', thumb)
                else:
                    addShowDir(title, url, 'listVideos', thumb)
                entries.append(url)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsNoThumb(urlMain, thumb):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain).read()
    spl = content.split('<div class="seriennavi')
    entries = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        if match:
            title = cleanTitle(match[0]).replace(" online ansehen", "")
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = urlMain+match[0]
            if '>FREE<' in entry or '>NEW<' in entry:
                if url not in entries:
                    addShowDir(title, url, 'listVideos', thumb)
                    entries.append(url)
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
            if url.endswith("gzsz.php"):
                addShowRDir(title, urllib.unquote_plus(url), "listSeasons", thumb)
            else:
                addShowRDir(title, urllib.unquote_plus(url), "listVideos", thumb)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listSeasons(urlMain, thumb):
    content = opener.open(urlMain).read()
    matchUrl = re.compile('xajaxRequestUri="(.+?)"', re.DOTALL).findall(content)
    ajaxUrl = matchUrl[0]
    matchParams = re.compile("<select onchange=\"xajax_show_top_and_movies.+?'(.+?)','(.+?)','(.+?)','(.+?)','(.+?)','(.+?)','(.+?)'", re.DOTALL).findall(content)
    if matchParams:
        match = re.compile("<div id=\"reiter.+?,'(.+?)','(.+?)'.+?<div class=\"m\">(.+?)<", re.DOTALL).findall(content)
        for id1, id2, title in match:
            args = "xajax=show_top_and_movies&xajaxr=&xajaxargs[]=0&xajaxargs[]="+id1+"&xajaxargs[]="+id2+"&xajaxargs[]="+matchParams[0][2]+"&xajaxargs[]="+matchParams[0][3]+"&xajaxargs[]="+matchParams[0][4]+"&xajaxargs[]="+matchParams[0][5]+"&xajaxargs[]="+matchParams[0][6]
            addDir(title, ajaxUrl, 'listVideos', thumb, args)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(urlMain, thumb, args=""):
    ajaxUrl = ""
    if not args:
        content = opener.open(urlMain).read()
        match = re.compile('<meta property="og:image" content="(.+?)"', re.DOTALL).findall(content)
        if match and thumb.split(os.sep)[-1].startswith("icon"):
            thumb = match[0]
        matchUrl = re.compile('xajaxRequestUri="(.+?)"', re.DOTALL).findall(content)
        ajaxUrl = matchUrl[0]
        matchParams = re.compile("<select onchange=\"xajax_show_top_and_movies.+?'(.+?)','(.+?)','(.+?)','(.+?)','(.+?)','(.+?)','(.+?)'", re.DOTALL).findall(content)
        if matchParams:
            args = "xajax=show_top_and_movies&xajaxr=&xajaxargs[]=0&xajaxargs[]="+matchParams[0][0]+"&xajaxargs[]="+matchParams[0][1]+"&xajaxargs[]="+matchParams[0][2]+"&xajaxargs[]="+matchParams[0][3]+"&xajaxargs[]="+matchParams[0][4]+"&xajaxargs[]="+matchParams[0][5]+"&xajaxargs[]="+matchParams[0][6]
            content = opener.open(ajaxUrl, args).read()
    else:
        content = opener.open(urlMain, args).read()
    spl = content.split('<div class="line')
    count = 0
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if 'class="minibutton">kostenlos<' in entry:
            match = re.compile('title=".+?">(.+?)<', re.DOTALL).findall(entry)
            if match:
                title = cleanTitle(match[0])
                match = re.compile('class="time"><div style=".+?">.+?</div>(.+?)<', re.DOTALL).findall(entry)
                date = ""
                if match:
                    date = match[0].strip()
                    if " " in date:
                        date = date.split(" ")[0]
                    if "." in date:
                        date = date[:date.rfind(".")]
                    title = date+" - "+title
                match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
                url = urlMain[:urlMain.rfind("/")]+match[0].replace("&amp;", "&")
                addLink(title, url, 'playVideo', thumb)
                count+=1
    matchParams = re.compile("<a class=\"sel\"  >.+?xajax_show_top_and_movies\\((.+?),'(.+?)','(.+?)','(.+?)','(.+?)','(.+?)','(.+?)','(.+?)'", re.DOTALL).findall(content)
    if matchParams and count==20:
        args = "xajax=show_top_and_movies&xajaxr=&xajaxargs[]="+matchParams[0][0]+"&xajaxargs[]="+matchParams[0][1]+"&xajaxargs[]="+matchParams[0][2]+"&xajaxargs[]="+matchParams[0][3]+"&xajaxargs[]="+matchParams[0][4]+"&xajaxargs[]="+matchParams[0][5]+"&xajaxargs[]="+matchParams[0][6]+"&xajaxargs[]="+matchParams[0][7]
        if ajaxUrl:
            ajaxUrlNext = ajaxUrl
        else:
            ajaxUrlNext = urlMain
        addDir(translation(30001), ajaxUrlNext, "listVideos", thumb, args)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosNew(urlMain, type):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain).read()
    content = content[content.find('<div id="'+type+'"'):]
    if type == "tipplist":
        if urlMain == urlMainNTV:
            content = content[:content.find("iv class=\"contentrow contentrow3\"><div class='contentrow_headline'")]
        else:
            content = content[:content.find("<div class='contentrow_headline'")]
        spl = content.split('<div class="m03medium"')
    else:
        content = content[:content.find('<div class="roundfooter"></div>')]
        spl = content.split('<div class="top10 ')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match1 = re.compile('<h2>(.+?)</h2>', re.DOTALL).findall(entry)
        match2 = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        if match1:
            title = cleanTitle(match1[0])
        elif match2:
            title = cleanTitle(match2[0])
        title = title.replace("<br>", ": ")
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0].replace("&amp;", "&")
        if not urlMain in url:
            url = urlMain+url
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("/216x122/", "/864x488/")
        if 'class="m03date">FREE' in entry or 'FREE |' in entry:
            addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(urlMain):
    content = opener.open(urlMain).read()
    if "<div>DAS TUT UNS LEID!</div>" in content:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30022))+',10000)')
    else:
        match = re.compile("data:'(.+?)'", re.DOTALL).findall(content)
        hosterURL = urlMain[urlMain.find("//")+2:]
        hosterURL = hosterURL[:hosterURL.find("/")]
        url = "http://"+hosterURL+urllib.unquote(match[0])
        content = opener.open(url).read()
        match = re.compile('<filename.+?><(.+?)>', re.DOTALL).findall(content)
        url = match[0].replace("![CDATA[", "")
        matchRTMPE = re.compile('rtmpe://(.+?)/(.+?)/(.+?)]', re.DOTALL).findall(url)
        matchHDS = re.compile('http://(.+?)/(.+?)/(.+?)/(.+?)/(.+?)\\?', re.DOTALL).findall(url)
        finalUrl = ""
        if matchRTMPE:
            playpath = matchRTMPE[0][2]
            if ".flv" in playpath:
                playpath = playpath[:playpath.rfind('.')]
            else:
                playpath = "mp4:"+playpath
            finalUrl = "rtmpe://"+matchRTMPE[0][0]+"/"+matchRTMPE[0][1]+"/ playpath="+playpath+" swfVfy=1 swfUrl=http://"+hosterURL+"/includes/vodplayer.swf app="+matchRTMPE[0][1]+"/_definst_ tcUrl=rtmpe://"+matchRTMPE[0][0]+"/"+matchRTMPE[0][1]+"/ pageUrl="+urlMain
        elif matchHDS:
            finalUrl = "rtmpe://fms-fra"+str(random.randint(1, 34))+".rtl.de/"+matchHDS[0][2]+"/ playpath=mp4:"+matchHDS[0][4].replace(".f4m", "")+" swfVfy=1 swfUrl=http://"+hosterURL+"/includes/vodplayer.swf app="+matchHDS[0][2]+"/_definst_ tcUrl=rtmpe://fms-fra"+str(random.randint(1, 34))+".rtl.de/"+matchHDS[0][2]+"/ pageUrl="+urlMain
        if finalUrl:
            listitem = xbmcgui.ListItem(path=finalUrl)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


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
    title = title.replace("u0026", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace("\\'", "'").strip()
    return title


def getPluginUrl():
    if xbox:
        return "plugin://video/"+addon.getAddonInfo('name')
    else:
        return "plugin://"+addonID


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc="", duration="", date=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Aired": date, "Duration": duration, "Episode": 1})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and not iconimage.split(os.sep)[-1].startswith("icon"):
        liz.setProperty("fanart_image", iconimage)
    entries = []
    entries.append((translation(30021), 'RunPlugin('+getPluginUrl()+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, args="", type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&args="+urllib.quote_plus(args)+"&type="+urllib.quote_plus(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and not iconimage.split(os.sep)[-1].startswith("icon"):
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, args="", type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&args="+urllib.quote_plus(args)+"&type="+urllib.quote_plus(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and not iconimage.split(os.sep)[-1].startswith("icon"):
        liz.setProperty("fanart_image", iconimage)
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30024), 'RunPlugin('+getPluginUrl()+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowRDir(name, url, mode, iconimage, args="", type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&args="+urllib.quote_plus(args)+"&type="+urllib.quote_plus(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and not iconimage.split(os.sep)[-1].startswith("icon"):
        liz.setProperty("fanart_image", iconimage)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30025), 'RunPlugin('+getPluginUrl()+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
args = urllib.unquote_plus(params.get('args', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
type = urllib.unquote_plus(params.get('type', ''))

if mode == 'listChannel':
    listChannel(url, thumb)
elif mode == 'listVideos':
    listVideos(url, thumb, args)
elif mode == 'listSeasons':
    listSeasons(url, thumb)
elif mode == 'listVideosNew':
    listVideosNew(url, type)
elif mode == 'listShowsThumb':
    listShowsThumb(url)
elif mode == 'listShowsNoThumb':
    listShowsNoThumb(url, thumb)
elif mode == 'playVideo':
    playVideo(url)
elif mode == "queueVideo":
    queueVideo(url, name)
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'favs':
    favs(url)
else:
    index()

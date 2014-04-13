#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcplugin
import xbmcaddon
import xbmcgui
import sys
import re
import os

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.ardmediathek_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
showSubtitles = addon.getSetting("showSubtitles") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewIDVideos"))
viewModeShows = str(addon.getSetting("viewIDShows"))
baseUrl = "http://www.ardmediathek.de"
defaultThumb = baseUrl+"/ard/static/pics/default/16_9/default_webM_16_9.jpg"
defaultBackground = "http://www.ard.de/pool/img/ard/background/base_xl.jpg"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
addon_work_folder = xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
subFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/sub.srt")

if not os.path.isdir(addon_work_folder):
    os.mkdir(addon_work_folder)


def index():
    addDir(translation(30011), "", 'listShowsFavs', "")
    addDir(translation(30001), baseUrl+"/ard/servlet/ajax-cache/3516220/view=switch/index.html", 'listVideos', "")
    addDir(translation(30002), baseUrl+"/ard/servlet/ajax-cache/3516210/view=list/show=recent/index.html", 'listVideos', "")
    addDir(translation(30010), baseUrl+"/ard/servlet/ajax-cache/3516188/view=switch/index.html", 'listVideos', "")
    addDir(translation(30014), "", 'listEinsLike', "")
    addDir(translation(30003), baseUrl+"/ard/servlet/ajax-cache/3474718/view=switch/index.html", 'listVideos', "")
    addDir(translation(30004), baseUrl+"/ard/servlet/ajax-cache/4585472/view=switch/index.html", 'listVideos', "")
    addDir(translation(30005), "", 'listShowsAZMain', "")
    addDir(translation(30006), "", 'listCats', "")
    addDir(translation(30007), "", 'listDossiers', "")
    addDir(translation(30008), "", 'search', "")
    addLink(translation(30013), "", 'playLive', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


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
            addShowFavDir(title, urllib.unquote_plus(url), "listShowVideos", thumb)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')


def listEinsLike():
    addDir(translation(30001), baseUrl+"/ard/servlet/ajax-cache/14844072/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30002), baseUrl+"/ard/servlet/ajax-cache/3516192/view=list/vflags=0-1,5-1/show=recent/index.html", 'listVideos', "")
    addDir(translation(30010), baseUrl+"/ard/servlet/ajax-cache/3516156/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30015), baseUrl+"/ard/servlet/ajax-cache/14844028/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30016), baseUrl+"/ard/servlet/ajax-cache/14844030/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30017), baseUrl+"/ard/servlet/ajax-cache/14844032/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30018), baseUrl+"/ard/servlet/ajax-cache/14844034/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30019), baseUrl+"/ard/servlet/ajax-cache/14844036/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listDossiers():
    content = getUrl(baseUrl+"/ard/servlet/ajax-cache/3516154/view=switch/index.html")
    spl = content.split('<div class="mt-media_item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<a href="(.+?)"', re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        id = url[url.find("documentId=")+11:]
        url = baseUrl+"/ard/servlet/ajax-cache/3517004/view=list/documentId="+id+"/goto=1/index.html"
        match = re.compile('<span class="mt-icon mt-icon-toggle_arrows"></span>(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = getBetterThumb(baseUrl+match[0])
        addDir(title, url, 'listVideosDossier', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowVideos(url):
    content = getUrl(url)
    spl = content.split('<div class="mt-media_item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "mt-icon_video" in entry:
            match = re.compile('<a href="(.+?)" class="mt-fo_source" rel="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
            url = baseUrl+match[0][0]
            title = cleanTitle(match[0][2])
            match = re.compile('<span class="mt-airtime">(.+?) (.+?) min</span>', re.DOTALL).findall(entry)
            match2 = re.compile('<span class="mt-airtime">(.+?)</span>', re.DOTALL).findall(entry)
            duration = ""
            date = ""
            if match:
                date = match[0][0]
                duration = match[0][1]
                title = date[:5]+" - "+title
                if "00:" in duration:
                    duration = 1
            elif match2:
                date = match2[0]
                duration = 1
                title = date[:5]+" - "+title
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = getBetterThumb(baseUrl+match[0])
            if "Livestream" not in title:
                addLink(title, url, 'playVideo', thumb, duration)
    match = re.compile('<a  href="(.+?)" rel=".+?"\n         class=".+?">(.+?)</a>', re.DOTALL).findall(content)
    for url, title in match:
        if title == "Weiter":
            addDir(translation(30009), baseUrl+url, 'listShowVideos', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsAZMain():
    addDir("0-9", "0-9", 'listShowsAZ', "")
    letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
    for letter in letters:
        addDir(letter.upper(), letter.upper(), 'listShowsAZ', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsAZ(letter):
    content = getUrl(baseUrl+"/ard/servlet/ajax-cache/3474820/view=list/initial="+letter+"/index.html")
    spl = content.split('<div class="mt-media_item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<a href="(.+?)" class="mt-fo_source" rel="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
        url = baseUrl+match[0][0]
        id = url[url.find("documentId=")+11:]
        url = baseUrl+"/ard/servlet/ajax-cache/3516962/view=list/documentId="+id+"/goto=1/index.html"
        title = cleanTitle(match[0][2])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = getBetterThumb(baseUrl+match[0])
        addShowDir(title, url, 'listShowVideos', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewModeShows+')')

def getBetterThumb(url):
    if baseUrl+"/ard/static/pics/default/16_9/default" in url:
        url = defaultThumb
    if "/scaled/" in url:
        url = url.replace("/scaled/","/contentblob/").replace("-bild-xs16x9","/bild/1")
    elif "/contentblob/" in url:
        customIDs = {12660422:10159866, 13076654:13076650, 13927884:10160114, 13250800:9717382}
        match = re.compile('/contentblob/.+?/.+?/.+?/.+?/(.+?)/', re.DOTALL).findall(url)
        id = int(match[0])
        if id in customIDs:
            id = customIDs[id]
        elif id>=15000000:
            id = id-2
        elif id>=12292408:
            id = id+2
        elif id>=10159892:
            id = id+6
        elif id>=10000000:
            id = id+4
        if id>=10000000:
            id = str(id)
            url = baseUrl+"/ard/servlet/contentblob/"+id[0:2]+"/"+id[2:4]+"/"+id[4:6]+"/"+id[6:8]+"/"+id+"/bild/1"
        else:
            newID = str(id*10)
            id = str(id)
            url = baseUrl+"/ard/servlet/contentblob/"+newID[0:2]+"/"+newID[2:4]+"/"+newID[4:6]+"/"+newID[6:8]+"/"+id+"/bild/1"
    return url
    

def listCats():
    content = getUrl(baseUrl)
    content = content[content.find('<div class="mt-reset mt-categories">'):]
    content = content[:content.find('</div>')]
    match = re.compile('<li><a href="(.+?)" title="">(.+?)</a></li>', re.DOTALL).findall(content)
    for url, title in match:
        id = url[url.find("documentId=")+11:]
        addDir(cleanTitle(title), id, 'listVideosMain', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosMain(id):
    addDir(translation(30001), baseUrl+"/ard/servlet/ajax-cache/3516698/view=switch/clipFilter=fernsehen/documentId="+id+"/index.html", 'listVideos', "")
    addDir(translation(30002), baseUrl+"/ard/servlet/ajax-cache/3516700/view=list/clipFilter=fernsehen/documentId="+id+"/show=recent/index.html", 'listVideos', "")
    addDir(translation(30010), baseUrl+"/ard/servlet/ajax-cache/3516702/view=switch/clipFilter=fernsehen/documentId="+id+"/index.html", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(url):
    content = getUrl(url)
    spl = content.split('<div class="mt-media_item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "mt-icon_video" in entry:
            match = re.compile('<a href="(.+?)" class="mt-fo_source" rel="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
            url = baseUrl+match[0][0]
            title = cleanTitle(match[0][2])
            match = re.compile('<p class="mt-source mt-tile-view_hide">aus: (.+?)</p>', re.DOTALL).findall(entry)
            show = ""
            if match:
                show = cleanTitle(match[0])
                title = show+": "+title
            match = re.compile('<span class="mt-channel mt-tile-view_hide">(.+?)</span>', re.DOTALL).findall(entry)
            channel = ""
            if match:
                channel = match[0]
            match = re.compile('<span class="mt-airtime">(.+?) (.+?) min</span>', re.DOTALL).findall(entry)
            match2 = re.compile('<span class="mt-airtime">(.+?)</span>', re.DOTALL).findall(entry)
            duration = ""
            date = ""
            if match:
                date = match[0][0]
                duration = match[0][1]
                title = date[:5]+" - "+title
                if "00:" in duration:
                    duration = 1
            elif match2:
                date = match2[0]
                duration = 1
                title = date[:5]+" - "+title
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = getBetterThumb(baseUrl+match[0])
            desc = cleanTitle(title+" ("+channel+")")
            if "Livestream" not in title:
                addLink(title, url, 'playVideo', thumb, duration, desc)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosDossier(url):
    content = getUrl(url)
    spl = content.split('<div class="mt-media_item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if 'class="mt-fo_source"' in entry:
            match = re.compile('<a href="(.+?)" class="mt-fo_source" rel="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
            url = baseUrl+match[0][0]
            title = cleanTitle(match[0][2])
            match = re.compile('<p class="mt-source mt-tile-view_hide">aus: (.+?)</p>', re.DOTALL).findall(entry)
            show = ""
            if match:
                show = match[0]
            match = re.compile('<span class="mt-channel mt-tile-view_hide">(.+?)</span>', re.DOTALL).findall(entry)
            channel = ""
            if match:
                channel = match[0]
            match = re.compile('<span class="mt-airtime">(.+?) (.+?) min</span>', re.DOTALL).findall(entry)
            match2 = re.compile('<span class="mt-airtime">(.+?)</span>', re.DOTALL).findall(entry)
            duration = ""
            date = ""
            if match:
                date = match[0][0]
                duration = match[0][1]
                title = date[:5]+" - "+title
                if "00:" in duration:
                    duration = 1
            elif match2:
                date = match2[0]
                duration = 1
                title = date[:5]+" - "+title
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = getBetterThumb(baseUrl+match[0])
            desc = cleanTitle(date+" - "+show+" ("+channel+")")
            if "Livestream" not in title:
                addLink(title, url, 'playVideo', thumb, duration, desc)
    match = re.compile('<a  href="(.+?)" rel=".+?"\n         class=".+?">(.+?)</a>', re.DOTALL).findall(content)
    for url, title in match:
        if title == "Weiter":
            addDir(translation(30009), baseUrl+url, 'listVideosDossier', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = getUrl(url)
    matchFSK = re.compile('<div class="fsk">(.+?)</div>', re.DOTALL).findall(content)
    if matchFSK:
        fsk = matchFSK[0].strip()
        xbmc.executebuiltin('XBMC.Notification(Info:,'+fsk+',15000)')
    else:
        match5 = re.compile('addMediaStream\\(1, 2, "", "(.+?)"', re.DOTALL).findall(content)
        match6 = re.compile('addMediaStream\\(1, 1, "", "(.+?)"', re.DOTALL).findall(content)
        match1 = re.compile('addMediaStream\\(0, 2, "(.+?)", "(.+?)"', re.DOTALL).findall(content)
        match2 = re.compile('addMediaStream\\(0, 2, "", "(.+?)"', re.DOTALL).findall(content)
        match3 = re.compile('addMediaStream\\(0, 1, "(.+?)", "(.+?)"', re.DOTALL).findall(content)
        match4 = re.compile('addMediaStream\\(0, 1, "", "(.+?)"', re.DOTALL).findall(content)
        matchUT = re.compile('setSubtitleUrl\\("(.+?)"', re.DOTALL).findall(content)
        url = ""
        if match5:
            url = match5[0]
        elif match6:
            url = match6[0]
        elif match2:
            url = match2[0]
        elif match1:
            base = match1[0][0]
            if not base.endswith("/"):
                base = base+"/"
            url = base+" playpath="+cleanUrl(match1[0][1])
        elif match4:
            url = match4[0]
        elif match3:
            base = match3[0][0]
            if not base.endswith("/"):
                base = base+"/"
            url = base+" playpath="+cleanUrl(match3[0][1])
        if url:
            if "?" in url:
                url = url[:url.find("?")]
            listitem = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
            if showSubtitles and matchUT:
                setSubtitle(baseUrl+matchUT[0])


def setSubtitle(url):
    if os.path.exists(subFile):
        os.remove(subFile)
    try:
        content = getUrl(url)
    except:
        content = ""
    if content:
        matchLine = re.compile('<p id=".+?" begin="1(.+?)" end="1(.+?)".+?>(.+?)</p>', re.DOTALL).findall(content)
        fh = open(subFile, 'a')
        count = 1
        for begin, end, line in matchLine:
            begin = "0"+begin.replace(".",",")[:-1]
            end = "0"+end.replace(".",",")[:-1]
            match = re.compile('<span(.+?)>', re.DOTALL).findall(line)
            for span in match:
                line = line.replace("<span"+span+">","")
            line = line.replace("<br />","\n").replace("</span>","").strip()
            fh.write(str(count)+"\n"+begin+" --> "+end+"\n"+cleanTitle(line)+"\n\n")
            count+=1
        fh.close()
        xbmc.sleep(1000)
        xbmc.Player().setSubtitles(subFile)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def playLive():
    content = getUrl("http://live.daserste.de/de/livestream.xml")
    match = re.compile('<streamingUrlIPad>(.+?)</streamingUrlIPad>', re.DOTALL).findall(content)
    url = ""
    if match:
        url = match[0]
    if url:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def search():
    keyboard = xbmc.Keyboard('', translation(30008))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listVideosSearch(baseUrl+"/suche?detail=40&sort=r&s="+search_string+"&inhalt=tv&goto=1")


def listVideosSearch(url):
    content = getUrl(url)
    spl = content.split('<div class="mt-media_item mt-media-item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<a href="(.+?)" class="mt-fo_source" rel="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
        url = baseUrl+match[0][0]
        title = cleanTitle(match[0][2])
        match = re.compile('<p class="mt-source mt-tile-view_hide">aus: (.+?)</p>', re.DOTALL).findall(entry)
        show = ""
        if match:
            show = match[0]
        match = re.compile('<span class="mt-channel mt-tile-view_hide">(.+?)</span>', re.DOTALL).findall(entry)
        channel = ""
        if match:
            channel = match[0]
        match = re.compile('<span class="mt-airtime">(.+?) (.+?) min</span>', re.DOTALL).findall(entry)
        match2 = re.compile('<span class="mt-airtime">(.+?)</span>', re.DOTALL).findall(entry)
        duration = ""
        date = ""
        if match:
            date = match[0][0]
            duration = match[0][1]
            title = date[:5]+" - "+title
            if "00:" in duration:
                duration = 1
        elif match2:
            date = match2[0]
            duration = 1
            title = date[:5]+" - "+title
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = getBetterThumb(baseUrl+match[0])
        desc = cleanTitle(date+" - "+show+" ("+channel+")")
        if "Livestream" not in title:
            addLink(title, url, 'playVideo', thumb, duration, desc)
    match = re.compile('href="(.+?)".+?>(.+?)<', re.DOTALL).findall(content)
    for url, title in match:
        if title == "Weiter":
            addDir(translation(30009), baseUrl+url.replace("&amp;", "&"), 'listVideosSearch', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode == True:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#034;", "\"").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&eacute;", "é").replace("&egrave;", "è")
    title = title.replace("&#x00c4;","Ä").replace("&#x00e4;","ä").replace("&#x00d6;","Ö").replace("&#x00f6;","ö").replace("&#x00dc;","Ü").replace("&#x00fc;","ü").replace("&#x00df;","ß")
    title = title.replace("&apos;","'").strip()
    return title


def cleanUrl(title):
    return title.replace(" ", "%20").replace("%F6", "ö").replace("%FC", "ü").replace("%E4", "ä").replace("%26", "&").replace("%C4", "Ä").replace("%D6", "Ö").replace("%DC", "Ü")


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


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


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, duration="", desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration, "Plot": desc})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart:
        if not iconimage or iconimage==icon or iconimage==defaultThumb:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart:
        if not iconimage or iconimage==icon or iconimage==defaultThumb:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart:
        if not iconimage or iconimage==icon or iconimage==defaultThumb:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30028), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowFavDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart:
        if not iconimage or iconimage==icon or iconimage==defaultThumb:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30029), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'listChannel':
    listChannel(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosMain':
    listVideosMain(url)
elif mode == 'listDossiers':
    listDossiers()
elif mode == 'listEinsLike':
    listEinsLike()
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'listVideosDossier':
    listVideosDossier(url)
elif mode == 'listVideosSearch':
    listVideosSearch(url)
elif mode == 'listShowsAZMain':
    listShowsAZMain()
elif mode == 'listShowsAZ':
    listShowsAZ(url)
elif mode == 'listCats':
    listCats()
elif mode == 'listShowVideos':
    listShowVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == "queueVideo":
    queueVideo(url, name)
elif mode == 'playLive':
    playLive()
elif mode == 'search':
    search()
elif mode == 'favs':
    favs(url)
else:
    index()

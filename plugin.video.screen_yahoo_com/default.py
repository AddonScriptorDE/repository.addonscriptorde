#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import urllib
import urllib2
import cookielib
import xbmcplugin
import xbmcaddon
import xbmcgui
import json
import sys
import os
import re

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.screen_yahoo_com'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(60)
pluginhandle = int(sys.argv[1])
cj = cookielib.MozillaCookieJar()
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
cookieFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cookies")
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0"
opener.addheaders = [('User-agent', userAgent)]

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))):
    addon.openSettings()
if os.path.exists(cookieFile):
    cj.load(cookieFile)

useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
forceView = addon.getSetting("forceView") == "true"
viewID = str(addon.getSetting("viewIDNew"))
site1 = addon.getSetting("site1") == "true"
site2 = addon.getSetting("site2") == "true"
site3 = addon.getSetting("site3") == "true"
site4 = addon.getSetting("site4") == "true"
site5 = addon.getSetting("site5") == "true"
site6 = addon.getSetting("site6") == "true"
site7 = addon.getSetting("site7") == "true"
site8 = addon.getSetting("site8") == "true"
site9 = addon.getSetting("site9") == "true"
site10 = addon.getSetting("site10") == "true"
site11 = addon.getSetting("site11") == "true"
maxVideoQuality = addon.getSetting("maxVideoQuality")
maxVideoQuality = [1096, 1628, 3192, 4192][int(maxVideoQuality)]
itemsPerPage = addon.getSetting("itemsPerPage")
itemsPerPage = ["25", "50", "75", "100"][int(itemsPerPage)]
urlMainUS = "http://screen.yahoo.com"
urlMainUK = "http://uk.screen.yahoo.com"
urlMainDE = "http://de.screen.yahoo.com"
urlMainIN = "http://in.screen.yahoo.com"
urlMainCA = "http://ca.screen.yahoo.com"
urlMainIT = "http://it.screen.yahoo.com"
urlMainES = "http://es.screen.yahoo.com"
urlMainMX = "http://mx.screen.yahoo.com"
urlMainBR = "http://br.screen.yahoo.com"
urlMainFR = "http://fr.screen.yahoo.com"
urlMainESUS = "http://es-us.screen.yahoo.com"


def index():
    if site1:
        addDir(translation(30003), urlMainUS, "listChannelsUS", icon, "en-US")
    if site2:
        addDir(translation(30004), urlMainUK, "listChannels", icon, "en-GB")
    if site3:
        addDir(translation(30005), urlMainDE, "listChannels", icon, "de-DE")
    if site4:
        addDir(translation(30006), urlMainCA, "listChannels", icon, "en-CA")
    if site5:
        addDir(translation(30007), urlMainFR, "listChannels", icon, "fr-FR")
    if site6:
        addDir(translation(30008), urlMainIT, "listChannels", icon, "it-IT")
    if site7:
        addDir(translation(30009), urlMainMX, "listChannels", icon, "es-MX")
    if site8:
        addDir(translation(30010), urlMainIN, "listChannels", icon, "en-IN")
    if site9:
        addDir(translation(30011), urlMainBR, "listChannels", icon, "pt-BR")
    if site10:
        addDir(translation(30012), urlMainES, "listChannels", icon, "es-ES")
    if site11:
        addDir(translation(30013), urlMainESUS, "listChannels", icon, "es-US")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listChannelsUS(urlMain, language):
    addDir("Search", urlMain, "search", "", language)
    content = opener.open(urlMainUS).read()
    match = re.compile('root.App.Cache.data.channels = (.+?);', re.DOTALL).findall(content)
    content = json.loads(match[0])
    for item in content['items']:
        title = item["name"]
        id = item["url_alias"]
        url = urlMainUS+"/ajax/resource/channel/id/"+id+";count="+itemsPerPage+";start=0"
        addChannelDir(title, url, 'listVideosUS', '', language)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listChannels(urlMain, language):
    if urlMain==urlMainDE:
        addDir("Alle Sendungen", urlMainDE+"/shows-a-z/", 'listShowsDE', '', language)
    addDir("Search", urlMain, "search", "", language)
    content = opener.open(urlMain).read()
    cj.save(cookieFile)
    match = re.compile('<li class="navitem.*?"><a href="(.+?)".+?<span>(.+?)</span>', re.DOTALL).findall(content)
    notWorkingUrls = ["http://de.screen.yahoo.com/shows-a-z/", "http://de.screen.yahoo.com/comedians/", "http://de.screen.yahoo.com/serien/", "http://de.screen.yahoo.com/bbc-dokus/", "http://in.screen.yahoo.com/explore"]
    for url, title in match:
        if urlMain not in url:
            url = urlMain+url
        if url not in notWorkingUrls:
            addChannelDir(cleanTitle(title), url, 'listVideosMain', '', language)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listVideosMain(urlMain, language):
    content = opener.open(urlMain).read()
    cj.save(cookieFile)
    content2 = content[:content.find('<div class="CAN_ad">')]
    matchTitles = re.compile('class="yom-mod yom-bcarousel ymg-carousel rapid-nf" id="(.+?)">.+?<h3>(.+?)</h3>', re.DOTALL).findall(content2)
    if len(matchTitles) == 0:
        match = re.compile('"modId":".+?".+?content_id=(.+?)&', re.DOTALL).findall(content)
        match2 = re.compile('"modId":".+?".+?list_id=(.+?)&', re.DOTALL).findall(content)
        url = ""
        if match:
            url = urlMain[:urlMain.find(".screen")]+".screen.yahoo.com/_xhr/carousel/bcarousel-mixed-collection/?content_id="+match[0]+"&thumb_ratio=16x9&pyoff=0&title_lines_max=2&show_cite=&show_date=&show_provider=&show_author=&show_duration=&show_subtitle=&show_provider_links=&apply_filter=&filters=%255B%255D&template=tile&num_cols=5&num_rows=10&start_initial=1&max_items=48&pages_per_batch=2&sec=&module=MediaBCarouselMixedLPCA&spaceid=&mod_units=16&renderer_key=&start=0"
        elif match2:
            url = urlMain[:urlMain.find(".screen")]+".screen.yahoo.com/_xhr/carousel/bcarousel-mixed-list/?list_id="+match2[0]+"&thumb_ratio=16x9&pyoff=0&title_lines_max=2&show_cite=&show_date=&show_provider=&show_author=&show_duration=&show_subtitle=&show_provider_links=&apply_filter=&filters=%255B%255D&template=tile&num_cols=5&num_rows=10&start_initial=1&max_items=48&pages_per_batch=2&sec=&module=MediaBCarouselMixedLPCA&spaceid=&mod_units=16&renderer_key=&start=0"
        if url:
            listVideos(url, language)
    if len(matchTitles) == 1:
        match = re.compile('"modId":"'+matchTitles[0][0]+'".+?content_id=(.+?)&', re.DOTALL).findall(content)
        match2 = re.compile('"modId":"'+matchTitles[0][0]+'".+?list_id=(.+?)&', re.DOTALL).findall(content)
        url = ""
        if match:
            url = urlMain[:urlMain.find(".screen")]+".screen.yahoo.com/_xhr/carousel/bcarousel-mixed-collection/?content_id="+match[0]+"&thumb_ratio=16x9&pyoff=0&title_lines_max=2&show_cite=&show_date=&show_provider=&show_author=&show_duration=&show_subtitle=&show_provider_links=&apply_filter=&filters=%255B%255D&template=tile&num_cols=5&num_rows=10&start_initial=1&max_items=48&pages_per_batch=2&sec=&module=MediaBCarouselMixedLPCA&spaceid=&mod_units=16&renderer_key=&start=0"
        elif match2:
            url = urlMain[:urlMain.find(".screen")]+".screen.yahoo.com/_xhr/carousel/bcarousel-mixed-list/?list_id="+match2[0]+"&thumb_ratio=16x9&pyoff=0&title_lines_max=2&show_cite=&show_date=&show_provider=&show_author=&show_duration=&show_subtitle=&show_provider_links=&apply_filter=&filters=%255B%255D&template=tile&num_cols=5&num_rows=10&start_initial=1&max_items=48&pages_per_batch=2&sec=&module=MediaBCarouselMixedLPCA&spaceid=&mod_units=16&renderer_key=&start=0"
        if url:
            listVideos(url, language)
    elif len(matchTitles) > 1:
        for id, title in matchTitles:
            try:
                if "<a href" in title:
                    title = title[title.find(">")+1:]
                    title = title[:title.find("<")]
                match = re.compile('"modId":"'+id+'".+?content_id=(.+?)&', re.DOTALL).findall(content)
                match2 = re.compile('"modId":"'+id+'".+?list_id=(.+?)&', re.DOTALL).findall(content)
                url = ""
                if match:
                    url = urlMain[:urlMain.find(".screen")]+".screen.yahoo.com/_xhr/carousel/bcarousel-mixed-collection/?content_id="+match[0]+"&thumb_ratio=16x9&pyoff=0&title_lines_max=2&show_cite=&show_date=&show_provider=&show_author=&show_duration=&show_subtitle=&show_provider_links=&apply_filter=&filters=%255B%255D&template=tile&num_cols=5&num_rows=10&start_initial=1&max_items=48&pages_per_batch=2&sec=&module=MediaBCarouselMixedLPCA&spaceid=&mod_units=16&renderer_key=&start=0"
                elif match2:
                    url = urlMain[:urlMain.find(".screen")]+".screen.yahoo.com/_xhr/carousel/bcarousel-mixed-list/?list_id="+match2[0]+"&thumb_ratio=16x9&pyoff=0&title_lines_max=2&show_cite=&show_date=&show_provider=&show_author=&show_duration=&show_subtitle=&show_provider_links=&apply_filter=&filters=%255B%255D&template=tile&num_cols=5&num_rows=10&start_initial=1&max_items=48&pages_per_batch=2&sec=&module=MediaBCarouselMixedLPCA&spaceid=&mod_units=16&renderer_key=&start=0"
                if url and "VEVO" not in title:
                    addDir(cleanTitle(title), url, 'listVideos', "", language)
            except:
                pass
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listVideos(urlMain, language):
    content = opener.open(urlMain).read()
    if not '<li class="bcarousel-item"' in content:
        content = opener.open(urlMain).read()
    spl = content.split('<li class="bcarousel-item"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('data-id="(.+?)"', re.DOTALL).findall(entry)
        id = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        thumb = thumb[thumb.rfind('http'):]
        if "icon-play-small" in entry:
            addLink(title, id, 'playVideo', thumb, language)
        else:
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            addDir(title, match[0], 'listVideosMain', thumb, language)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listVideosUS(url, language):
    xbmcplugin.setContent(pluginhandle, "episodes")
    content = opener.open(url).read()
    content = json.loads(content)
    for video in content['videos']:
        title = video['title'].encode('utf-8')
        desc = video['description'].encode('utf-8')
        date = video['provider_publish_time']
        date = date[:date.find('T')]
        duration = video['duration']
        views = str(video['view_count'])
        desc = views+" Views\n"+desc
        id = video['id']
        thumb = video['thumbnails'][0]['url']
        addLink(title, id, 'playVideo', thumb, language, desc, duration, date)
    if len(content['videos']) == 50:
        currentIndex = url[url.rfind("=")+1:]
        nextIndex = str(int(currentIndex)+int(itemsPerPage))
        nextUrl = url[:url.rfind("=")+1]+nextIndex
        addDir(translation(30001), nextUrl, 'listVideosUS', "", language)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listShowsDE(urlMain, language):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain).read()
    content = content[content.find('<div class="yom-mod yom-heading-generic"'):]
    content = content[:content.find('<div class="yom-mod yom-scrollflow"')]
    match = re.compile('<a href="(.+?)"><span>(.+?)<', re.DOTALL).findall(content)
    for url, title in match:
        addDir(title, url, 'listVideosMain', "", language)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def listSearchVideos(url, language):
    content = opener.open(url).read()
    if '"results":[]' in content:
        content = opener.open(url).read()
    content = content.replace("\u003C", "<").replace("\u003E", ">").replace("\u0022", "\"").replace("\u0027", "'").replace("\ufffd", "").replace("\\", "").replace("/r", "")
    spl = content.split('<a href')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('data-rurl="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('<span class="note dur">(.+?)</span>', re.DOTALL).findall(entry)
        duration = match[0]
        if duration.startswith("00:"):
            duration = 1
        match = re.compile('"d":"(.+?)"', re.DOTALL).findall(entry)
        desc = cleanTitle(match[0]).replace("<b>", "").replace("</b>", "")
        match = re.compile('<s class="splay"></s></span>(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addSearchLink(title, url, 'playVideoSearch', thumb, language, desc, duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewID+')')


def search(urlMain, language):
    keyboard = xbmc.Keyboard('', translation(30002))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "%23")
        listSearchVideos(urlMain.replace("screen.yahoo.com", "video.search.yahoo.com")+"/search/?fr=screen&o=js&p="+search_string, language)


def playVideo(id, language):
    content = opener.open("http://video.query.yahoo.com/v1/public/yql?q=SELECT%20*%20FROM%20yahoo.media.video.streams%20WHERE%20id%3D%22"+id+"%22%20AND%20format%3D%22mp4%2Cflv%22%20AND%20protocol%3D%22http%22%20AND%20rt%3D%22flash%22%20AND%20plrs%3D%22%22%20AND%20acctid%3D%22%22%20AND%20plidl%3D%22%22%20AND%20pspid%3D%22%22%20AND%20offnetwork%3D%22false%22%20AND%20site%3D%22ivy%22%20AND%20lang%3D%22"+language+"%22%20AND%20region%3D%22"+language.split("-")[1]+"%22%20AND%20override%3D%22none%22%3B&env=prod&format=json").read()
    if '"geo restricted"' in content:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30014))+',5000)')
    else:
        content = json.loads(content)
        url = ""
        for stream in content['query']['results']['mediaObj'][0]['streams']:
            br = stream['bitrate']
            if br <= maxVideoQuality:
                url = stream['host']+stream['path']
        if url:
            listitem = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playVideoSearch(url, language):
    content = opener.open(url).read()
    match = re.compile('root.App.Cache.context.videoCache.curChannel = \\{".+?":"(.+?)"', re.DOTALL).findall(content)
    match2 = re.compile('CONTENT_ID = "(.+?)"', re.DOTALL).findall(content)
    if match:
        playVideo(match[0], language)
    elif match2:
        playVideo(match2[0], language)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def cleanTitle(title):
    title = title.replace("u0026", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace("\\'", "'").strip()
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


def addLink(name, url, mode, iconimage, language="", desc="", duration="", date=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&language="+str(language)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Aired": date, "Episode": 1})
    liz.setProperty('IsPlayable', 'true')
    if duration:
        liz.addStreamInfo('video', {'duration': duration})
    if useThumbAsFanart:
        liz.setProperty("fanart_image", iconimage)
    entries = []
    entries.append((translation(30043), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addSearchLink(name, url, mode, iconimage, language="", desc="", duration="", date=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&language="+str(language)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Aired": date, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    entries = []
    entries.append((translation(30043), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, language=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&language="+str(language)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addChannelDir(name, url, mode, iconimage, language=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&language="+str(language)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addChannelFavDir(name, url, mode, iconimage, language=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&language="+str(language)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
language = urllib.unquote_plus(params.get('language', ''))

if mode == 'listVideosUS':
    listVideosUS(url, language)
elif mode == 'listChannelsUS':
    listChannelsUS(url, language)
elif mode == 'listShowsDE':
    listShowsDE(url, language)
elif mode == 'listChannels':
    listChannels(url, language)
elif mode == 'listVideosMain':
    listVideosMain(url, language)
elif mode == 'listVideos':
    listVideos(url, language)
elif mode == 'listSearchVideos':
    listSearchVideos(url, language)
elif mode == 'playVideo':
    playVideo(url, language)
elif mode == 'playVideoSearch':
    playVideoSearch(url, language)
elif mode == "queueVideo":
    queueVideo(url, name)
elif mode == 'search':
    search(url, language)
else:
    index()

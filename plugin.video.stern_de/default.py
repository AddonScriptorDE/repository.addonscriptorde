#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib,urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,socket
from pyamf import remoting

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.stern_de')
translation = addon.getLocalizedString
forceViewMode=addon.getSetting("forceViewMode")
viewMode=str(addon.getSetting("viewMode"))

def index():
        addDir(translation(30001),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=100&pageNumber=0",'listVideos',"")
        addDir(translation(30002),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=12&pageNumber=0",'listVideos',"")
        addDir(translation(30003),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=13&pageNumber=0",'listVideos',"")
        addDir(translation(30004),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=44&pageNumber=0",'listVideos',"")
        addDir(translation(30005),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=16&pageNumber=0",'listVideos',"")
        addDir(translation(30006),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=15&pageNumber=0",'listVideos',"")
        addDir(translation(30007),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=18&pageNumber=0",'listVideos',"")
        addDir(translation(30008),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=14&pageNumber=0",'listVideos',"")
        addDir(translation(30009),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=17&pageNumber=0",'listVideos',"")
        addDir(translation(30010),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=53&pageNumber=0",'listVideos',"")
        addDir(translation(30011),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=28&pageNumber=0",'listVideos',"")
        addDir(translation(30012),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=33&pageNumber=0",'listVideos',"")
        addDir("WebTV","",'listWebTV',"")
        addDir(translation(30031),"",'search',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listWebTV():
        addDir(translation(30013),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=51&pageNumber=0",'listVideos',"")
        addDir(translation(30014),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=76&pageNumber=0",'listVideos',"")
        addDir(translation(30015),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=48&pageNumber=0",'listVideos',"")
        addDir(translation(30016),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=74&pageNumber=0",'listVideos',"")
        addDir(translation(30017),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=47&pageNumber=0",'listVideos',"")
        addDir(translation(30018),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=24&pageNumber=0",'listVideos',"")
        addDir(translation(30019),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=75&pageNumber=0",'listVideos',"")
        addDir(translation(30020),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=64&pageNumber=0",'listVideos',"")
        addDir(translation(30021),"http://www.stern.de/video-center/?renderer=TeaserListRenderer&playlist=26&pageNumber=0",'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideos(url):
        mainUrl=url
        content = getUrl2(url)
        spl=content.split('<div class="videoItem">')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile("videoItemLink\\('(.+?)'", re.DOTALL).findall(entry)
            id=match[0]
            match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb=match[0]
            match=re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            match=re.compile('<span class="itemHead">(.+?)</span>', re.DOTALL).findall(entry)
            desc=""
            if len(match)>0:
              desc=match[0]
              desc=cleanTitle(desc)
            match=re.compile('<span class="itemInfo">(.+?)</span>', re.DOTALL).findall(entry)
            info=""
            if len(match)>0:
              info=match[0]
            addLink(title+": "+desc,id,'playVideo',thumb,info+"\n"+desc)
        page=0
        match=re.compile('<span id="pagerPageNumber">(.+?)</span>', re.DOTALL).findall(content)
        if len(match)>0:
          page=int(match[0])
        maxPage=-1
        match=re.compile('<span id="pagerTotalCount">(.+?)</span>', re.DOTALL).findall(content)
        if len(match)>0:
          maxPage=int(match[0])
        if page<=maxPage:
          addDir(translation(30030),mainUrl.replace("pageNumber="+str(page-1),"pageNumber="+str(page)),'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def search():
        keyboard = xbmc.Keyboard('', translation(30031))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
          search_string = keyboard.getText().replace(" ","+")
          listVideos("http://www.stern.de/video-center/?renderer=SearchRenderer&videoSearchQuery="+search_string)

def playVideo(id):
        content = getUrl("http://www.stern.de/"+id+".html")
        fh = open("d:\\html.txt", 'w')
        fh.write(id+"\n"+content)
        fh.close()
        match=re.compile('<meta itemprop="contentURL" content="(.+?)"', re.DOTALL).findall(content)
        url=match[0]
        listItem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle,True,listItem)

def playBrightCoveStream(bc_videoID):
        bc_playerID = 597218556001
        bc_publisherID = 1203065853
        bc_const = "ed2f5c980d27173d0baeebab9603cf129b28c933"
        conn = httplib.HTTPConnection("c.brightcove.com")
        envelope = remoting.Envelope(amfVersion=3)
        envelope.bodies.append(("/1", remoting.Request(target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", body=[bc_const, bc_playerID, bc_videoID, bc_publisherID], envelope=envelope)))
        conn.request("POST", "/services/messagebroker/amf?playerId=" + str(bc_playerID), str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
        response = conn.getresponse().read()
        fh = open("d:\\html.txt", 'w')
        fh.write(str(remoting.decode(response)))
        fh.close()
        response = remoting.decode(response).bodies[0][1].body
        streamUrl = ""
        for item in sorted(response['renditions'], key=lambda item:item['encodingRate'], reverse=False):
          encRate = item['encodingRate']
          if encRate < maxBitRate:
            streamUrl = item['defaultURL']
        if streamUrl=="":
          streamUrl=response['FLVFullLengthURL']
        if streamUrl!="":
          url = streamUrl[0:streamUrl.find("&")]
          playpath = streamUrl[streamUrl.find("&")+1:]
          listItem = xbmcgui.ListItem(path=url+' playpath='+playpath)
          xbmcplugin.setResolvedUrl(pluginhandle,True,listItem)

def cleanTitle(title):
        return title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#038;","&").replace("&#39;","'").replace("&#039;","'").replace("&#8211;","-").replace("&#8220;","-").replace("&#8221;","-").replace("&#8217;","'").replace("&quot;","\"").strip()

def getUrl(url):
          req = urllib2.Request(url)
          req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:18.0) Gecko/20100101 Firefox/18.0')
          response = urllib2.urlopen(req)
          link=response.read()
          response.close()
          return link

def getUrl2(url):
          req = urllib2.Request(url)
          req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:18.0) Gecko/20100101 Firefox/18.0')
          req.add_header('X-Requested-With', 'XMLHttpRequest')
          response = urllib2.urlopen(req)
          link=response.read()
          response.close()
          return link

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addLink(name,url,mode,iconimage,desc):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
         
params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listWebTV':
    listWebTV()
elif mode == 'search':
    search()
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playBrightCoveStream':
    playBrightCoveStream(url)
else:
    index()

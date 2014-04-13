#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,os,random

pluginhandle = int(sys.argv[1])

addonID = "plugin.video.mtv_de"
playlistFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".playlists")
artistsFavsFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".artistsFavs")
titlesListFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".titles")
blacklistFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".blacklist")
addon = xbmcaddon.Addon(id=addonID)
translation = addon.getLocalizedString
filterVids=addon.getSetting("filterVids")
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))

def index():
        artistsFavsCount=0
        if os.path.exists(artistsFavsFile):
          fh = open(artistsFavsFile, 'r')
          artistsFavsCount = len(fh.readlines())
          fh.close()
        titlesCount=0
        if os.path.exists(titlesListFile):
          fh = open(titlesListFile, 'r')
          if filterVids=="true": 
            all_lines = fh.readlines()
            titlesCount=0
            for line in all_lines:
              if line.lower().find("all eyes on")==-1 and line.lower().find("interview")==-1:
                titlesCount=titlesCount+1
          else:
            titlesCount = len(fh.readlines())
          fh.close()
        addDir("TV-Shows","http://www.mtv.de/shows/alle",'listShows',"")
        addDir(translation(30007),"http://www.mtv.de/musikvideos",'listVideosLatest',"")
        addDir(translation(30001),"http://www.mtv.de/charts/5-hitlist-germany-top-100",'listVideos',"")
        addDir(translation(30004),"http://www.mtv.de/charts/8-mtv-de-videocharts",'listVideos',"")
        addDir(translation(30003),"http://www.mtv.de/charts/199-top-100-single-jahrescharts-2013",'listVideos',"")
        addDir(str(translation(30009))+" ("+str(artistsFavsCount)+")","ARTISTSFAVS",'artistsFavs',"")
        addTCDir(str(translation(30010))+" ("+str(titlesCount)+")","ARTISTS",'titles',"")
        addDir(translation(30008),"ARTISTS_AZ",'artists',"")
        addDir(translation(30005),"SEARCH_ARTIST",'search',"")
        addDir(translation(30006),"SEARCH_SPECIAL",'search',"")
        addDir(translation(30011),"PLAYLISTMAIN",'playlistMain',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def cleanTitle(title):
        return title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#x27;","'").replace("&#039;","\\").replace("&quot;","\"").strip()

def playlistMain():
        playlists=[]
        if os.path.exists(playlistFile):
          fh = open(playlistFile, 'r')
          for line in fh:
            pl=line[line.find("PLAYLIST###=")+12:]
            pl=pl[:pl.find("###")]
            if not pl in playlists:
              playlists.append(pl)
          fh.close()
          if len(playlists)==1:
            playlist(playlists[0])
          else:
            for pl in playlists:
              addDir(pl,pl,'playlist',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def playlist(playlist):
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_PRODUCTIONCODE)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if os.path.exists(playlistFile):
          fh = open(playlistFile, 'r')
          count=fh.read().count("###PLAYLIST###="+playlist+"###")
          rndNumbers=random.sample(range(count), count)
          fh.close()
          fh = open(playlistFile, 'r')
          all_lines = fh.readlines()
          i=0
          for line in all_lines:
            pl=line[line.find("PLAYLIST###=")+12:]
            pl=pl[:pl.find("###")]
            url=line[line.find("###URL###=")+10:]
            url=url[:url.find("###TITLE###")]
            title=line[line.find("###TITLE###=")+12:]
            title=title[:title.find("###THUMB###")]
            thumb=line[line.find("###THUMB###=")+12:]
            thumb=thumb[:thumb.find("###END###")]
            if pl==playlist:
              addPlaylistLink(title,urllib.quote_plus(url),'playVideoFromPlaylist',thumb,(rndNumbers[i]+1),playlist)
              i=i+1
          fh.close()
        xbmcplugin.endOfDirectory(pluginhandle)

def artists():
        letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
        for letter in letters:
          addDir(letter.upper(),letter,'artistsAZ',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def artistsAZ(letter):
        content = getUrl("http://www.mtv.de/artists?letter="+letter)
        content = content[content.find("<div class='teaser_collection small artist_list'>"):]
        content = content[:content.find("</ul>")]
        spl=content.split('<li>')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('<a href="(.+?)">', re.DOTALL).findall(entry)
            url="http://www.mtv.de"+match[0]
            match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb=match[0]
            if thumb=="http://images.mtvnn.com/2edca9f206f1010355e380e7793b93d4/96x54_":
              thumb=""
            match=re.compile("<h3 title=(.+?)>", re.DOTALL).findall(entry)
            title=match[0]
            title=title[1:len(title)-1]
            title=cleanTitle(title)
            addArtistDir(title,url,'listVideos',thumb)
        xbmcplugin.endOfDirectory(pluginhandle)

def artistsFavs():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if os.path.exists(artistsFavsFile):
          fh = open(artistsFavsFile, 'r')
          all_lines = fh.readlines()
          for line in all_lines:
            url=line[line.find("###URL###=")+10:]
            url=url[:url.find("###TITLE###")]
            title=line[line.find("###TITLE###=")+12:]
            title=title[:title.find("###END###")]
            addArtistFavDir(title,urllib.quote_plus(url),'listVideosFromFavs',"")
          fh.close()
        xbmcplugin.endOfDirectory(pluginhandle)

def listVideosFromFavs(url):
        listVideos(urllib.unquote_plus(url))

def titles():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_PRODUCTIONCODE)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        contentBlacklist=""
        if os.path.exists(blacklistFile):
          fh = open(blacklistFile, 'r')
          contentBlacklist=fh.read()
          fh.close()
        numTitles=-1
        if os.path.exists(titlesListFile):
          fh = open(titlesListFile, 'r')
          all_lines = fh.readlines()
          numTitles=len(all_lines)
          rndNumbers=random.sample(range(numTitles), numTitles)
          i=0
          for line in all_lines:
            url=line[line.find("###URL###=")+10:]
            url=url[:url.find("###TITLE###")]
            title=line[line.find("###TITLE###=")+12:]
            title=title[:title.find("!!!END!!!")]
            if contentBlacklist.find(title)==-1:
              if filterVids=="true":
                if title.lower().find("all eyes on")==-1 and title.lower().find("interview")==-1:
                  addLink(title,url,'playVideo',"",(rndNumbers[i]+1))
              else:
                addLink(title,url,'playVideo',"",(rndNumbers[i]+1))
            i=i+1
          fh.close()
        xbmcplugin.endOfDirectory(pluginhandle)
        try:
          wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
          wnd.getControl(wnd.getFocusId()).selectItem(1)
        except:
          pass

def playVideoFromPlaylist(url):
        listitem = xbmcgui.ListItem(path=urllib.unquote_plus(url))
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def listShows(url):
        content = getUrl(url)
        spl=content.split("class='franchise teaser")
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('<a href="(.+?)"', re.DOTALL).findall(entry)
            url="http://www.mtv.de"+match[0]
            match=re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
            title=match[0]
            match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb=match[0]
            addDir(title,url,'listVideos',thumb)
        xbmcplugin.endOfDirectory(pluginhandle)

def listShow(url):
        content = getUrl(url)
        if content.find("<div class='season-info'>")>=0:
          content = content[content.find("<div class='season-info'>"):]
          content = content[:content.find("</ol>")]
          spl=content.split("<li")
          for i in range(1,len(spl),1):
              entry=spl[i]
              match=re.compile('href="(.+?)" class=".*?">(.+?)<', re.DOTALL).findall(entry)
              url="http://www.mtv.de"+match[0][0]
              title="Season "+match[0][1]
              addDir(title,url,'listVideos',"")
          xbmcplugin.endOfDirectory(pluginhandle)
        else:
          listVideos(url)

def listVideos(url):
        contentTitles=""
        if os.path.exists(titlesListFile):
          fh = open(titlesListFile, 'r')
          contentTitles=fh.read()
          fh.close()
        contentBlacklist=""
        if os.path.exists(blacklistFile):
          fh = open(blacklistFile, 'r')
          contentBlacklist=fh.read()
          fh.close()
        content = getUrl(url)
        newTitles=""
        #content = content[content.find("<div class='current_season'>"):]
        #content = content[:content.find("</ul>")]
        spl=content.split('marquee-slide video')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('"token":"(.+?)"', re.DOTALL).findall(entry)
            if match:
              url=match[0]
              match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
              thumb=match[0]
              match=re.compile("class='info-title'>(.+?)<", re.DOTALL).findall(entry)
              title=match[0]
              if ">" in title:
                title = title[title.find(">")+1:]
              match=re.compile("class='info-subtitle'>(.+?)<", re.DOTALL).findall(entry)
              title2=match[0]
              if ">" in title2:
                title2 = title2[title2.find(">")+1:].strip()
              match=re.compile("<span>(.+?)</span>", re.DOTALL).findall(entry)
              if match:
                title2=match[0]
              title=title+" - "+title2
              title=cleanTitle(title)
              titleInfos="###URL###="+url+"###TITLE###="+title+"!!!END!!!"
              match=re.compile("<span class='chart_position'>(.+?)</span>", re.DOTALL).findall(entry)
              titleRaw=title
              if len(match)==1:
                title=match[0].strip()+". "+title
              if contentTitles.find(titleInfos)==-1 and newTitles.find(titleInfos)==-1:
                newTitles = newTitles + titleInfos
              if contentBlacklist.find(titleRaw)==-1:
                if filterVids=="true":
                  if title.lower().find("all eyes on")==-1 and title.lower().find("interview")==-1:
                    addLink(title,url,'playVideo',thumb)
                else:
                  addLink(title,url,'playVideo',thumb)
        xbmcplugin.endOfDirectory(pluginhandle)
        xbmc.executebuiltin('XBMC.RunScript(special://home/addons/'+addonID+'/titles.py,'+urllib.quote_plus(newTitles)+')')
        if forceViewMode:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosLatest(url):
        urlMain=url
        contentBlacklist=""
        if os.path.exists(blacklistFile):
          fh = open(blacklistFile, 'r')
          contentBlacklist=fh.read()
          fh.close()
        contentTitles=""
        newTitles=""
        if os.path.exists(titlesListFile):
          fh = open(titlesListFile, 'r')
          contentTitles=fh.read()
          fh.close()
        content = getUrl(url)
        spl=content.split(" teaser'>")
        for i in range(1,len(spl),1):
          entry=spl[i]
          match=re.compile('href="(.+?)"', re.DOTALL).findall(entry)
          url="http://www.mtv.de/"+match[0]
          match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
          thumb=match[0].replace("/306x172","/960x540!")
          match=re.compile('title="(.+?)"', re.DOTALL).findall(entry)
          titleNew=match[0]
          titleNew=cleanTitle(titleNew)
          titleInfos="###URL###="+url+"###TITLE###="+titleNew+"!!!END!!!"
          if contentTitles.find(titleInfos)==-1 and newTitles.find(titleInfos)==-1:
            newTitles = newTitles + titleInfos
          if contentBlacklist.find(titleNew)==-1:
            addLink(titleNew,url,'playVideo',thumb)
        if urlMain.find("?page=")==-1:
          nextPage="2"
        else:
          nextPage=str(int(urlMain[-1:])+1)
        addDir(translation(30012)+" ("+nextPage+")","http://www.mtv.de/musikvideos?page="+nextPage,'listVideosLatest',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        xbmc.executebuiltin('XBMC.RunScript(special://home/addons/'+addonID+'/titles.py,'+urllib.quote_plus(newTitles)+')')
        if forceViewMode:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playShow(id):
        content = getUrl("http://api.mtvnn.com/v2/mrss.xml?uri=mgid:sensei:video:mtvnn.com:local_playlist-"+id+"-DE")
        match=re.compile("<media:content duration='(.+?)' isDefault='true' type='text/xml' url='(.+?)'></media:content>", re.DOTALL).findall(content)
        playVideoMain(match[0][1])

def playVideo(url):
        if url.find("http://")==0:
          content = getUrl(url)
          match=re.compile('music_video-(.+?)-DE', re.DOTALL).findall(content)
          url=match[0]
        content = getUrl("http://api.mtvnn.com/v2/mrss.xml?uri=mgid:sensei:video:mtvnn.com:music_video-"+url+"-DE")
        match=re.compile("<media:content duration='(.+?)' isDefault='true' type='text/xml' url='(.+?)'></media:content>", re.DOTALL).findall(content)
        playVideoMain(match[0][1])

def playVideoMain(url):
        content = getUrl(url)
        if content.find("/www/custom/intl/errorslates/video_error.flv")>=0 or content.find("/www/custom/intl/errorslates/copyright_error.flv")>=0 or content.find('<error message="uri not found" />')>=0:
          xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30209))+',5000)')
        else:
          match=re.compile('type="video/mp4" bitrate="(.+?)">\n<src>(.+?)</src>', re.DOTALL).findall(content)
          match2=re.compile('type="video/mp4" bitrate="(.+?)">\n        <src>(.+?)</src>', re.DOTALL).findall(content)
          match3=re.compile('type="video/x-flv" bitrate="(.+?)">\n<src>(.+?)</src>', re.DOTALL).findall(content)
          match4=re.compile('type="video/x-flv" bitrate="(.+?)">\n        <src>(.+?)</src>', re.DOTALL).findall(content)
          urlNew=""
          bitrate=0
          if len(match)>0:
            pass
          elif len(match2)>0:
            match=match2
          elif len(match3)>0:
            match=match3
          elif len(match4)>0:
            match=match4
          for br,url in match:
            if int(br)>bitrate:
              bitrate=int(br)
              urlNew=url
          if urlNew!="":
            if urlNew.find("http://")==0:
              listitem = xbmcgui.ListItem(path=urlNew)
            elif urlNew.find("rtmp://")==0 or urlNew.find("rtmpe://")==0:
              listitem = xbmcgui.ListItem(path=urlNew+" swfVfy=1 swfUrl=http://media.mtvnservices.com/player/prime/mediaplayerprime.1.8.1.swf")
            return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def search(SEARCHTYPE):
        keyboard = xbmc.Keyboard('', 'Search')
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
          search_string = keyboard.getText().replace(" ","+")
          url="http://www.mtv.de/search?query="+search_string+"&ajax=1"
          content = getUrlSearch(url)
          if SEARCHTYPE=="SEARCH_ARTIST":
            if content.find("<h2>Artists</h2>")>=0:
              content=content[content.find("<h2>Artists</h2>"):]
              content=content[:content.find("</ul>")]
              spl=content.split('<li>')
              for i in range(1,len(spl),1):
                  entry=spl[i]
                  match=re.compile('<a href="(.+?)"', re.DOTALL).findall(entry)
                  url=match[0]
                  match=re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
                  title=match[0]
                  title=cleanTitle(title)
                  addArtistDir(title,"http://www.mtv.de"+url,'listVideos',"")
          elif SEARCHTYPE=="SEARCH_SPECIAL":
            if content.find("<h2>Videos</h2>")>=0:
              content=content[content.find("<h2>Videos</h2>"):]
              content=content[:content.find("</ul>")]
              spl=content.split('<li>')
              for i in range(1,len(spl),1):
                  entry=spl[i]
                  match=re.compile('<a href="(.+?)"', re.DOTALL).findall(entry)
                  url=match[0]
                  match=re.compile('<h3>(.+?)</h3>', re.DOTALL).findall(entry)
                  title1=match[0]
                  match=re.compile('<p>(.+?)</p>', re.DOTALL).findall(entry)
                  title=match[0]+" - "+title1
                  title=cleanTitle(title)
                  if filterVids=="true":
                    if title.lower().find("all eyes on")==-1 and title.lower().find("interview")==-1:
                      addLink(title,"http://www.mtv.de"+url,'playVideo',"")
                  else:
                    addLink(title,"http://www.mtv.de"+url,'playVideo',"")
          xbmcplugin.endOfDirectory(pluginhandle)

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:16.0) Gecko/20100101 Firefox/16.0')
        response = urllib2.urlopen(req,timeout=30)
        link=response.read()
        response.close()
        return link

def getUrlSearch(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        req.add_header('Referer', 'http://www.mtv.de/charts')
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

def addLink(name,url,mode,iconimage,rndPos=""):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        if rndPos=="":
          liz.setInfo( type="Video", infoLabels={ "Title": name } )
        else:
          liz.setInfo( type="Video", infoLabels={ "Title": name, "Code": str(rndPos) } )
        liz.setProperty('IsPlayable', 'true')
        nameNew=name
        if name.find(". ")==2:
          nameNew=name[4:]
        if useThumbAsFanart:
          liz.setProperty("fanart_image", iconimage)
        playListInfos="###MODE###=ADD###URL###="+u+"###TITLE###="+nameNew+"###THUMB###="+iconimage+"###END###"
        liz.addContextMenuItems([(translation(30202), 'XBMC.RunScript(special://home/addons/'+addonID+'/playlist.py,'+urllib.quote_plus(playListInfos)+')',),(translation(30204), 'XBMC.RunScript(special://home/addons/'+addonID+'/blacklist.py,'+urllib.quote_plus(playListInfos)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addPlaylistLink(name,url,mode,iconimage,rndPos,playlist):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Code": str(rndPos) } )
        liz.setProperty('IsPlayable', 'true')
        playListInfos="###MODE###=REMOVE###REFRESH###=TRUE###URL###="+urllib.unquote_plus(url)+"###TITLE###="+name+"###THUMB###="+iconimage+"###END###PLAYLIST###="+playlist+"###PLEND###"
        liz.addContextMenuItems([(translation(30203), 'XBMC.RunScript(special://home/addons/'+addonID+'/playlist.py,'+urllib.quote_plus(playListInfos)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urllib.unquote_plus(url),listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addShowLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addTCDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.addContextMenuItems([(translation(30207), 'XBMC.RunScript(special://home/addons/'+addonID+'/deleteTitles.py)',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addArtistDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        playListInfos="###MODE###=ADD###URL###="+url+"###TITLE###="+name+"###END###"
        liz.addContextMenuItems([(translation(30205), 'XBMC.RunScript(special://home/addons/'+addonID+'/artistsFavs.py,'+urllib.quote_plus(playListInfos)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addArtistFavDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        playListInfos="###MODE###=REMOVE###REFRESH###=TRUE###URL###="+urllib.unquote_plus(url)+"###TITLE###="+name+"###END###"
        liz.addContextMenuItems([(translation(30206), 'XBMC.RunScript(special://home/addons/'+addonID+'/artistsFavs.py,'+urllib.quote_plus(playListInfos)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosLatest':
    listVideosLatest(url)
elif mode == 'listVideosFromFavs':
    listVideosFromFavs(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listShow':
    listShow(url)
elif mode == 'listEpisodes':
    listEpisodes(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playShow':
    playShow(url)
elif mode == 'playVideoFromPlaylist':
    playVideoFromPlaylist(url)
elif mode == 'search':
    search(url)
elif mode == 'titles':
    titles()
elif mode == 'artists':
    artists()
elif mode == 'artistsAZ':
    artistsAZ(url)
elif mode == 'artistsFavs':
    artistsFavs()
elif mode == 'playlist':
    playlist(url)
elif mode == 'playlistMain':
    playlistMain()
else:
    index()

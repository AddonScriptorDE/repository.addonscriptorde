#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
iconARD=xbmc.translatePath('special://home/addons/'+addonID+'/iconARD.png')
iconArte=xbmc.translatePath('special://home/addons/'+addonID+'/iconArte.png')
iconATV=xbmc.translatePath('special://home/addons/'+addonID+'/iconATV.png')
iconDMAX=xbmc.translatePath('special://home/addons/'+addonID+'/iconDMAX.png')
iconEuroNews=xbmc.translatePath('special://home/addons/'+addonID+'/iconEuroNews.png')
iconMTV=xbmc.translatePath('special://home/addons/'+addonID+'/iconMTV.png')
iconMySpass=xbmc.translatePath('special://home/addons/'+addonID+'/iconMySpass.png')
iconN24=xbmc.translatePath('special://home/addons/'+addonID+'/iconN24.png')
iconNOW=xbmc.translatePath('special://home/addons/'+addonID+'/iconNOW.png')
iconSouthPark=xbmc.translatePath('special://home/addons/'+addonID+'/iconSouthPark.png')
iconSpiegelTV=xbmc.translatePath('special://home/addons/'+addonID+'/iconSpiegelTV.png')
iconVEVOTV=xbmc.translatePath('special://home/addons/'+addonID+'/iconVEVOTV.png')
iconWeltDerWunder=xbmc.translatePath('special://home/addons/'+addonID+'/iconWeltDerWunder.png')
iconZDF=xbmc.translatePath('special://home/addons/'+addonID+'/iconZDF.png')
iconTele5=xbmc.translatePath('special://home/addons/'+addonID+'/iconTele5.png')
iconTT=xbmc.translatePath('special://home/addons/'+addonID+'/iconTT.png')
iconPS=xbmc.translatePath('special://home/addons/'+addonID+'/iconPS.png')


def index():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    addDir("ARD","plugin://plugin.video.ardmediathek_de",iconARD)
    addDir("Arte","plugin://plugin.video.arte_tv",iconArte)
    addDir("ATV","plugin://plugin.video.atv_at",iconATV)
    addDir("DMAX","plugin://plugin.video.dmax_de",iconDMAX)
    addDir("Euronews","plugin://plugin.video.euronews_com",iconEuroNews)
    addDir("MTV","plugin://plugin.video.mtv_de/?mode=listShows&url=http%3a%2f%2fwww.mtv.de%2fshows%2falle",iconMTV)
    addDir("MySpass","plugin://plugin.video.myspass_de",iconMySpass)
    addDir("N24","plugin://plugin.video.n24_de",iconN24)
    addDir("South Park","plugin://plugin.video.southpark_de",iconSouthPark)
    addDir("Spiegel TV","plugin://plugin.video.spiegel_tv",iconSpiegelTV)
    addDir("VEVO TV","plugin://plugin.video.vevo_tv",iconVEVOTV)
    addDir("Welt der Wunder","plugin://plugin.video.welt_der_wunder",iconWeltDerWunder)
    addDir("ZDF","plugin://plugin.video.zdf_de_lite",iconZDF)
    addDir("Tele 5","plugin://plugin.video.tele5_de",iconTele5)
    addDir("NOW","plugin://plugin.video.rtl_now", iconNOW)
    addDir("TV Today - Best of Mediatheken","plugin://plugin.video.tvtoday_de", iconTT)
    addDir("ProSiebenSat.1 Media","plugin://plugin.video.prosiebensat1_media", iconPS)
    xbmcplugin.endOfDirectory(pluginhandle)


def addDir(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=True)
    return ok


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

index()

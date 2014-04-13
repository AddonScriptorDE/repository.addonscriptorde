#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
iconTivi=xbmc.translatePath('special://home/addons/'+addonID+'/iconTivi.png')
iconKIKA=xbmc.translatePath('special://home/addons/'+addonID+'/iconKIKA.png')
iconNick=xbmc.translatePath('special://home/addons/'+addonID+'/iconNick.png')
iconKIKI=xbmc.translatePath('special://home/addons/'+addonID+'/iconKIKI.png')
iconPK=xbmc.translatePath('special://home/addons/'+addonID+'/iconPK.png')
iconKN=xbmc.translatePath('special://home/addons/'+addonID+'/iconKN.png')
iconCE=xbmc.translatePath('special://home/addons/'+addonID+'/iconCE.png')
iconSS=xbmc.translatePath('special://home/addons/'+addonID+'/iconSS.png')
iconDC=xbmc.translatePath('special://home/addons/'+addonID+'/iconDC.png')
site1=addon.getSetting("site1")=="true"
site2=addon.getSetting("site2")=="true"
site3=addon.getSetting("site3")=="true"
site4=addon.getSetting("site4")=="true"
site5=addon.getSetting("site5")=="true"
site6=addon.getSetting("site6")=="true"
site7=addon.getSetting("site7")=="true"
site8=addon.getSetting("site8")=="true"
site9=addon.getSetting("site9")=="true"

def index():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if site1:
        addDir("ZDF tivi","plugin://plugin.video.tivi_de",iconTivi)
    if site2:
        addDir("KIKA+","plugin://plugin.video.kika_de",iconKIKA)
    if site3:
        addDir("Nickelodeon","plugin://plugin.video.nick_de", iconNick)
    if site4:
        addDir("Kinderkino","plugin://plugin.video.kinderkino_de", iconKIKI)
    if site5:
        addDir("Pfefferkörner","plugin://plugin.video.pfefferkoerner_de", iconPK)
    if site6:
        addDir("SWR Kindernetz","plugin://plugin.video.kindernetz_de", iconKN)
    if site7:
        addDir("ARD CheckEins","plugin://plugin.video.checkeins_de", iconCE)
    if site8:
        addDir("Sesamstraße","plugin://plugin.video.sesamstrasse_de", iconSS)
    if site9:
        addDir("Disney Channel","plugin://plugin.video.disneychannel_de", iconDC)
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

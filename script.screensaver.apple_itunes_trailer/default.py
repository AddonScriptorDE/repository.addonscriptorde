#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import xbmcplugin
import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
quality = addon.getSetting("quality")
quality = ["480p", "720p", "1080p"][int(quality)]
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'iTunes')]

def playVideo(url):
    content = opener.open(url).read()
    match = re.compile('<a class="movieLink" href="(.+?)"', re.DOTALL).findall(content)
    url = match[0]
    url = url[:url.find("?")].replace("720p", "h"+quality)+"|User-Agent=iTunes"
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
url = urllib.unquote_plus(params.get('url', ''))
playVideo(url)

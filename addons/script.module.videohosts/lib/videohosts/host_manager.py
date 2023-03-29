import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import json
import re
import socket
import xbmc
import xbmcgui
import xbmcaddon
import XbmcHelpers
common = XbmcHelpers

from . import collaps
from . import iframe
from . import videocdn
from . import hdvb

from . import tools

socket.setdefaulttimeout(120)

ID = 'script.module.videohosts'
ADDON = xbmcaddon.Addon(ID)

def select_vhost(hm):
    if len(hm) > 1:
        dialog = xbmcgui.Dialog()
        index_ = dialog.select("Select videohost", list(hm))
        if int(index_) < 0:
            index_ = -1    
    else:
        index_ = 0
    if index_ == -1:
        return None
    else:    
        return list(hm)[index_]

def get_playlist_by_vhost(vhost, iframe):
    try:
        if vhost == "HDVB":
            return hdvb.get_playlist(iframe)
        elif vhost == "COLLAPS":
            return collaps.get_playlist(iframe)
        elif vhost == "VIDEOCDN":
            return videocdn.get_playlist(iframe)
        elif vhost == "VIDEOFRAME":
            return iframe.get_playlist(iframe)
        else:
            return None, None, None, None
    except:
        return None, None, None, None


def get_playlist(data):
    manifest_links = {}
    iframes_hm = {} 
    subtitles = None
    season = None
    episode = None
    mode = ADDON.getSetting("mode")
    preferred = ADDON.getSetting("preferred")

    iframes = common.parseDOM(data, "iframe", ret="src")
    iframes += common.parseDOM(data, "li", ret="data-iframe")
    
    for item in iframes:
        if re.search("vid\d+", item):
            iframes_hm["HDVB"] = item
        elif re.search("api\d+", item):
            iframes_hm["COLLAPS"] = item
        elif "kinokong" in item:
            iframes_hm["VIDEOCDN"] = item
        elif "videoframe" in item:
            iframes_hm["VIDEOFRAME"] = item

    xbmc.log("hm=" + repr(iframes_hm))

    if mode == "preferred":
        test = None
        try:
            test = iframes_hm[preferred]
        except:
            pass
        if test:
            return get_playlist_by_vhost(preferred, iframes_hm[preferred])        
        else:
            mode = "auto"

    if mode == "auto":
        for k, v in list(iframes_hm.items()):
            if manifest_links and (len(manifest_links) > 0):
               break 
            manifest_links, subtitles, season, episode = get_playlist_by_vhost(k, v)
    else:
        vhost = select_vhost(iframes_hm)
        if vhost:
            manifest_links, subtitles, season, episode = get_playlist_by_vhost(vhost, iframes_hm[vhost])

    return manifest_links, subtitles, season, episode 
    
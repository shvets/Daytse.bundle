# -*- coding: utf-8 -*-

ART = 'art-default.jpg'
ICON = 'icon-default.png'

PREFIX = '/video/daytse'

import library_bridge

library_bridge.bridge.export_object('L', L)
library_bridge.bridge.export_object('R', R)
library_bridge.bridge.export_object('Log', Log)
library_bridge.bridge.export_object('Resource', Resource)
library_bridge.bridge.export_object('Datetime', Datetime)
library_bridge.bridge.export_object('Core', Core)
library_bridge.bridge.export_object('Prefs', Prefs)
library_bridge.bridge.export_object('Locale', Locale)
library_bridge.bridge.export_object('Callback', Callback)
library_bridge.bridge.export_object('AudioCodec', AudioCodec)
library_bridge.bridge.export_object('AudioStreamObject', AudioStreamObject)
library_bridge.bridge.export_object('VideoStreamObject', VideoStreamObject)
library_bridge.bridge.export_object('DirectoryObject', DirectoryObject)
library_bridge.bridge.export_object('PartObject', PartObject)
library_bridge.bridge.export_object('MediaObject', MediaObject)
library_bridge.bridge.export_object('EpisodeObject', EpisodeObject)
library_bridge.bridge.export_object('TVShowObject', TVShowObject)
library_bridge.bridge.export_object('MovieObject', MovieObject)
library_bridge.bridge.export_object('TrackObject', TrackObject)
library_bridge.bridge.export_object('VideoClipObject', VideoClipObject)
library_bridge.bridge.export_object('MessageContainer', MessageContainer)

import plex_util

from daytse_plex_service import DaytsePlexService

service = DaytsePlexService()

import main

def Start():
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')
    Plugin.AddViewGroup('MediaPreview', viewMode='MediaPreview', mediaType='items')

    ObjectContainer.title1 = unicode(L("Title"))
    DirectoryObject.art = R(ART)
    VideoClipObject.art = R(ART)

    # HTTP.CacheTime = CACHE_1HOUR

    plex_util.validate_prefs()

@handler(PREFIX, 'Daytse', R(ART), R(ICON))
def MainMenu():
    if not service.available():
        return MessageContainer(L('Error'), L('Service not avaliable'))

    oc = ObjectContainer(title2=unicode(L('Title')), no_cache=True)

    oc.add(DirectoryObject(key = Callback(main.HandleMovies), title = unicode(L("Movies"))))
    oc.add(DirectoryObject(key = Callback(main.HandleLatestEpisodes), title = unicode(L("Latest Episodes"))))
    oc.add(DirectoryObject(key = Callback(main.HandleSeries), title = unicode(L("Series"))))
    oc.add(DirectoryObject(key = Callback(main.HandleGenres), title = unicode(L("Genres"))))
    oc.add(DirectoryObject(key=Callback(main.HandleHistory), title=unicode(L('History'))))
    oc.add(DirectoryObject(key=Callback(main.HandleQueue), title=unicode(L('Queue'))))

    oc.add(InputDirectoryObject(
        key=Callback(main.HandleSearch),
        title=unicode(L('Search')), prompt=unicode(L('Search on Dayt.se'))
    ))

    return oc

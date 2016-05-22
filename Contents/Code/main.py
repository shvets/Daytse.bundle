# -*- coding: utf-8 -*-

import plex_util
import pagination
import history
from media_info import MediaInfo

@route(PREFIX + "/movies")
def HandleMovies(page=1):
    oc = ObjectContainer(title1=unicode(L("Movies")))

    response = service.get_movies(page=page)

    for item in response['movies']:
        oc.add(DirectoryObject(
            key=Callback(HandleMovie, name=item['name'], id=item['path'], thumb=item['thumb']),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    pagination.append_controls(oc, response, callback=HandleMovies, page=page)

    return oc

@route(PREFIX + "/latest_episodes")
def HandleLatestEpisodes(page=1):
    oc = ObjectContainer(title1=unicode(L("Latest Episodes")))

    response = service.get_latest_episodes(page=page)

    for item in response['movies']:
        oc.add(DirectoryObject(
            key=Callback(HandleEpisode, name=item['name'], id=item['path'], thumb=item['thumb']),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    pagination.append_controls(oc, response, callback=HandleLatestEpisodes, page=page)

    return oc

@route(PREFIX + "/series")
def HandleSeries(page=1):
    oc = ObjectContainer(title1=unicode(L("Series")))

    response = service.get_series(page=page)

    for item in response['movies']:
        oc.add(DirectoryObject(
            key=Callback(HandleSerie, serieName=item['name'], id=item['path'], thumb=item['thumb']),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    pagination.append_controls(oc, response, callback=HandleSeries, page=page)

    return oc

@route(PREFIX + "/serie")
def HandleSerie(**params):
    oc = ObjectContainer(title1=unicode(params['serieName']))

    response = service.get_seasons(params['id'])

    for item in response:
        oc.add(DirectoryObject(
            key=Callback(HandleSeason, name=item['name'], id=item['path']),
            title=item['name'],
            thumb=params['thumb']
        ))

    return oc

@route(PREFIX + "/season")
def HandleSeason(name, id):
    oc = ObjectContainer(title1=unicode(name))

    response = service.get_season(id)

    for item in response:
        season_name = service.simplify_name(item['name'])

        oc.add(DirectoryObject(
            key=Callback(HandleEpisode, name=season_name, id=item['path']),
            title=season_name
        ))

    return oc

@route(PREFIX + '/episode')
def HandleEpisode(operation=None, container=False, **params):
    return HandleMovie(operation=operation, container=container, **params)

@route(PREFIX + "/genres")
def HandleGenres():
    oc = ObjectContainer(title1=unicode(L("Genres")))

    response = service.get_genres()

    for item in response:
        oc.add(DirectoryObject(
            key=Callback(HandleGenre, name=item['name'], id=item['path']),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    return oc

@route(PREFIX + "/genre")
def HandleGenre(name, id, page=1):
    oc = ObjectContainer(title1=unicode(name))

    response = service.get_genre(id, page=page)

    for item in response['movies']:
        oc.add(DirectoryObject(
            key=Callback(HandleMovie, name=item['name'], id=item['path'], thumb=item['thumb']),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    pagination.append_controls(oc, response, callback=HandleGenre, name=name, id=id, page=page)

    return oc

@route(PREFIX + "/movie")
def HandleMovie(operation=None, container=False, **params):
    oc = ObjectContainer(title1=unicode(params['name']))

    media_info = MediaInfo(**params)

    service.queue.handle_bookmark_operation(operation, media_info)

    response = service.get_movie(params['id'])

    if response['thumb']:
        thumb = response['thumb']
    else:
        thumb = params['thumb']

    name = response['name']

    urls = response['urls']

    urls_length = len(urls)

    for index, url in enumerate(urls):
        if urls_length > 1:
            url_name = str(index+1) + "-" + name
        else:
            url_name = name

        oc.add(MetadataObjectForURL(url=url, thumb=thumb, title=url_name))

    if 'trailer_url' in response:
        oc.add(MetadataObjectForURL(url=response['trailer_url'], thumb=thumb, title="Watch Trailer"))

    if str(container) == 'False':
        history.push_to_history(Data, media_info)
        service.queue.append_bookmark_controls(oc, HandleMovie, media_info)

    return oc

def MetadataObjectForURL(url, thumb, title):
    metadata_object = VideoClipObject(
        url=url,
        thumb=plex_util.get_thumb(thumb),
        title=unicode(L(title))
    )

    return metadata_object

@route(PREFIX + '/search')
def HandleSearch(query=None, page=1):
    oc = ObjectContainer(title2=unicode(L('Search')))

    response = service.search(query=query)

    for item in response:
        oc.add(DirectoryObject(
            key=Callback(HandleMovieOrSerie, id=tem['path'], name=item['name'], isSerie=item['isSerie']),
            title=unicode(item['name'])
        ))

    pagination.append_controls(oc, response, callback=HandleSearch, query=query, page=page)

    return oc

@route(PREFIX + '/movie_or_serie')
def HandleMovieOrSerie(**params):
    if params['isSerie'] == True:
        params['type'] = 'serie'
        params['serieName'] = params['name']
    else:
        params['type'] = 'movie'

    return HandleContainer(**params)

@route(PREFIX + '/container')
def HandleContainer(**params):
    Log(params)
    type = params['type']

    if type == 'movie':
        return HandleMovie(**params)
    elif type == 'episode':
        return HandleEpisode(**params)
    elif type == 'season':
        return HandleSeason(**params)
    elif type == 'serie':
        return HandleSerie(**params)

@route(PREFIX + '/queue')
def HandleQueue():
    oc = ObjectContainer(title2=unicode(L('Queue')))

    service.queue.handle_queue_items(oc, HandleContainer, service.queue.data)

    if len(service.queue.data) > 0:
        oc.add(DirectoryObject(
            key=Callback(ClearQueue),
            title=unicode(L("Clear Queue"))
        ))

    return oc

@route(PREFIX + '/clear_queue')
def ClearQueue():
    service.queue.clear()

    return HandleQueue()

@route(PREFIX + '/history')
def HandleHistory():
    history_object = history.load_history(Data)

    oc = ObjectContainer(title2=unicode(L('History')))

    if history_object:
        data = sorted(history_object.values(), key=lambda k: k['time'], reverse=True)

        service.queue.handle_queue_items(oc, HandleContainer, data)

    return oc
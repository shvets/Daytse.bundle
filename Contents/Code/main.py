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

@route(PREFIX + "/latest")
def HandleLatest(page=1):
    oc = ObjectContainer(title1=unicode(L("Latest")))

    response = service.get_latest(page=page)

    for item in response['movies']:
        new_params = {
            # "isSerie": True,
            "name": item['name'],
            "id": item['path'],
            "thumb": item['thumb']
        }
        oc.add(DirectoryObject(
            key=Callback(HandleMovie, **new_params),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    pagination.append_controls(oc, response, callback=HandleLatest, page=page)

    return oc

# @route(PREFIX + "/latest_episodes")
# def HandleLatestEpisodes(page=1):
#     oc = ObjectContainer(title1=unicode(L("Latest Episodes")))
#
#     response = service.get_latest_episodes(page=page)
#
#     for item in response['movies']:
#         oc.add(DirectoryObject(
#             key=Callback(HandleEpisode, name=item['name'], id=item['path'], thumb=item['thumb']),
#             title=item['name'],
#             thumb=plex_util.get_thumb(item['thumb'])
#         ))
#
#     pagination.append_controls(oc, response, callback=HandleLatestEpisodes, page=page)
#
#     return oc

@route(PREFIX + "/series")
def HandleSeries(page=1):
    oc = ObjectContainer(title1=unicode(L("Series")))

    response = service.get_series(page=page)

    for item in response['movies']:
        new_params = {
            'type': 'serie',
            'name': item['name'],
            'id': item['path'],
            'thumb': item['thumb']
        }

        oc.add(DirectoryObject(
            key=Callback(HandleSerie, **new_params),
            title=item['name'],
            thumb=plex_util.get_thumb(item['thumb'])
        ))

    pagination.append_controls(oc, response, callback=HandleSeries, page=page)

    return oc

@route(PREFIX + "/serie")
def HandleSerie(operation=None, **params):
    oc = ObjectContainer(title1=unicode(params['name']))

    media_info = MediaInfo(**params)

    service.queue.handle_bookmark_operation(operation, media_info)

    response = service.get_seasons(params['id'])

    for item in response:
        season_number = item['name'][len("Season"):].strip()

        new_params = {
            'type': 'season',
            'id': item['path'],
            'serieName': params['name'],
            'name': item['name'],
            'thumb': params['thumb'],
            'season': season_number,
        }

        oc.add(DirectoryObject(
            key=Callback(HandleSeason, **new_params),
            title=item['name'],
            thumb=params['thumb']
        ))

    service.queue.append_bookmark_controls(oc, HandleSerie, media_info)

    return oc

@route(PREFIX + "/season")
def HandleSeason(operation=None, container=False, **params):
    oc = ObjectContainer(title1=unicode(params['name']))

    media_info = MediaInfo(**params)

    service.queue.handle_bookmark_operation(operation, media_info)

    response = service.get_season(params['id'])

    for item in response:
        episode_name = service.simplify_name(item['name'])
        episode_number = episode_name[len("Episode"):].strip()

        new_params = {
            'type': 'episode',
            'id': item['path'],
            'serieName': params['serieName'],
            'name': episode_name,
            'thumb': params['thumb'],
            'season': params['season'],
            'episodeNumber': episode_number
        }

        oc.add(DirectoryObject(
            key=Callback(HandleEpisode, **new_params),
            title=episode_name
        ))

    if str(container) == 'False':
        history.push_to_history(Data, media_info)
        service.queue.append_bookmark_controls(oc, HandleSeason, media_info)

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

        oc.add(VideoClipObject(
            url=url,
            thumb=plex_util.get_thumb(thumb),
            title=unicode(L(url_name))
        ))

        #oc.add(MetadataObjectForURL2(media_info=media_info, url_items=url_items, handler=HandleMovie, player=PlayVideo))

    # if 'trailer_url' in response:
    #     oc.add(VideoClipObject(
    #         url=response['trailer_url'],
    #         thumb=plex_util.get_thumb(thumb),
    #         title=unicode(L("Watch Trailer"))
    #     ))

    if str(container) == 'False':
        history.push_to_history(Data, media_info)
        service.queue.append_bookmark_controls(oc, HandleMovie, media_info)

    return oc

# @route(PREFIX + '/movie_or_serie')
# def HandleMovieOrSerie(**params):
#     if 'isSerie' in params and str(params['isSerie']) == 'True':
#         params['type'] = 'serie'
#     else:
#         params['type'] = 'movie'
#
#     return HandleContainer(**params)

# def MetadataObjectForURL2(media_info, url_items, handler, player):
#     metadata_object = builder.build_metadata_object(media_type=media_info['type'], title=media_info['name'])
#
#     metadata_object.key = Callback(handler, container=True, **media_info)
#
#     metadata_object.rating_key = unicode(media_info['name'])
#     metadata_object.thumb = media_info['thumb']
#     metadata_object.title = media_info['name']
#
#     metadata_object.items = MediaObjectsForURL(url_items, player=player)
#
#     return metadata_object
#
# def MediaObjectsForURL(url_items, player):
#     media_objects = []
#
#     for item in url_items:
#         url = item['url']
#         config = item['config']
#
#         play_callback = Callback(player, url=url, play_list=False)
#
#         media_object = builder.build_media_object(play_callback, config)
#
#         media_objects.append(media_object)
#
#     return media_objects

# @route(PREFIX + '/search')
# def HandleSearch(query=None, page=1):
#     oc = ObjectContainer(title2=unicode(L('Search')))
#
#     response = service.search(query=query)
#
#     for item in response:
#         oc.add(DirectoryObject(
#             key=Callback(HandleContainer, id=item['path'], name=item['name'], type=item['type'], thumb='thumb'),
#             title=unicode(item['name'])
#         ))
#
#     pagination.append_controls(oc, response, callback=HandleSearch, query=query, page=page)
#
#     return oc

@route(PREFIX + '/container')
def HandleContainer(**params):
    if not 'thumb' in params:
        params['thumb'] = None

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

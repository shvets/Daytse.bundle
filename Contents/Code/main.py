# -*- coding: utf-8 -*-

import constants
import plex_util
import pagination
import history
from flow_builder import FlowBuilder
from media_info import MediaInfo
from daytse_plex_service import DaytsePlexService

service = DaytsePlexService()

builder = FlowBuilder()

@route(constants.PREFIX + "/movies")
def HandleMovies(page=1):
    oc = ObjectContainer(title1=unicode(L("Movies")))

    response = service.get_movies(page=page)

    for item in response['movies']:
        id = item['path']
        name = item['name']
        thumb = item['thumb']

        oc.add(DirectoryObject(
            key=Callback(HandleMovie, name=name, id=id, thumb=thumb),
            title=name,
            thumb=plex_util.get_thumb(thumb)
        ))

    pagination.append_controls(oc, response, callback=HandleMovies, page=page)

    return oc

@route(constants.PREFIX + "/latest_episodes")
def HandleLatestEpisodes(page=1):
    oc = ObjectContainer(title1=unicode(L("Latest Episodes")))

    response = service.get_latest_episodes(page=page)

    for item in response['movies']:
        id = item['path']
        name = item['name']
        thumb = item['thumb']

        oc.add(DirectoryObject(
            key=Callback(HandleEpisode, name=name, id=id, thumb=thumb),
            title=name,
            thumb=plex_util.get_thumb(thumb)
        ))

    pagination.append_controls(oc, response, callback=HandleLatestEpisodes, page=page)

    return oc

@route(constants.PREFIX + "/series")
def HandleSeries(page=1):
    oc = ObjectContainer(title1=unicode(L("Series")))

    response = service.get_series(page=page)

    for item in response['movies']:
        path = item['path']
        name = item['name']
        thumb = item['thumb']

        oc.add(DirectoryObject(
            key=Callback(HandleSerie, serieName=name, id=path),
            title=name,
            thumb=plex_util.get_thumb(thumb)
        ))

    pagination.append_controls(oc, response, callback=HandleSeries, page=page)

    return oc

@route(constants.PREFIX + "/serie")
def HandleSerie(serieName, id):
    oc = ObjectContainer(title1=unicode(serieName))

    response = service.get_previous_seasons(id)

    for item in response:
        season_id = item['path']
        name = item['name']

        oc.add(DirectoryObject(
            key=Callback(HandleSeason, serieName=serieName, id=season_id),
            title=name
        ))

    response = service.get_season(id)

    for item in response:
        season_id = item['path']
        name = item['name']

        oc.add(DirectoryObject(
            key=Callback(HandleEpisode, name=name, id=season_id),
            title=name
        ))

    return oc

    # url = service.URL + id
    #
    # page_data = HTML.ElementFromURL(url)
    # eps_list = page_data.xpath("//div[@class='inner']/h3/a")
    # season_list = page_data.xpath("//div[@class='titleline']/h2/a")
    # if len(season_list) >= 1:
    #     for each in season_list:
    #         season_url = "/forum/" + each.xpath("./@href")[0]
    #         season_title = serieName + " " + each.xpath("./text()")[0]
    #
    #         oc.add(DirectoryObject(
    #             key = Callback(HandleSerie, serieName = season_title, id = season_url),
    #             title = season_title
    #         ))

@route(constants.PREFIX + "/season")
def HandleSeason(serieName, id):
    oc = ObjectContainer(title1=unicode(serieName))

    response = service.get_season(id)

    for item in response:
        id = item['path']
        name = item['name']

        oc.add(DirectoryObject(
            key=Callback(HandleEpisode, name=name, id=id),
            title=name
        ))

    return oc

@route(constants.PREFIX + '/episode')
def HandleEpisode(operation=None, container=False, **params):
    return HandleMovie(operation=operation, container=container, **params)

@route(constants.PREFIX + "/genres")
def HandleGenres():
    oc = ObjectContainer(title1=unicode(L("Genres")))

    response = service.get_genres()

    for item in response:
        id = item['path']
        name = item['name']
        thumb = item['thumb']

        oc.add(DirectoryObject(
            key=Callback(HandleGenre, name=name, id=id),
            title=name,
            thumb=plex_util.get_thumb(thumb)
        ))

    return oc

@route(constants.PREFIX + "/genre")
def HandleGenre(name, id, page=1):
    oc = ObjectContainer(title1=unicode(name))

    response = service.get_genre(id)

    for item in response:
        id = item['path']
        name = item['name']
        thumb = item['thumb']

        oc.add(DirectoryObject(
            key=Callback(HandleMovie, name=name, id=id, thumb=thumb),
            title=name,
            thumb=plex_util.get_thumb(thumb)
        ))

    pagination.append_controls(oc, response, callback=HandleGenre, name=name, id=id, page=page)

    return oc

@route(constants.PREFIX + "/movie")
def HandleMovie(name, id, thumb=None, operation=None, container=False):
    oc = ObjectContainer(title1=unicode(name))

    response = service.get_movie(id)

    if response['thumb']:
        thumb = response['thumb']

    final_frame_url = response['final_frame_url']

    if final_frame_url:
        oc.add(VideoClipObject(
            url = final_frame_url,
            thumb = plex_util.get_thumb(thumb),
            title = unicode(response['name'])
        ))

    final_frame_url_part2 = response['final_frame_url_part2']

    if final_frame_url_part2:
        oc.add(VideoClipObject(
            url=final_frame_url_part2,
            thumb=plex_util.get_thumb(thumb),
            title=unicode("2-"+response['name'])
        ))

    final_frame_url_part3 = response['final_frame_url_part3']

    if final_frame_url_part3:
        oc.add(VideoClipObject(
            url=final_frame_url_part3,
            thumb=plex_util.get_thumb(thumb),
            title=unicode("3-"+response['name'])
        ))

    trailer_url = response['trailer_url']

    if trailer_url:
        oc.add(VideoClipObject(
            url=trailer_url,
            thumb=plex_util.get_thumb(thumb),
            title=unicode(L("Watch Trailer"))
        ))

    if str(container) == 'False':
        pass
        # history.push_to_history(Data, media_info)
        # service.queue.append_bookmark_controls(oc, HandleMovie, media_info)

    return oc

@route(constants.PREFIX + '/search')
def HandleSearch(query=None, page=1):
    oc = ObjectContainer(title2=unicode(L('Search')))

    response = service.search(query=query)

    for movie in response:
        name = movie['name']
        id = movie['path']
        # thumb = movie['thumb']

        Log(name)
        new_params = {
            'id': movie['path'],
            # 'title': name,
            'name': name,
            # 'thumb': thumb
        }
        oc.add(DirectoryObject(
            #key=Callback(HandleMovieOrSerie, **new_params),
            key=Callback(HandleMovie, **new_params),
            title=unicode(name)
            # thumb=thumb
        ))

    pagination.append_controls(oc, response, callback=HandleSearch, query=query, page=page)

    return oc

@route(constants.PREFIX + '/movie_or_serie')
def HandleMovieOrSerie(**params):
    serie_info = service.get_serie_info(params['id'])

    if serie_info:
        params['type'] = 'serie'
    else:
        params['type'] = 'movie'

    return HandleContainer(**params)

@route(constants.PREFIX + '/container')
def HandleContainer(**params):
    type = params['type']

    if type == 'movie':
        return HandleMovie(**params)
    elif type == 'episode':
        return HandleEpisode(**params)
    elif type == 'season':
        return HandleSeason(**params)
    elif type == 'serie':
        return HandleSerie(**params)


@route(constants.PREFIX + '/queue')
def HandleQueue():
    oc = ObjectContainer(title2=unicode(L('Queue')))

    service.queue.handle_queue_items(oc, HandleContainer, service.queue.data)

    if len(service.queue.data) > 0:
        oc.add(DirectoryObject(
            key=Callback(ClearQueue),
            title=unicode(L("Clear Queue"))
        ))

    return oc

@route(constants.PREFIX + '/clear_queue')
def ClearQueue():
    service.queue.clear()

    return HandleQueue()

@route(constants.PREFIX + '/history')
def HandleHistory():
    history_object = history.load_history(Data)

    oc = ObjectContainer(title2=unicode(L('History')))

    if history_object:
        data = sorted(history_object.values(), key=lambda k: k['time'], reverse=True)

        service.queue.handle_queue_items(oc, HandleContainer, data)

    return oc
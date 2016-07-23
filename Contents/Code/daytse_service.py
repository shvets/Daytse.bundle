# -*- coding: utf-8 -*-

import library_bridge

# Log = library_bridge.bridge.objects['Log']

from http_service import HttpService

class DaytseService(HttpService):
    URL = 'http://cyro.se'

    def available(self):
        document = self.fetch_document(self.URL, self.get_headers())

        return document.xpath('//td[@class="topic_content"]')

    def get_movies(self, page=1):
        return self.get_category(category="movies", page=page)

    def get_series(self, page=1):
        return self.get_category(category="tvseries", page=page)

    def get_latest_episodes(self, page=1):
        return self.get_category(category="episodes", page=page)

    def get_latest(self, page=1):
        return self.get_category(category=None, page=page)

    def get_category(self, category, page=1):
        result = []

        if category:
            page_path = "/" + category + "/index.php?" + "page=" + str(page)
        else:
            page_path = "/index.php?show=latest-topics&" + "page=" + str(page)

        document = self.fetch_document(self.URL + page_path, self.get_headers())

        items = document.xpath('//td[@class="topic_content"]')

        for item in items:
            if category:
                path = '/' + category + '/' + item.xpath("./div/a/@href")[0]
            else:
                path = '/' + item.xpath("./div/a/@href")[0]

            name = item.xpath("./div/a/img/@alt")[0]
            thumb = self.URL + item.xpath("./div/a/img/@src")[0]

            result.append({'path': path, 'thumb': thumb, 'name': name})

        pagination = self.extract_pagination_data(page_path, page=page)

        return {'movies': result, "pagination": pagination["pagination"]}

    def get_genres(self):
        result = []

        document = self.fetch_document(self.URL + "/movies/genre.php?showC=27", self.get_headers())

        items = document.xpath('//td[@class="topic_content"]')

        for item in items:
            path = "/movies/" + item.xpath("./div/a/@href")[0]
            path = path[0:len(path)]
            thumb = self.URL + item.xpath("./div/a/img/@src")[0]
            name = thumb.rsplit("/", 1)[1].rsplit("-", 1)[0]

            result.append({'path': path, 'thumb': thumb, 'name': name})

        return result

    def get_genre(self, path, page=1):
        result = []

        response = self.http_request(self.URL + self.get_corrected_path(path), headers=self.get_headers())
        new_url = response.url

        new_path = new_url[len(self.URL):]

        page_path = new_path + "&page=" + str(page)

        document = self.fetch_document(self.URL + page_path, self.get_headers())

        items = document.xpath('//td[@class="topic_content"]')

        for item in items:
            path = "/movies/" + item.xpath("./div/a/@href")[0]
            name = item.xpath("./div/a/img/@alt")[0]
            thumb = self.URL + item.xpath("./div/a/img/@src")[0]

            result.append({'path': path, 'thumb': thumb, 'name': name})

        pagination = self.extract_pagination_data(page_path, page=page)

        return {'movies': result, "pagination": pagination["pagination"]}

    def get_serie(self, path):
        result = []

        document = self.fetch_document(self.URL + path, self.get_headers())

        items = document.xpath('//div[@class="titleline"]/h2/a')

        for item in items:
            path = "/forum/" + item.xpath("./@href")[0]
            name = item.xpath("./text()")[0]

            result.append({'path': path, 'name': name})

        return result

    def get_seasons(self, path):
        result = self.get_previous_seasons(path)

        current_season = self.get_season(path)

        first_item_name = current_season[0]['name']
        index1 = first_item_name.find('Season')
        index2 = first_item_name.find('Episode')

        number = first_item_name[index1+6:index2].strip()

        result.append({'path': path, 'name': "Season " + number})

        return result

    def get_season(self, path):
        result = []

        document = self.fetch_document(self.URL + self.get_corrected_path(path), self.get_headers())

        items = document.xpath('//div[@class="inner"]/h3/a')

        for item in items:
            path = "/forum/" + item.xpath("./@href")[0]
            name = item.xpath("./text()")[0]

            if name.find("Season Download") < 1:
                result.append({'path': path, 'name': self.extract_name(name)})

        return result

    def get_previous_seasons(self, path):
        result = []

        document = self.fetch_document(self.URL + path, self.get_headers())

        items = document.xpath('//div[@class="titleline"]/h2/a')

        for item in items:
            path = "/forum/" + item.xpath("./@href")[0]
            name = item.xpath("./text()")[0]

            result.append({'path': path, 'name': name})

        return result

    def get_movie(self, id):
        result = {}

        url = self.http_request(self.URL + id, headers=self.get_headers()).url

        document = self.fetch_document(url, self.get_headers())

        result['name'] = self.extract_name(document.xpath("//title/text()")[0])

        # node = document.xpath("//blockquote[@class='postcontent restore']//div/img/@src")
        #
        # if len(node) == 0:
        #     node = document.xpath("//div[@id='fullimage']//a/img/@src")
        #
        # if len(node) > 0:
        #     result['thumb'] = node[0]

        result['thumb'] = self.URL + document.xpath('//img[@id="nameimage"]')[0].get('src')

        # load recursive iframes to find google docs url

        result['urls'] = []

        # wpm_node = document.xpath('//iframe[@id="wpm"]')
        #
        # if len(wpm_node) > 0:
        #     src = wpm_node[0].get('src')
        #
        #     document2 = self.fetch_document(self.URL + src, self.get_headers())
        #
        #     ggplayer_node = document2.xpath('//iframe[@id="ggplayer"]')
        #
        #     nodes = document2.xpath('//div/div')
        #
        #     cnt = 0
        #     for node in nodes:
        #         if node.get('id') and node.get('id')[0:4] == 'part':
        #             cnt = cnt + 1
        #
        #     if len(wpm_node) > 0:
        #         src = self.URL + ggplayer_node[0].get('src')
        #
        #         for index in range(cnt):
        #             if index == 0:
        #                 result['urls'].append(src)
        #             else:
        #                 result['urls'].append(src[0:len(src)-4] + str(index+1) + '.php')
        #
        # trailpm_node = document.xpath('//iframe[@id="trailpm"]')
        #
        # if len(trailpm_node) > 0:
        #     src = trailpm_node[0].get('src')
        #
        #     document2 = self.fetch_document(self.URL + src, self.get_headers())
        #
        #     yttrailer_node = document2.xpath('//iframe[@id="yttrailer"]')
        #
        #     if len(yttrailer_node) > 0:
        #         src = yttrailer_node[0].get('src')
        #
        #         result['trailer_url'] = src
        #


        node1 = document.xpath("//iframe/@src")

        first_frame_url = node1[0]

        # if len(node1) > 1:
        #     first_frame_url = node1[1]
        # elif len(node1) > 0:
        #     first_frame_url = node1[0]
        # else:
        #     first_frame_url = None

        if first_frame_url:
            first_frame_data = self.fetch_document(self.URL + first_frame_url, self.get_headers())

            second_frame_url = first_frame_data.xpath("//iframe/@src")[0]

            second_frame_data = self.fetch_document(self.URL + second_frame_url, self.get_headers())

            result['urls'].append(second_frame_data.xpath("//iframe/@src")[0])

            node2 = second_frame_url.split(".php")

            if len(node2) > 0:
                second_frame_url_part2 = node2[0] + "2.php"

                try:
                    second_frame_data_part2 = self.fetch_document(self.URL + second_frame_url_part2, self.get_headers())

                    result['urls'].append(second_frame_data_part2.xpath("//iframe/@src")[0])
                except:
                    pass

                try:
                    second_frame_url_part3 = node2[0] + "3.php"

                    second_frame_data_part3 = self.fetch_document(self.URL + second_frame_url_part3, self.get_headers())

                    node3 = second_frame_data_part3.xpath("//iframe/@src")

                    if len(node3) > 0:
                        result['urls'].append(node3[0])
                except:
                    pass

        if len(document.xpath("//iframe[contains(@src,'ytid=')]/@src")) > 0:
            el = self.URL + document.xpath("//iframe[contains(@src,'ytid=')]/@src")[0]

            result['trailer_url'] = el.split("?",1)[0].replace("http://dayt.se/bits/pastube.php", "https://www.youtube.com/watch?v=") + el.split("=",1)[1]

        return result

    # def search(self, query):
    #     result = []
    #
    #     data = {'titleonly': '1', 'q': query}
    #     response = self.http_request(self.URL + "/forum/search.php?do=process", method="POST", data=data, headers=self.get_headers())
    #     content = response.read()
    #
    #     document = self.to_document(content)
    #
    #     items = document.xpath('//div[@class="blockbody"]/*/li')
    #
    #     for item in items:
    #         node = item.find('div/div/div/h3[@class="searchtitle"]/a')
    #
    #         path = "/forum/" + node.xpath("./@href")[0]
    #         name = node.xpath("./text()")[0]
    #
    #         statusNode = item.find('div/div/a[@class="threadstatus"]')
    #
    #         if statusNode != None:
    #             type = 'serie'
    #         elif name.find("Episode") >=0:
    #             type = 'episode'
    #         else:
    #             type = 'movie'
    #
    #         result.append({'path': path, 'name': self.extract_name(name), 'type': type})
    #
    #     return result

    def extract_pagination_data(self, path, page):
        page = int(page)

        document = self.fetch_document(self.URL + path, self.get_headers())

        pages = 1

        response = {}

        pagination_root = document.xpath('//div[@class="mainpagination"]/table/tr')

        if pagination_root:
            pagination_block = pagination_root[0]

            items = pagination_block.xpath('td[@class="table"]/a')

            pages = len(items)

        response["pagination"] = {
            "page": page,
            "pages": pages,
            "has_previous": page > 1,
            "has_next": page < pages,
        }

        return response

    def extract_name(self, name):
        return name.rsplit(" Streaming", 1)[0].rsplit(" Download", 1)[0]

    def simplify_name(self, name):
        index = name.find('Episode')

        if index >= 0:
            return name[index:]
        else:
            return name

    @staticmethod
    def get_media_id(path):
        index = path.find('/goto-')

        id_part = path[index + 6:]

        return id_part[0:id_part.index('-')]

    @staticmethod
    def get_corrected_path(path):
        id = DaytseService.get_media_id(path)

        index = path.find('goto-')

        return path[0:index] + 'view.php?id=' + id

    @staticmethod
    def get_headers():
        return {
            'User-Agent': 'Plex-User-Agent'
        }

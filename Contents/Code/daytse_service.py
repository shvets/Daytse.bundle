# -*- coding: utf-8 -*-

import re

from http_service import HttpService

class DaytseService(HttpService):
    URL = 'http://dayt.se'


    def available(self):
        # document = self.fetch_document(self.URL)
        #
        # return document.xpath('//div[@class="container"]/div[@class="row"]')

        return True

    def get_movies(self, page=1):
        return self.get_category(category="movies", page=page)

    def get_series(self, page=1):
        return self.get_category(category="tvseries", page=page)

    def get_latest_episodes(self, page=1):
        return self.get_category(category="episodes", page=page)

    def get_category(self, category, page=1):
        result = []

        page_path = "/" + category + "/index.php?" + "page=" + str(page)

        document = self.fetch_document(self.URL + page_path, self.get_headers())

        items = document.xpath('//td[@class="topic_content"]')

        for item in items:
            path = '/' + category + '/' + item.xpath("./div/a/@href")[0]
            name = item.xpath("./div/a/img/@alt")[0]
            thumb = item.xpath("./div/a/img/@src")[0]

            result.append({'path': path, 'thumb': thumb, 'name': name})

        pagination = self.extract_pagination_data(page_path, page=page)

        return {'movies': result, "pagination": pagination["pagination"]}

    def get_genres(self):
        result = []

        document = self.fetch_document(self.URL + "/movies/genre.php?showC=27", self.get_headers())

        items = document.xpath('//td[@class="topic_content"]')

        for item in items:
            path = "/movies/" + item.xpath("./div/a/@href")[0]
            thumb = item.xpath("./div/a/img/@src")[0]
            name = thumb.rsplit("/", 1)[1].rsplit("-", 1)[0]

            result.append({'path': path, 'thumb': thumb, 'name': name})

        return result

    def get_genre(self, path, page=1):
        result = []

        document = self.fetch_document(self.URL + path, self.get_headers())

        items = document.xpath('//td[@class="topic_content"]')

        for item in items:
            path = "/movies/" + item.xpath("./div/a/@href")[0]
            name = item.xpath("./div/a/img/@alt")[0]
            thumb = item.xpath("./div/a/img/@src")[0]

            result.append({'path': path, 'thumb': thumb, 'name': name})

        return result

    def get_serie(self, path):
        result = []

        document = self.fetch_document(self.URL + path, self.get_headers())

        items = document.xpath('//div[@class="titleline"]/h2/a')

        for item in items:
            path = "/forum/" + item.xpath("./@href")[0]
            name = item.xpath("./text()")[0]

            result.append({'path': path, 'name': name})

        return result

    def get_season(self, path):
        result = []

        document = self.fetch_document(self.URL + path, self.get_headers())

        items = document.xpath('//div[@class="inner"]/h3/a')

        for item in items:
            path = "/forum/" + item.xpath("./@href")[0]
            name = item.xpath("./text()")[0]

            if name.find("Season Download") < 1:
                title = name.rsplit(" Streaming", 1)[0].rsplit(" Download", 1)[0]

                result.append({'path': path, 'name': title})

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
        url = self.URL + id

        document = self.fetch_document(url, self.get_headers())

        name = document.xpath("//title/text()")[0].rsplit(" Streaming",1)[0].rsplit(" Download",1)[0]

        try:
            thumb = document.xpath("//blockquote[@class='postcontent restore']//div/img/@src")[0]
        except:
            thumb = document.xpath("//div[@id='fullimage']//a/img/@src")[0]

        # load recursive iframes to find google docs url

        try:
            first_frame_url = document.xpath("//blockquote/div/iframe/@src")[1]
        except:
            first_frame_url = document.xpath("//blockquote/div/iframe/@src")[0]

        first_frame_data = self.fetch_document(first_frame_url, self.get_headers())

        second_frame_url = first_frame_data.xpath("//iframe/@src")[0]

        second_frame_data = self.fetch_document(second_frame_url, self.get_headers())

        final_frame_url = second_frame_data.xpath("//iframe/@src")[0]

        try:
            second_frame_url_part2 = second_frame_url.split(".php")[0]+"2.php"

            second_frame_data_part2 = self.fetch_document(second_frame_url_part2, self.get_headers())

            final_frame_url_part2 = second_frame_data_part2.xpath("//iframe/@src")[0]
        except:
            final_frame_url_part2 = None

        try:
            second_frame_url_part3 = second_frame_url.split(".php")[0]+"3.php"

            second_frame_data_part3 = self.fetch_document(second_frame_url_part3, self.get_headers())

            final_frame_url_part3 = second_frame_data_part3.xpath("//iframe/@src")[0]
        except:
            final_frame_url_part3 = None

        if len(document.xpath("//iframe[contains(@src,'ytid=')]/@src")) > 0:
            el = document.xpath("//iframe[contains(@src,'ytid=')]/@src")[0]

            trailer_url = el.split("?",1)[0].replace("http://dayt.se/pastube.php", "https://www.youtube.com/watch?v=") + el.split("=",1)[1]
        else:
            trailer_url = None

        return {
            'name': name,
            'thumb': thumb,
            'final_frame_url': final_frame_url,
            'final_frame_url_part2': final_frame_url_part2,
            'final_frame_url_part3': final_frame_url_part3,
            'trailer_url': trailer_url
        }

    def search(self, query):
        result = []

        data = {'titleonly': '0', 'q': query}
        response = self.http_request(self.URL + "/forum/search.php?do=process", method="POST", data=data, headers=self.get_headers())
        content = response.read()

        document = self.to_document(content)

        items = document.xpath('//h3[@class="searchtitle"]/a')

        for item in items:
            path = "/forum/" + item.xpath("./@href")[0]
            name = item.xpath("./text()")[0]

            result.append({'path': path, 'name': name})

        return result

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

    @staticmethod
    def get_headers():
        return {
            'User-Agent': 'Plex-User-Agent',
        }

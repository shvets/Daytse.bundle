# coding=utf-8

import test_helper

import unittest
import json

from daytse_service import DaytseService

class MyHitServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = DaytseService()

    def test_get_movies(self):
        result = self.service.get_movies()

        print(json.dumps(result, indent=4))

    def test_get_series(self):
        result = self.service.get_series()

        print(json.dumps(result, indent=4))

    def test_get_category(self):
        result = self.service.get_category(category="movies")

        print(json.dumps(result, indent=4))

    def test_get_season(self):
        id = '/tvseries/goto-9750'

        result = self.service.get_season(id)

        print(json.dumps(result, indent=4))

    def test_get_seasons(self):
        id = '/tvseries/goto-9750'

        result = self.service.get_seasons(id)

        print(json.dumps(result, indent=4))

    def test_get_movie(self):
        id = '/movies/goto-22704'

        result = self.service.get_movie(id)

        print(json.dumps(result, indent=4))

    def test_get_genres(self):
        result = self.service.get_genres()

        print(json.dumps(result, indent=4))

    def test_get_genre(self):
        genres = self.service.get_genres()

        genre = genres[0]

        result = self.service.get_genre(genre['path'])

        print(json.dumps(result, indent=4))

    def test_pagination_in_movies(self):
        result = self.service.get_movies(page=1)

        # print(json.dumps(result, indent=4))

        pagination = result['pagination']

        self.assertEqual(pagination['has_next'], True)
        self.assertEqual(pagination['has_previous'], False)
        self.assertEqual(pagination['page'], 1)

        result = self.service.get_movies(page=2)

        #print(json.dumps(result, indent=4))

        pagination = result['pagination']

        self.assertEqual(pagination['has_next'], True)
        self.assertEqual(pagination['has_previous'], True)
        self.assertEqual(pagination['page'], 2)

    def test_search(self):
        query = 'da vinci'

        result = self.service.search(query)

        print(json.dumps(result, indent=4))

if __name__ == '__main__':
    unittest.main()

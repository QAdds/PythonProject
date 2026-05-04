import logging
from custom_requester.custom_requester import CustomRequester
from constants import API_BASE_URL, MOVIES_ENDPOINT

class MoviesAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=API_BASE_URL)

    def get_movie(self, movie_id, expected_status=200):
        '''
        GET /movies - Получение всех списков фильмов по id
        '''
        return self.send_request(method="GET", endpoint=f'{MOVIES_ENDPOINT}/{movie_id}', expected_status=expected_status)

    def get_all_movies(self, expected_status=200):
        '''
        GET /movies - Получение всех списков фильмов
        '''
        return self.send_request(method="GET", endpoint=MOVIES_ENDPOINT, expected_status=expected_status)

    def create_movie(self, movie_data, expected_status=201):
        '''
        POST /movies - Создание нового фильма
        '''
        return self.send_request(method="POST", endpoint=MOVIES_ENDPOINT, data=movie_data, expected_status=expected_status)







import pytest
from api.api_manager import ApiManager
from faker import Faker

fake = Faker()

class TestMoviesApi:

    # Позитивные тесты
    def test_create_movie_by_admin(self, api_manager: ApiManager, authenticated_admin):
        '''
        Тест проверяет создание фильма администратором
        '''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://image.url",
            "price": 100,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }

        response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        data = response.json()

        assert "id" in data, "ID фильма отсутствует в ответе"
        assert data["name"] == movie_data["name"]
        assert data["location"] == movie_data["location"]

    def test_get_all_movies(self, api_manager: ApiManager):
        '''
        ПОлучение списка всех фильмоа
        '''
        response = api_manager.movies_api.get_all_movies(expected_status=200)
        data = response.json()

        assert "movies" in data, "Список фильмов отсутствует в ответе"

    def test_get_movie_by_id(self,api_manager: ApiManager, authenticated_admin):
        '''
        Получение фильма по ID
        '''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://image.url",
            "price": 100,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }
        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        data = create_response.json()
        movie_id = data["id"]
        response = api_manager.movies_api.get_movie(movie_id, expected_status=200)
        data = response.json()
        assert data["id"] == movie_id
        assert data["name"] == movie_data["name"]
        assert data["location"] == movie_data["location"]

    # Негативные тесты

    def test_create_movie_without_name(self, api_manager: ApiManager):
        """
        Создание фильма без авторизации
        """
        movie_data = {'name': 'neavtorizovan Movie','discriptoin': fake.text()}
        api_manager.movies_api.create_movie(movie_data, expected_status=401)

    def test_create_movie_user(self, api_manager: ApiManager, authenticated_user):
        '''
        Обычный пользователь не может создать фильм
        '''
        movie_data = {'name': 'neavtorizovan Movie', 'discriptoin': fake.text()}
        api_manager.movies_api.create_movie(movie_data, expected_status=403)

    def test_get_no_movie(self, api_manager: ApiManager):
        '''
        Получение несущевствующего фильма
        '''
        api_manager.movies_api.create_movie(fake.text(), expected_status=400)


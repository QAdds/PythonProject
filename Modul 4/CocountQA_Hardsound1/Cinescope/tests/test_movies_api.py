import pytest
from api.api_manager import ApiManager
from faker import Faker

from conftest import api_manager

fake = Faker()


class TestMoviesApi:

    # ===================== ПОЗИТИВНЫЕ ТЕСТЫ =====================

    def test_create_movie_by_admin(self, api_manager: ApiManager, authenticated_admin):
        '''Тест проверяет создание фильма администратором'''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
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
        assert data["price"] == movie_data["price"]
        assert data["location"] == movie_data["location"]
        assert data["published"] is True


    def test_get_all_movies(self, api_manager: ApiManager):
        '''Получение списка всех фильмов'''
        response = api_manager.movies_api.get_all_movies(expected_status=200)
        data = response.json()

        assert "movies" in data, "Список фильмов отсутствует в ответе"
        assert "count" in data, "Отсутствует поле count"


    def test_get_movie_by_id(self, api_manager: ApiManager, authenticated_admin):
        '''Получение фильма по ID'''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 1000,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }

        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        response = api_manager.movies_api.get_movie(movie_id, expected_status=200)
        data = response.json()

        assert data["id"] == movie_id
        assert data["name"] == movie_data["name"]


    # ===================== НЕГАТИВНЫЕ ТЕСТЫ =====================

    def test_create_movie_without_auth(self, api_manager: ApiManager):
        '''Неавторизованный пользователь не может создать фильм (401)'''
        if 'authorization' in api_manager.movies_api.session.headers:
            del api_manager.movies_api.session.headers['authorization']

        movie_data = {
            "name": "Movie without auth",
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }

        api_manager.movies_api.create_movie(movie_data, expected_status=401)


    def test_create_movie_by_regular_user(self, api_manager: ApiManager, authenticated_user):
        '''Обычный пользователь не может создать фильм (403)'''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }

        api_manager.movies_api.create_movie(movie_data, expected_status=403)


    def test_create_movie_invalid_data(self, api_manager: ApiManager, authenticated_admin):
        '''Создание фильма с некорректными данными возвращает 400'''
        movie_data = {
            "name": "",           # пустое обязательное поле
            "price": -100,        # некорректная цена
            "genreId": 99999      # несуществующий жанр
        }

        api_manager.movies_api.create_movie(movie_data, expected_status=400)


    def test_get_nonexistent_movie(self, api_manager: ApiManager):
        '''Получение несуществующего фильма возвращает 404'''
        api_manager.movies_api.get_movie(9999999, expected_status=404)

    def test_admin_can_update_movie(self, api_manager: ApiManager, authenticated_admin):
        ''' Super Admin мщжут обновить фильм'''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }
        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]
        update_data = {
            "name": fake.name(),
            "price": 500,
            "description": fake.text(),
            "location": "MSK",
        }
        response=api_manager.movies_api.patch_movie(movie_id, update_data, expected_status=200)
        data = response.json()
        assert data["id"] == movie_id
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        assert data["description"] == update_data["description"]

    def test_admin_can_delete_movie(self, api_manager: ApiManager, authenticated_admin):
        ''' Super Admin может удалить фильм'''
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }
        create_response= api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id=create_response.json()["id"]
        #удаляем фильм
        api_manager.movies_api.delete_movie(movie_id, expected_status=200)
        api_manager.movies_api.get_movie(movie_id, expected_status=404)

    def test_regular_user_cannot_delete_movie(self, api_manager: ApiManager, authenticated_admin, authenticated_user):
        '''Обычный пользователь не может удалять фильмы (403)'''
        # Создаём фильм под админом
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1
        }
        # Явно переключаемся на админа перед созданием
        api_manager.movies_api.session.headers['authorization'] = f"Bearer {authenticated_admin['accessToken']}"

        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        # === 2. Переключаемся на обычного пользователя ===
        api_manager.movies_api.session.headers['authorization'] = f"Bearer {authenticated_user['accessToken']}"

        # === 3. Пытаемся удалить ===
        api_manager.movies_api.delete_movie(movie_id, expected_status=403)

    def test_admin_can_delete_movie(self, api_manager: ApiManager, authenticated_admin):
        '''SUPER_ADMIN может успешно удалить фильм'''
        movie_data = {
            "name": f"Фильм_для_удаления_{fake.unique.word().capitalize()}",
            "imageUrl": "https://example.com/to_delete.jpg",
            "price": 800,
            "description": "Будет удалён",
            "location": "SPB",
            "published": True,
            "genreId": 1
        }

        # Явно используем токен админа
        api_manager.movies_api.session.headers['authorization'] = f"Bearer {authenticated_admin['accessToken']}"

        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        # Удаляем
        api_manager.movies_api.delete_movie(movie_id, expected_status=200)

        # Проверяем, что фильм удалён
        api_manager.movies_api.get_movie(movie_id, expected_status=404)

        
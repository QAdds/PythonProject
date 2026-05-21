import pytest
import allure
from api.api_manager import ApiManager
from faker import Faker
from models.movie_models import MoviesListResponse

fake = Faker()


class TestMoviesApi:
    # ПОЗИТИВНЫЕ ТЕСТЫ

    @allure.epic("Cinescope API")
    @allure.feature("Movies API")
    @allure.story("Создание фильма администратором")
    @allure.title("Администратор может создать фильм с валидными данными")
    @allure.description(
        "Тест проверяет, что администратор может создать фильм через Movies API, "
        "и в ответе возвращаются корректные данные созданного фильма."
    )
    @pytest.mark.smoke
    def test_create_movie_by_admin(self, api_manager: ApiManager, authenticated_admin):
        """Тест проверяет создание фильма администратором."""
        with allure.step("Подготовить данные фильма для создания"):
            movie_data = {
                "name": fake.name(),
                "imageUrl": "https://example.com/image.jpg",
                "price": 100,
                "description": fake.text(),
                "location": "SPB",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Отправить запрос на создание фильма от имени администратора"):
            response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
            data = response.json()

        with allure.step("Проверить, что фильм успешно создан и поля совпадают с отправленными"):
            assert "id" in data, "ID фильма отсутствует в ответе"
            assert data["name"] == movie_data["name"]
            assert data["price"] == movie_data["price"]
            assert data["location"] == movie_data["location"]
            assert data["published"] is True

    # == PYDANTIC model =====
    @pytest.mark.smoke
    def test_get_all_movies(self, api_manager: ApiManager):
        """Получение списка всех фильмов и проверка схемы ответа."""
        response = api_manager.movies_api.get_all_movies(expected_status=200)
        movies_response = MoviesListResponse(**response.json())

        assert isinstance(movies_response.count, int)
        assert isinstance(movies_response.movies, list)


    @pytest.mark.regression
    def test_get_movie_by_id(self, api_manager: ApiManager, authenticated_admin):
        """Получение фильма по ID."""
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 1000,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1,
        }

        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        response = api_manager.movies_api.get_movie(movie_id, expected_status=200)
        data = response.json()

        assert data["id"] == movie_id
        assert data["name"] == movie_data["name"]

    # НЕГАТИВНЫЕ ТЕСТЫ

    @pytest.mark.smoke
    def test_create_movie_without_auth(self, guest_api_manager: ApiManager):
        """Неавторизованный пользователь не может создать фильм (401)."""
        if "authorization" in guest_api_manager.movies_api.session.headers:
            del guest_api_manager.movies_api.session.headers["authorization"]

        movie_data = {
            "name": "Movie without auth",
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1,
        }

        guest_api_manager.movies_api.create_movie(movie_data, expected_status=401)

    @pytest.mark.regression
    def test_create_movie_by_regular_user(self, api_manager: ApiManager, authenticated_user):
        """Обычный пользователь не может создать фильм (403)."""
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1,
        }

        api_manager.movies_api.create_movie(movie_data, expected_status=403)

    # == ЗАДАНИЕ ПО ПАРАМЕТРИЗАЦИИ =====
    @allure.epic("Cinescope API")
    @allure.feature("Movies API")
    @allure.story("Валидация создания фильма")
    @allure.title("Создание фильма с невалидными данными возвращает ошибку")
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "movie_data, expected_status",
        [
            (
                    {
                        "name": "",
                        "imageUrl": "https://example.com/image.jpg",
                        "price": 100,
                        "description": "test",
                        "location": "SPB",
                        "published": True,
                        "genreId": 1,
                    },
                    400,
            ),
            (
                    {
                        "name": "Bad image movie",
                        "imageUrl": "",
                        "price": 100,
                        "description": "test",
                        "location": "SPB",
                        "published": True,
                        "genreId": 1,
                    },
                    400,
            ),
            (
                    {
                        "name": "Bad genre movie",
                        "imageUrl": "https://example.com/image.jpg",
                        "price": 100,
                        "description": "test",
                        "location": "SPB",
                        "published": True,
                        "genreId": 99999,
                    },
                    400,
            ),
        ],
        ids=[
            "empty_name",
            "empty_image_url",
            "invalid_genre_id",
        ],
    )
    def test_create_movie_invalid_data(
            self,
            api_manager: ApiManager,
            authenticated_admin,
            movie_data,
            expected_status,
    ):
        """Создание фильма с некорректными данными возвращает ошибку."""
        with allure.step("Отправить запрос на создание фильма с невалидными данными"):
            api_manager.movies_api.create_movie(movie_data, expected_status=expected_status)

    @pytest.mark.regression
    def test_get_nonexistent_movie(self, api_manager: ApiManager):
        """Получение несуществующего фильма возвращает 404."""
        api_manager.movies_api.get_movie(9999999, expected_status=404)

    @pytest.mark.smoke
    def test_admin_can_update_movie(self, api_manager: ApiManager, authenticated_admin):
        """Super Admin может обновить фильм."""
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1,
        }
        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        update_data = {
            "name": fake.name(),
            "price": 500,
            "description": fake.text(),
            "location": "MSK",
        }
        response = api_manager.movies_api.patch_movie(movie_id, update_data, expected_status=200)
        data = response.json()

        assert data["id"] == movie_id
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        assert data["description"] == update_data["description"]

    @pytest.mark.smoke
    def test_admin_can_delete_movie(self, api_manager: ApiManager, authenticated_admin):
        """Super Admin может удалить фильм."""
        movie_data = {
            "name": fake.name(),
            "imageUrl": "https://example.com/image.jpg",
            "price": 500,
            "description": fake.text(),
            "location": "SPB",
            "published": True,
            "genreId": 1,
        }
        create_response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
        movie_id = create_response.json()["id"]

        api_manager.movies_api.delete_movie(movie_id, expected_status=200)
        api_manager.movies_api.get_movie(movie_id, expected_status=404)

    ### === ВЫПОЛНЕНИЕ ЗАПРОСА В БД =====
    @allure.epic("Cinescope API")
    @allure.feature("Movies API")
    @allure.story("Создание фильма с проверкой в БД")
    @allure.title("После создания фильма через API запись появляется в БД")
    @pytest.mark.regression
    def test_create_movie_saved_in_db(self, api_manager: ApiManager, authenticated_admin, db_helper):
        """Проверка, что после создания фильма через API запись появляется в БД."""
        with allure.step("Подготовить данные фильма"):
            movie_data = {
                "name": fake.name(),
                "imageUrl": "https://example.com/image.jpg",
                "price": 100,
                "description": fake.text(),
                "location": "SPB",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Создать фильм через API"):
            response = api_manager.movies_api.create_movie(movie_data, expected_status=201)
            response_data = response.json()
            movie_id = response_data["id"]

        with allure.step("Получить фильм из БД по id"):
            db_movie = db_helper.get_movie_by_id(movie_id)

        with allure.step("Проверить, что фильм есть в БД и его поля совпадают"):
            assert db_movie is not None, "Фильм не найден в БД"
            assert db_movie.id == movie_id
            assert db_movie.name == movie_data["name"]
            assert db_movie.price == movie_data["price"]
            assert db_movie.description == movie_data["description"]
            assert db_movie.image_url == movie_data["imageUrl"]
            assert str(db_movie.location) == movie_data["location"]
            assert db_movie.published == movie_data["published"]
            assert db_movie.genre_id == movie_data["genreId"]
from faker import Faker
import pytest
import requests
from api.api_manager import ApiManager
from constants import BASE_URL, REGISTER_ENDPOINT
from custom_requester.data_generator import DataGenerator

fake = Faker()

@pytest.fixture(scope="session")
def session():
    """Фикстура для создания HTTP-сессии."""
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """Фикстура для создания экземпляра ApiManager."""
    return ApiManager(session)

@pytest.fixture(scope="session")
def test_user():
    """Генерация случайного пользователя для тестов."""
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="session")
def registered_user(api_manager, test_user):
    """Регистрирует пользователя и возвращает его данные с id."""
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user
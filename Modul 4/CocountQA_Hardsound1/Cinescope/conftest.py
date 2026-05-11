import os

import pytest
import requests
from dotenv import load_dotenv
from faker import Faker

from api.api_manager import ApiManager
from custom_requester.data_generator import DataGenerator

load_dotenv()

fake = Faker()


@pytest.fixture(scope="function")
def session():
    """Фикстура для создания HTTP-сессии."""
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="function")
def api_manager(session):
    """Авторизуемый API manager на обычной сессии."""
    return ApiManager(session)


@pytest.fixture(scope="function")
def guest_session():
    """Отдельная гостевая сессия без токена."""
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="function")
def guest_api_manager(guest_session):
    """Гостевой API manager без авторизации."""
    return ApiManager(guest_session)


@pytest.fixture(scope="function")
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
        "roles": ["USER"],
    }


@pytest.fixture(scope="function")
def admin_user():
    """Данные администратора из переменных окружения."""
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        raise ValueError("Не заданы ADMIN_EMAIL / ADMIN_PASSWORD в переменных окружения")

    return {
        "email": email,
        "password": password,
        "fullName": "Super Admin",
        "roles": ["SUPER_ADMIN"],
    }


@pytest.fixture(scope="function")
def authenticated_admin(api_manager, admin_user):
    """Логин под администратором и установка токена."""
    api_manager.auth_api.authenticate(admin_user)
    return admin_user


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    """Регистрация пользователя и возврат данных с id."""
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()

    user_data = test_user.copy()
    user_data["id"] = response_data["id"]
    return user_data


@pytest.fixture(scope="function")
def authenticated_user(api_manager, registered_user):
    """Регистрация пользователя, логин и установка токена."""
    api_manager.auth_api.authenticate(registered_user)
    return registered_user

@pytest.fixture(scope="function")
def other_user(api_manager):
    user_data = {
        "email": fake.email(),
        "fullName": fake.name(),
        "password": "Qwerty123!",
        "passwordRepeat": "Qwerty123!",
        "roles": ["USER"]
    }

    response = api_manager.auth_api.register_user(user_data)
    response_data = response.json()

    user_data["id"] = response_data["id"]
    return user_data
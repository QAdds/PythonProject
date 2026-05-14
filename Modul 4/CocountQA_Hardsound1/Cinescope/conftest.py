import os
import pytest
import requests
from dotenv import load_dotenv
from faker import Faker

from api.api_manager import ApiManager
from custom_requester.data_generator import DataGenerator
from entities.user import User
from enums.roles import Roles
from resources.user_creds import SuperAdminCreds
from enums.roles import Roles

load_dotenv()
fake = Faker()

# МОДУЛЬ 4

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
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }


@pytest.fixture(scope="function")
def admin_user():
    """Данные администратора из переменных окружения."""
    email = os.getenv("SUPER_ADMIN_USERNAME")
    password = os.getenv("SUPER_ADMIN_PASSWORD")

    if not email or not password:
        raise ValueError("Не заданы ADMIN_EMAIL / ADMIN_PASSWORD в переменных окружения")

    return {
        "email": email,
        "password": password,
        "fullName": "Super Admin",
        "roles": [Roles.SUPER_ADMIN.value],
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
    '''Генерирует случайные email и fullName'''
    user_data = {
        "email": fake.email(),
        "fullName": fake.name(),
        "password": "Qwerty123!",
        "passwordRepeat": "Qwerty123!",
        "roles": [Roles.USER.value]
    }

    response = api_manager.auth_api.register_user(user_data)
    response_data = response.json()

    user_data["id"] = response_data["id"]
    return user_data

# МОДУЛЬ 5

@pytest.fixture(scope='function')
def user_session(api_manager):
    '''управляет жизненным циклом пользовательских сессий для API-тестов'''
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        api_manager = ApiManager(session)
        user_pool.append(api_manager)
        return api_manager

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture(scope="function")
def super_admin(user_session):
    '''создает и настраивает объект пользователя с ролью суперадминистратора '''
    new_session = user_session()

    super_admin = User(
        email=SuperAdminCreds.USERNAME,
        password=SuperAdminCreds.PASSWORD,
        roles=[Roles.SUPER_ADMIN.value],
        api=new_session
    )

    super_admin.api.auth_api.authenticate({
        "email": super_admin.email,
        "password": super_admin.password
    })
    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    '''Обновленная фикстура ("test_user" Генерация случайного пользователя для тестов)'''
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    '''создание обычного юзера с ролью USER'''
    new_session = user_session()

    common_user = User(
        email=creation_user_data["email"],
        password=creation_user_data["password"],
        roles=[Roles.USER.value],
        api=new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate({
        "email": common_user.email,
        "password": common_user.password
    })
    return common_user
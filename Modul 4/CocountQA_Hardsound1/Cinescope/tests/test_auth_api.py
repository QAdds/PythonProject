from api.api_manager import ApiManager
from faker import Faker
from enums.roles import Roles
from models.base_models import RegisterUserResponse, TestUser
import pytest
import allure

fake = Faker()


class TestAuthAPI:

    # ПОЗИТИВНЫЕ ТЕСТЫ

    @allure.epic("Cinescope API")
    @allure.feature("Auth API")
    @allure.story("Регистрация пользователя")
    @allure.title("Пользователь может зарегистрироваться с валидными данными")
    @allure.description(
        "Тест проверяет, что при регистрации нового пользователя через Auth API "
        "возвращается корректный email и роль USER.")
    @pytest.mark.regression
    def test_register_user(self, api_manager: ApiManager, test_user: TestUser):
        """Тест на регистрацию пользователя."""
        with allure.step("Отправить запрос на регистрацию нового пользователя"):
            response = api_manager.auth_api.register_user(user_data=test_user)

        with allure.step("Преобразовать JSON-ответ в модель RegisterUserResponse"):
            register_user_response = RegisterUserResponse(**response.json())

        with allure.step("Проверить email и роль пользователя в ответе"):
            assert register_user_response.email == test_user.email, "Email не совпадает"
            assert Roles.USER in register_user_response.roles, "Роль USER отсутствует"

    @allure.epic("Cinescope API")
    @allure.feature("Auth API")
    @allure.story("Регистрация и авторизация пользователя")
    @allure.title("Пользователь может авторизоваться после регистрации")
    @allure.description(
        "Тест проверяет, что зарегистрированный пользователь может авторизоваться, "
        "и в ответе возвращаются корректный email и accessToken.")
    @pytest.mark.regression
    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """Тест на регистрацию и авторизацию пользователя."""
        with allure.step("Подготовить данные для авторизации пользователя"):
            login_data = {
                "email": registered_user.email,
                "password": registered_user.password,
            }

        with allure.step("Отправить запрос на логин пользователя"):
            response = api_manager.auth_api.login_user(login_data)
            response_data = response.json()

        with allure.step("Проверить email пользователя в ответе"):
            assert response_data["user"]["email"] == registered_user.email, "Email не совпадает"

        with allure.step("Проверить, что в ответе есть токен доступа"):
            assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"

    # НЕГАТИВНЫЕ ТЕСТЫ

    @pytest.mark.regression
    def test_error_password(self, api_manager: ApiManager, registered_user):
        """Тест на авторизацию с неправильным паролем."""
        login_data = {
            "email": registered_user.email,
            "password": "WrongPassword123!"
        }
        api_manager.auth_api.login_user(login_data, expected_status=401)

    @pytest.mark.regression
    def test_login_no_email(self, api_manager: ApiManager):
        """Тест: Ошибка при логине с несуществующим email."""
        login_data = {
            "email": "nonexistent123456789@gmail.com",
            "password": "AnyPassword123!"
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)
        response_data = response.json()

        assert response_data.get("error") == "Unauthorized", "Ожидалась ошибка Unauthorized"
        assert "Неверный логин или пароль" in response_data.get("message", ""), "Сообщение об ошибке не совпадает"

    @pytest.mark.regression
    def test_registration_with_existing_email(self, api_manager: ApiManager, registered_user):
        """Тест: Ошибка при регистрации с уже существующим email."""

        duplicate_user = TestUser(
            email=registered_user.email,
            fullName="Duplicate User",
            password="Password123!",
            passwordRepeat="Password123!",
            roles=[Roles.USER]
        )

        response = api_manager.auth_api.register_user(duplicate_user, expected_status=409)
        data = response.json()

        assert data.get("statusCode") == 409
        assert "Пользователь с таким email уже зарегистрирован" in data.get("message", "")

    @pytest.mark.regression
    def test_register_admin_by_superadmin(self, api_manager: ApiManager, authenticated_admin):
        """Попытка создания SUPER_ADMIN через авторизованного администратора,
        но создается пользователь с ролью USER """

        unique_email = f"newadmin_{fake.unique.random_int(min=10000, max=99999)}@gmail.com"

        admin_data = {
            "email": unique_email,
            "fullName": "Created by Test Admin",
            "password": "asdqwe123Q",
            "passwordRepeat": "asdqwe123Q",
            "roles": [Roles.SUPER_ADMIN.value]
        }

        response = api_manager.auth_api.register_admin(admin_data, expected_status=201)
        data = response.json()
        assert data["email"] == admin_data["email"]
        assert data["fullName"] == admin_data["fullName"]
        assert data['roles'] == [Roles.USER.value]
from api.api_manager import ApiManager
from faker import Faker
fake = Faker()

class TestAuthAPI:

    # ПОЗИТИВНЫЕ ТЕСТЫ

    def test_register_user(self, api_manager: ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"
        assert response.status_code == 201, "Статус код не 201"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()
        assert response_data['user']["email"] == registered_user["email"], 'Email не совпадает'
        assert 'accessToken' in response_data, 'Токен доступа отсутствует в ответе'

    # НЕГАТИВНЫЕ ТЕСТЫ

    def test_error_password(self, api_manager: ApiManager, registered_user):
        '''
        Тест на авторизацию с неправильным паролем
        '''
        login_data = {
           'email': registered_user['email'],
           'password': 'WrongPassword123!'
        }
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_login_no_email(self, api_manager: ApiManager):
        '''
        Тест: Ошибка при логине с несущевствующим email.
        '''
        login_data = {
            "email": "nonexistent123456789@gmail.com",
            "password": "AnyPassword123!"
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)
        response_data = response.json()
        assert response_data.get("error") == "Unauthorized", "Ожидалась ошибка Unauthorized"
        assert "Неверный логин или пароль" in response_data.get("message", ""), "Сообщение об ошибке не совпадает"

    def test_registration_with_existing_email(self, api_manager: ApiManager, registered_user):
        """
        Тест: Ошибка при регистрации с уже существующим email.
        """
        duplicate_user = {
            "email": registered_user["email"],
            "fullName": "Duplicate User",
            "password": "Password123!",
            "passwordRepeat": "Password123!",
            "roles": ["USER"]
        }

        response = api_manager.auth_api.register_user(duplicate_user, expected_status=409)
        data = response.json()

        assert data.get("statusCode") == 409
        assert "Пользователь с таким email уже зарегистрирован" in data.get("message", "")

    def test_register_admin_by_superadmin(self, api_manager: ApiManager, authenticated_admin):
        """
        Попытка создания SUPER_ADMIN через авторизованного администратора.
        """
        unique_email = f"newadmin_{fake.unique.random_int(min=10000, max=99999)}@gmail.com"

        admin_data = {
            "email": unique_email,
            "fullName": "Created by Test Admin",
            "password": "asdqwe123Q",
            "passwordRepeat": "asdqwe123Q",
            "roles": ["SUPER_ADMIN"]
        }
        response = api_manager.auth_api.register_admin(admin_data, expected_status=400)
        data = response.json()
        assert data.get("statusCode") == 400

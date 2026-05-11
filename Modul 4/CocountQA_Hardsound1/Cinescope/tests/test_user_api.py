from api.api_manager import ApiManager

class TestUserAPI:

    # ПОЗИТИВНЫЕ ТЕСТЫ

    def test_delete_user_by_admin(self, api_manager: ApiManager, authenticated_admin, test_user):
        """
        Тест: Администратор может удалить пользователя.
        """
        # Создаем пользователя
        reg_response = api_manager.auth_api.register_user(test_user, expected_status=201)
        user_id = reg_response.json()["id"]

        # Удаляем пользователя
        api_manager.user_api.delete_user(user_id, expected_status=200)

        # Проверяем что сделал удаление пользователя
        get_response = api_manager.user_api.get_user_info(user_id, expected_status=200)
        assert get_response.json() == {}

    def test_get_user_info_by_admin(self, api_manager: ApiManager, authenticated_admin, registered_user):
        """
        Тест: Администратор может получить информацию о любом пользователе.
        """
        user_id = registered_user["id"]
        response = api_manager.user_api.get_user_info(user_id, expected_status=200)
        data = response.json()

        assert data["id"] == user_id
        assert data["email"] == registered_user["email"]

    # НЕГАТИВНЫЕ ТЕСТЫ

    def test_delete_user_without_permission(self, api_manager: ApiManager, authenticated_user, other_user):
        ''' Удалить пользователя без разрешения'''

        response = api_manager.user_api.delete_user(other_user["id"], expected_status=403)
        data= response.json()

        assert data["statusCode"] == 403
        assert data["message"] == "Forbidden"

    def test_regular_user_cannot_get_user_info(self, api_manager: ApiManager, authenticated_user):
        """Обычный пользователь не может получить информацию о себе"""
        user_id = authenticated_user["id"]
        response = api_manager.user_api.get_user_info(user_id, expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["error"] == "Forbidden"
        assert data["message"] == "Forbidden resource"
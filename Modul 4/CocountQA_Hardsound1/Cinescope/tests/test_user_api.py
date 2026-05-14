from api.api_manager import ApiManager

class TestUserAPI:
    # Позитивные тесты

    def test_delete_user_by_admin(self, api_manager: ApiManager, authenticated_admin, test_user):
        """Администратор может удалить пользователя."""

        reg_response = api_manager.auth_api.register_user(test_user, expected_status=201)
        user_id = reg_response.json()["id"]

        api_manager.user_api.delete_user(user_id, expected_status=200)

        get_response = api_manager.user_api.get_user(user_id, expected_status=200)
        assert get_response.json() == {}

    def test_get_user_info_by_admin(self, api_manager: ApiManager, authenticated_admin, registered_user):
        """Администратор может получить информацию о пользователе."""

        user_id = registered_user["id"]
        response = api_manager.user_api.get_user(user_id, expected_status=200)
        data = response.json()

        assert data["id"] == user_id
        assert data["email"] == registered_user["email"]

    # Негативные тесты

    def test_delete_user_without_permission(self, api_manager: ApiManager, authenticated_user, other_user):
        """Обычный пользователь не может удалить другого пользователя."""

        response = api_manager.user_api.delete_user(other_user["id"], expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["message"] == "Forbidden"

    def test_regular_user_cannot_get_user_info(self, api_manager: ApiManager,authenticated_user):
        """Обычный пользователь не может получить информацию о пользователе."""

        user_id = authenticated_user["id"]
        response = api_manager.user_api.get_user(user_id, expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["error"] == "Forbidden"
        assert data["message"] == "Forbidden resource"


class TestUserRoleModel:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data, expected_status=201).json()

        assert response.get("id"), "ID должен быть не пустым"
        assert response["email"] == creation_user_data["email"]
        assert response["fullName"] == creation_user_data["fullName"]
        assert response["roles"] == creation_user_data["roles"]
        assert response["verified"] is True
        assert response["banned"] is False

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data, expected_status=201).json()

        response_by_id = super_admin.api.user_api.get_user(created_user_response["id"], expected_status=200).json()

        response_by_email = super_admin.api.user_api.get_user(creation_user_data["email"],expected_status=200).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get("id"), "ID должен быть не пустым"
        assert response_by_id["email"] == creation_user_data["email"]
        assert response_by_id["fullName"] == creation_user_data["fullName"]
        assert response_by_id["roles"] == creation_user_data["roles"]
        assert response_by_id["verified"] is True
        assert response_by_id["banned"] is False

    def test_get_user_by_id_common_user(self, common_user):
        response = common_user.api.user_api.get_user(common_user.email, expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["error"] == "Forbidden"
        assert data["message"] == "Forbidden resource"
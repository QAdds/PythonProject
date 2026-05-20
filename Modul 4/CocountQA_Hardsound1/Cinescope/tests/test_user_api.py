from api.api_manager import ApiManager
from models.base_models import TestUser
from pytest_check import check
import pytest
import allure
import json

class TestUserAPI:
    # Позитивные тесты

    @pytest.mark.smoke
    def test_delete_user_by_admin(self, api_manager: ApiManager, authenticated_admin, test_user):
        """Администратор может удалить пользователя."""

        reg_response = api_manager.auth_api.register_user(test_user, expected_status=201)
        user_id = reg_response.json()["id"]

        api_manager.user_api.delete_user(user_id, expected_status=200)

        get_response = api_manager.user_api.get_user(user_id, expected_status=200)
        assert get_response.json() == {}

    @allure.epic("Cinescope API")
    @allure.feature("User API")
    @allure.story("Получение информации о пользователе администратором")
    @allure.title("Администратор может получить информацию о пользователе по id")
    @allure.description(
        "Тест проверяет, что администратор может запросить информацию о существующем пользователе, "
        "и сервис возвращает корректный id и email."
    )
    @pytest.mark.slow
    def test_get_user_info_by_admin(self, api_manager: ApiManager, authenticated_admin, registered_user):
        """Администратор может получить информацию о пользователе."""
        with allure.step("Подготовить id зарегистрированного пользователя"):
            user_id = registered_user.id

        with allure.step("Отправить запрос на получение информации о пользователе от имени администратора"):
            response = api_manager.user_api.get_user(user_id, expected_status=200)
            data = response.json()

        with allure.step("Проверить, что в ответе возвращён корректный id и email"):
            assert data["id"] == user_id
            assert data["email"] == registered_user.email

    # Негативные тесты

    @pytest.mark.slow
    def test_delete_user_without_permission(self, api_manager: ApiManager, authenticated_user, other_user):
        """Обычный пользователь не может удалить другого пользователя."""

        response = api_manager.user_api.delete_user(other_user.id, expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["message"] == "Forbidden"

    @pytest.mark.slow
    def test_regular_user_cannot_get_user_info(self, api_manager: ApiManager,authenticated_user):
        """Обычный пользователь не может получить информацию о пользователе."""

        user_id = authenticated_user.id
        response = api_manager.user_api.get_user(user_id, expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["error"] == "Forbidden"
        assert data["message"] == "Forbidden resource"


class TestUserRoleModel:

    @pytest.mark.smoke
    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data, expected_status=201).json()

        assert response.get("id"), "ID должен быть не пустым"
        assert response["email"] == creation_user_data.email
        assert response["fullName"] == creation_user_data.fullName
        assert response["roles"] == creation_user_data.roles
        assert response["verified"] is True
        assert response["banned"] is False

    @pytest.mark.smoke
    def test_get_user_by_locator(self, super_admin, creation_user_data: TestUser):
        with allure.step("Создать пользователя через User API от имени супер-фдмина"):
            created_user_response = super_admin.api.user_api.create_user(creation_user_data, expected_status=201).json()

            allure.attach(json.dumps(created_user_response, ensure_ascii=False, indent=2), name="created_user_response.json", attachment_type=allure.attachment_type.JSON,)
        with allure.step("Получить пользователя по id"):
            response_by_id = super_admin.api.user_api.get_user(created_user_response["id"], expected_status=200).json()
        with allure.step("Получение пользователя по email"):
            response_by_email = super_admin.api.user_api.get_user(creation_user_data.email,expected_status=200).json()

        with allure.step("Логировать ответы по id и по email"):
            allure.attach(
                json.dumps(response_by_id, ensure_ascii=False, indent=2),
                name="response_by_id.json",
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                json.dumps(response_by_email, ensure_ascii=False, indent=2),
                name="response_by_email.json",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Сравнить ответы и проверить ключевые поля пользователя (soft asserts)"):
            with check:
                check.equal(response_by_id, response_by_email, "Содержание ответов должно быть идентичным")
                check.is_true(bool(response_by_id.get("id")),"ID должен быть не пустым")
                check.equal(response_by_id["email"], creation_user_data.email, "Email не совпадает")
                check.equal(response_by_id["fullName"], creation_user_data.fullName, "fullName не совпадает")
                check.equal(response_by_id["roles"], creation_user_data.roles, "roles не совпадают")
                check.is_true(response_by_id["verified"], "Флаг verified должен быть True")
                check.is_false(response_by_id["banned"], "Флаг banned должен быть False")
                
    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        response = common_user.api.user_api.get_user(common_user.email, expected_status=403)
        data = response.json()

        assert data["statusCode"] == 403
        assert data["error"] == "Forbidden"
        assert data["message"] == "Forbidden resource"
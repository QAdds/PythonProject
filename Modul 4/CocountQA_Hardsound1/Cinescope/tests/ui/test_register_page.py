import allure
import pytest
from pages.register_page import CinescopeRegisterPage
from custom_requester.data_generator import DataGenerator


@allure.epic("ui")
@allure.feature("Register page")
@pytest.mark.ui
class TestRegisterPage:

    @allure.title("Успешная регистрация через ui")
    def test_register_by_ui(self, page):
        register_page = CinescopeRegisterPage(page)

        email = DataGenerator.generate_random_email()
        name = DataGenerator.generate_random_name()
        password = DataGenerator.generate_random_password()

        register_page.open()
        register_page.register(
            full_name=f"PlaywrightTest {name}",
            email=email,
            password=password,
            confirm_password=password
        )

        register_page.assert_redirect_to_login_page()
        register_page.attach_screenshot("register_success")
        register_page.assert_register_success_popup()
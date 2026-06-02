import allure
import pytest
from pages.login_page import CinescopeLoginPage


@allure.epic("ui")
@allure.feature("Login page")
@pytest.mark.ui
class TestLoginPage:

    @allure.title("Успешный вход через ui")
    def test_login_by_ui(self, page, registered_user):
        login_page = CinescopeLoginPage(page)

        login_page.open()
        login_page.login(registered_user.email, registered_user.password)

        login_page.assert_redirect_to_home_page()
        login_page.attach_screenshot("login_success")
        login_page.assert_login_success_popup()


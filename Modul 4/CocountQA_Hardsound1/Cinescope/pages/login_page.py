import allure
from pages.base_page import BasePage


class CinescopeLoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{self.BASE_URL}login"

        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль")
        self.login_button = page.locator("form button[type='submit']")
        self.register_link = page.get_by_role("link", name="Зарегистрироваться")

    @allure.step("Открыть страницу логина")
    def open(self):
        self.open_url(self.url)

    @allure.step("Выполнить логин")
    def login(self, email: str, password: str):
        self.fill(self.email_input, email)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    @allure.step("Проверить редирект на главную")
    def assert_redirect_to_home_page(self):
        self.wait_for_url(self.BASE_URL)

    @allure.step("Проверить уведомление об успешном входе")
    def assert_login_success_popup(self):
        self.assert_popup_text("Вы вошли в аккаунт")
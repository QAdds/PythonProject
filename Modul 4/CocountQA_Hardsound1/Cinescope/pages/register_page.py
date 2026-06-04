import allure
from pages.base_page import BasePage


class CinescopeRegisterPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{self.BASE_URL}register"

        self.full_name_input = page.get_by_role("textbox", name="Имя Фамилия Отчество")
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль", exact=True)
        self.repeat_password_input = page.get_by_role("textbox", name="Повторите пароль")
        self.register_button = page.get_by_role("button", name="Зарегистрироваться")
        self.login_link = page.get_by_role("link", name="Войти")

    @allure.step("Открыть страницу регистрации")
    def open(self):
        self.open_url(self.url)

    @allure.step("Выполнить регистрацию")
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.fill(self.full_name_input, full_name)
        self.fill(self.email_input, email)
        self.fill(self.password_input, password)
        self.fill(self.repeat_password_input, confirm_password)
        self.click(self.register_button)

    @allure.step("Проверить редирект на логин")
    def assert_redirect_to_login_page(self):
        self.wait_for_url(f"{self.BASE_URL}login")

    @allure.step("Проверить уведомление после регистрации")
    def assert_register_success_popup(self):
        self.assert_popup_text("Подтвердите свою почту")
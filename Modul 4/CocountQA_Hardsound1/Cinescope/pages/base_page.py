import allure
from playwright.sync_api import Page, expect


class PageActions:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Открыть страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Клик по элементу")
    def click(self, locator):
        locator.click()

    @allure.step("Ввести текст: {text}")
    def fill(self, locator, text: str):
        locator.fill(text)

    @allure.step("Дождаться URL: {url}")
    def wait_for_url(self, url: str):
        self.page.wait_for_url(url)
        expect(self.page).to_have_url(url)

    @allure.step("Проверить pop-up с текстом: {text}")
    def assert_popup_text(self, text: str):
        popup = self.page.get_by_text(text)
        expect(popup).to_be_visible()
        popup.wait_for(state="hidden")

    @allure.step("Сделать скриншот")
    def attach_screenshot(self, name: str = "screenshot"):
        path = f"{name}.png"
        self.page.screenshot(path=path, full_page=True)
        allure.attach.file(path, name=name, attachment_type=allure.attachment_type.PNG)


class BasePage(PageActions):
    BASE_URL = "https://dev-cinescope.coconutqa.ru/"

    def __init__(self, page: Page):
        super().__init__(page)
        self.home_link = page.get_by_role("link", name="Cinescope")
        self.all_movies_link = page.get_by_role("link", name="Все фильмы")

    @allure.step("Перейти на главную страницу")
    def go_to_home_page(self):
        self.click(self.home_link)
        self.wait_for_url(self.BASE_URL)

    @allure.step("Перейти на страницу 'Все фильмы'")
    def go_to_all_movies_page(self):
        self.click(self.all_movies_link)
        self.wait_for_url(f"{self.BASE_URL}movies")
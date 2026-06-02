import allure
from playwright.sync_api import expect
from pages.base_page import BasePage


class ReviewMoviesPage(BasePage):
    def __init__(self, page):
        super().__init__(page)

        self.review_input = page.get_by_placeholder('Написать отзыв')
        self.submit_review_button = page.get_by_role("button", name="Отправить")

    @allure.step("Открыть страницу фильма")
    def open_movie_page(self, movie_id: int = 2448):
        self.open_url(f"{self.BASE_URL}movies/{movie_id}")

    @allure.step("Ввести текст отзыва")
    def fill_review(self, review_text: str):
        self.fill(self.review_input, review_text)

    @allure.step("Отправить отзыв")
    def submit_review(self):
        self.click(self.submit_review_button)

    @allure.step("Проверить, что отзыв отображается")
    def assert_review_visible(self, review_text: str):
        expect(self.page.get_by_text(review_text)).to_be_visible()
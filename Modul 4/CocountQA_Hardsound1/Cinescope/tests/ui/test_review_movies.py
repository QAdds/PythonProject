import allure
import pytest
from pages.login_page import CinescopeLoginPage
from pages.review_movies_page import ReviewMoviesPage


@allure.epic("ui")
@allure.feature("Movie review")
@pytest.mark.ui
@pytest.mark.review
class TestReviewMoviesPage:

    @allure.title("Авторизованный пользователь может оставить отзыв под фильмом")
    def test_add_review_to_movie(self, page, registered_user):
        login_page = CinescopeLoginPage(page)
        review_page = ReviewMoviesPage(page)

        review_text = "Не то чтобы по вкусу вкусно - но по сути вкусно"


        login_page.open()
        login_page.login(registered_user.email, registered_user.password)
        login_page.assert_redirect_to_home_page()
        login_page.assert_login_success_popup()

        review_page.open_movie_page(2448)
        review_page.fill_review(review_text)
        review_page.submit_review()
        review_page.assert_review_visible(review_text)
        review_page.attach_screenshot("review_success")
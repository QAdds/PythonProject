import pytest
import requests
from playwright.sync_api import sync_playwright



DEFAULT_UI_TIMEOUT = 30000  # Пример значения таймаута

AUTH_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru"
REGISTER_ENDPOINT = f"{AUTH_BASE_URL}/register"

@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch(headless=False, slow_mo=500)  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов


@pytest.fixture(scope="function")  # Контекст создается для каждого теста
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)  # Трассировка для отладки
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)  # Установка таймаута по умолчанию
    yield context  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    context.close()  # Контекст закрывается после завершения теста

@pytest.fixture(scope="function")  # Страница создается для каждого теста
def page(context):
    page = context.new_page()
    yield page  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    page.close()  # Страница закрывается после завершения теста

@pytest.fixture(scope="function")
def registered_user():
    import uuid

    random_suffix = uuid.uuid4().hex[:8]
    password = "Qwerty123!"

    payload = {
        "email": f"ui_test_{random_suffix}@mail.com",
        "fullName": 'Test User',
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }

    response = requests.post(
        REGISTER_ENDPOINT,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

    assert response.status_code in (200, 201), f"Не удалось зарегистрировать пользователя: {response.status_code}, {response.text}"

    data = response.json()

    class RegisteredUser:
        def __init__(self, data, payload):
            self.id = data.get("id")
            self.email = payload["email"]
            self.fullName = payload["fullName"]
            self.password = payload["password"]
            self.passwordRepeat = payload["passwordRepeat"]
            self.roles = payload["roles"]

    return RegisteredUser(data, payload)
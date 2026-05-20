from custom_requester.custom_requester import CustomRequester
from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT, BASE_URL
from pydantic import BaseModel

class AuthAPI(CustomRequester):
    """
      Класс для работы с аутентификацией.
      """

    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_URL)

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=200):
        """
        Авторизация пользователя.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        if isinstance(user_creds, BaseModel):
            email = user_creds.email
            password = user_creds.password
        else:
            email = user_creds["email"]
            password = user_creds["password"]

        login_data = {
            "email": email,
            "password": password,}

        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._update_session_headers(**{"authorization": "Bearer " + token})

    def register_admin(self, admin_data: dict, expected_status: int = 201):
        """
        Регистрация пользователя с повышенными правами (ADMIN / SUPER_ADMIN).
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=admin_data,
            expected_status=expected_status
        )
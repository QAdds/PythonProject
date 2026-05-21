import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enums.roles import Roles


class TestUser(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="passwordRepeat должен полностью совпадать с password",
    )
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    # Pydantic v2: поведение сериализации и enum
    model_config = ConfigDict(
        use_enum_values=True  # Enum -> строка при сериализации
    )

    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value


class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Email пользователя",
    )
    fullName: str = Field(
        min_length=1,
        max_length=100,
        description="Полное имя пользователя",
    )
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str = Field(
        description="Дата и время создания пользователя в формате ISO 8601"
    )

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(
                "Некорректный формат даты и времени. Ожидается формат ISO 8601."
            )
        return value

class RegisteredUser(TestUser):
    id: str
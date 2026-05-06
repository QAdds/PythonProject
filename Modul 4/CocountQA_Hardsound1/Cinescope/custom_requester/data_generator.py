import random
import string
from faker import Faker

faker = Faker()


class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"


    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 строчная буква.
        - Минимум 1 заглавная буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        lowercase = random.choice(string.ascii_lowercase)
        uppercase = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)

        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars

        total_length = random.randint(8, 20)
        remaining_length = total_length - 3
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        password = list(lowercase + uppercase + digit + remaining_chars)
        random.shuffle(password)

        return ''.join(password)
    @staticmethod
    def generate_movie_data():
        """Генерирует случайные данные для создания фильма."""
        return {
            "name": faker.sentence(nb_words=3)[:-1],
            "price": 100,
            "description": faker.paragraph(),
            "year": random.randint(1900, 2026),
            "location": "SPB",
            "published": True,
            "genreID": 1,
            "genres": [random.choice(["Action", "Comedy", "Drama", "Horror", "Sci-Fi"])]
        }
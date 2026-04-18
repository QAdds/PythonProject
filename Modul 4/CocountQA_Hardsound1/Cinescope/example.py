
import requests
# Делаем GET запрос к API
response = requests.get('https://restful-booker.herokuapp.com/booking')

# Смотрим, что нам пришло
print(f"Статус ответа: {response.status_code}")
print(f"Тело ответа: {response.text}")
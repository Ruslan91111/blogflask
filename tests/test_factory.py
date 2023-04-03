"""Проверка, что создано тестовое приложение, а также страницы '/hello'"""
from blog import create_app


# Создано ли тестовое приложение
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


# Проверка, что страница по url '/hello' содержит фразу 'Hello, man'.
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, man'




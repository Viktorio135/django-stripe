# URLs

### /admin/ - административная панель
### /item/id/  -  страница определенного товара
### /order/id/  -  страница корзины
### /buy/id/  -  запрос получения session.id для одного товара
### /buy/id/?order=True  -  запрос получения session.id для корзины

##### где id - номер товара/корзины



# Запуск проекта

## 1. Запуск через Docker

### Шаг 1: Настройка Docker

Убедитесь, что у вас установлены Docker и Docker Compose. Если они не установлены, следуйте [официальной документации Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).

### Шаг 2: Создание файла `.env`

Создайте файл `.env` в корне проекта, если его нет, и добавьте следующие переменные окружения (или используйте свои значения):

SECRET_KEY = ''<br>
STRIPE_API_KEY_USD = ''<br>
STRIPE_API_PUBLIC_KEY_USD = ''<br>
STRIPE_API_KEY_EUR = ''<br>
STRIPE_API_PUBLIC_KEY_EUR = ''<br>
MAIN_URL = '' (например http://127.0.0.1:8000)<br>
DEBUG='' (1 or 0)


### Шаг 3: Запуск через Docker Compose

1. Соберите и запустите контейнеры с помощью Docker Compose:

```bash
docker-compose up --build -d
```
Шаг 4: Доступ к приложению

Проект будет доступен по адресу: http://localhost:8000.

## 2. Запуск через Gunicorn


### Шаг 1: Установка зависимостей

Убедитесь, что у вас установлен Python 3.13 и pip. Затем установите все зависимости, указанные в requirements.txt:

```bash
pip install -r requirements.txt
```

### Шаг 2: Миграции базы данных

Для применения миграций к базе данных выполните:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Шаг 3: Сбор статических файлов

```bash
python manage.py collectstatic
```

### Шаг 4: Запуск Gunicorn

Теперь запустите сервер с помощью Gunicorn на порту 8000:

```bash
gunicorn --bind 0.0.0.0:8000 stripe-django.wsgi:application
```


Проект будет доступен по адресу: http://your-server-ip:8000.


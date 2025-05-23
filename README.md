# Foodgram

**Foodgram** — это кулинарный сервис для публикации и обмена рецептами. Пользователи могут добавлять рецепты, просматривать чужие, формировать список покупок и подписываться на других авторов.

## Контакты

- **ФИО** - Усачев Никита Максимович
- **Telegram** - [Никита Усачев](https://t.me/tokyo_simp)

## Технологии

- **Python 3.11**
- **Django REST Framework** — API backend
- **Djoser** — регистрация и авторизация
- **PostgreSQL** — база данных
- **Docker & Docker Compose** — контейнеризация
- **Nginx** — прокси-сервер
- **Gunicorn** — WSGI сервер
- **React** — frontend приложения

## Как запустить проект

1. **Клонируйте репозиторий и перейдите в папку проекта:**

```bash
git clone https://github.com/usichUs/foodgram-st.git
cd foodgram-st/infra
```

2. **Создайте файл .env с настройками окружения (если его нет)**

Пример содержимого:

```
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
SECRET_KEY=your_secret_key
DEBUG=False
```

3. **Запустите проект в Docker:**

```
docker-compose up --build
```

4. **В папке бекэнд для запуска АПИ(без Докера)**

- Создайте виртуальное окружение

```
python -m venv venv
```

- Активируйте виртуальное окружение

Windows

```
venv\Scripts\activate
```

MacOS/Linux

```
source venv/bin/activate
```

- Установите зависимости

```
pip install -r requirements.txt
```

- Загрузите json фикстуры

```
python manage.py import_ingredient
```

- Запустите сервер

```
python manage.py runserver
```

5. **Доступ к сервисам:**

- [Frontend](http://localhost)
- [Документация API](http://localhost/api/docs/)
- [Админ-панель](http://127.0.0.1:8000/admin)

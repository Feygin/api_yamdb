# YaMDb API

## Описание

YaMDb — сервис для сбора отзывов на произведения (книги, фильмы, музыку и др.).  
Пользователи могут оставлять отзывы, ставить оценки и комментировать. 

## Основные возможности

- Категории и жанры произведений.
- Отзывы, оценки (1-10) и рейтинги.
- Комментарии к отзывам.
- Права доступа для пользователей, модераторов и администраторов.

## Как запустить проект

1. **Клонировать репозиторий:**
    ```bash
    git clone git@github.com:Feygin/api_yamdb.git
    cd api_yamdb
    ```

2. **Установить и активировать виртуальное окружение:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Настроить отправку email:**
   - Создайте файл `.env` в корневой директории проекта.
   - Укажите в нём данные вашей почты:
     ```env
     EMAIL_HOST_USER=your_email@yandex.ru
     EMAIL_HOST_PASSWORD=your_email_password
     ```
   - Либо используйте консольный backend для тестирования:
     ```env
     EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
     ```

4. **Выполнить миграции и запустить сервер:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ``` 

Документация API доступна по адресу: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

## Пример запроса

### Получение списка произведений

**Запрос:**
```bash
GET /titles/
```

**Пример ответа:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Интерстеллар",
      "year": 2014,
      "rating": 9,
      "description": "Эпический научно-фантастический фильм о выживании человечества.",
      "genre": [
        {
          "name": "Фантастика",
          "slug": "fantasy"
        },
        {
          "name": "Драма",
          "slug": "drama"
        }
      ],
      "category": {
        "name": "Фильмы",
        "slug": "movies"
      }
    }
  ]
}
```
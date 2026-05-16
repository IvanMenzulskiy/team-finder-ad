# TeamFinder

Django-приложение для поиска тиммейтов на pet-проекты. Автор публикует
идею, остальные пользователи могут заявить себя как участники.

Реализован **Вариант 2** задания: навыки пользователей и фильтрация
списка участников по навыку.

## Стек

- Python 3.11
- Django 5.2.4
- PostgreSQL 16
- Pillow (генерация placeholder-аватаров)
- python-decouple (конфигурация через `.env`)
- Docker / docker-compose (для подъёма БД)

## Локальный запуск

```bash
git clone https://github.com/IvanMenzulskiy/team-finder-ad.git
cd team-finder-ad

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env_example .env              # отредактируйте по вкусу

docker compose up -d              # PostgreSQL
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Сайт открыт на `http://localhost:8000/`.

## Переменные окружения

| Имя                    | Описание                                         |
|------------------------|--------------------------------------------------|
| `DJANGO_SECRET_KEY`    | секретный ключ                                   |
| `DJANGO_DEBUG`         | `True` для разработки                            |
| `DJANGO_ALLOWED_HOSTS` | список хостов через запятую                      |
| `POSTGRES_DB`          | имя БД                                           |
| `POSTGRES_USER`        | пользователь                                     |
| `POSTGRES_PASSWORD`    | пароль                                           |
| `POSTGRES_HOST`        | хост                                             |
| `POSTGRES_PORT`        | порт                                             |

## Демо-аккаунты

| Email                     | Пароль        | Роль          |
|---------------------------|---------------|---------------|
| `admin@example.com`       | `admin12345`  | администратор |
| `ivan@yandex.ru`          | `qwerty12345` | пользователь  |
| `kate@example.com`        | `qwerty12345` | пользователь  |
| `stas@example.com`        | `qwerty12345` | пользователь  |
| `alina@example.com`       | `qwerty12345` | пользователь  |

## Что реализовано

- Кастомная модель `User` с email вместо username.
- Автогенерация placeholder-аватарки при создании пользователя.
- Нормализация телефона: `8XXXXXXXXXX` → `+7XXXXXXXXXX`.
- Валидация ссылки на `github.com` через `RegexValidator`.
- Пагинация по 12 элементов на списках проектов и пользователей.

### Особенности варианта 2 — навыки

- Модель `Skill` (`users.Skill`) с уникальным именем.
- M2M-связь `User.skills` (related_name `users`).
- Блок «Навыки» на странице профиля; владелец профиля может
  добавлять/удалять навыки без перезагрузки страницы.
- При добавлении навыка работает автокомплит (`GET /projects/skills/?q=...`)
  и можно создать новый навык, если его нет в БД.
- Список пользователей `/users/list/?skill=<Название>` показывает
  только тех, у кого есть указанный навык.
- В шапке фильтра подсвечивается активный навык, есть кнопка «Сбросить».

### AJAX-эндпоинты навыков

| Метод | URL                                                    | Описание                       |
|-------|--------------------------------------------------------|--------------------------------|
| GET   | `/projects/skills/?q=<query>`                          | автокомплит навыков            |
| POST  | `/projects/<user_id>/skills/add/`                      | добавить навык в свой профиль  |
| POST  | `/projects/<user_id>/skills/<skill_id>/remove/`        | убрать навык                    |

Префикс `/projects/` — это требование готового `static/js/skills.js`
(он шлёт POST по этому пути; URL в проекте подобран соответственно).

## Тесты

```bash
python manage.py test users projects
```

24 теста: модели, регистрация/логин, страницы проектов, AJAX-эндпоинты
проекта, фильтр пользователей по навыку и все skill-AJAX-эндпоинты.

## Линтер

```bash
pip install flake8
flake8 users projects team_finder
```

Конфиг — в `setup.cfg`, `max-line-length = 100`.

## Автор

[Ivan Menzulskiy](https://github.com/IvanMenzulskiy)

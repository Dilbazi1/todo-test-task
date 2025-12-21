Как запустить проект
Клонируем репозиторий:

git clone <repo_url>
cd <repo_folder>
Создаем .env с настройками (DB, токен бота, секрет Django):
Копировать код
Env
DEBUG=True
SECRET_KEY=


API_URL=http://backend:8000/api/


DB_NAME=todo
DB_USER=todo_user
DB_PASSWORD=todo_pass
DB_HOST=db
DB_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

TIME_ZONE=America/Adak


BOT_TOKEN=<your_bot_token>
Запускаем все сервисы через Docker Compose:
Копировать код
Bash
docker compose up --build
Backend доступен по адресу: http://localhost:8000
Telegram-бот автоматически подключен к backend




Архитектура решения
Backend (Django)
Модели: UserProfile, Task, Category
Поля PK используют ULID вместо UUID или автогенерации чисел.
UserProfile хранит telegram_id и telegram_link_code для привязки.
API CRUD для задач и категорий через Django REST Framework.
Celery проверяет просроченные задачи и отправляет уведомления в Telegram.
Telegram Bot (Aiogram + Dialog)
Команда /start проверяет привязку пользователя через telegram_link_code.
Все обращения к базе данных проходят через sync_to_async для асинхронного выполнения.
Основной диалог позволяет добавлять и просматривать задачи с категориями.
Docker
Контейнеры: backend, bot, db (PostgreSQL), redis (для Celery)
Docker Compose обеспечивает корректное взаимодействие сервисов.



 Сложности и решения
SynchronousOnlyOperation
Проблема: прямые ORM-запросы в async-хендлерах бота.
Решение: оборачивание всех ORM-вызовов через sync_to_async.
KeyError при обращении к profile.user
Причина: OneToOneField не подгружался в async-контексте.
Решение: использован select_related('user').
HTTP-запросы к backend (httpx) падали на таймаут
Причина: backend контейнер ещё не был готов или медленно отвечал.
Решение: увеличен таймаут и добавлены повторные попытки с asyncio.sleep.
Привязка Telegram
Проблема: пользователи без локально установленного Telegram не могли пройти /start.
Решение: сгенерирован telegram_link_code через backend и пользователи могут кликать на ссылку прямо из веба, бот обрабатывает код.

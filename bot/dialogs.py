from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from bot.api import api
from datetime import datetime
import httpx
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from backend.todo.models import UserProfile
import os
from bot.config import API_URL
from backend.todo.models import UserProfile

dialog_router = Router()


# --- States ---
class MainSG(StatesGroup):
    main = State()

class AddTaskSG(StatesGroup):
    title = State()
    description = State()
    due_date = State()
    category = State()


@dialog_router.message(CommandStart())
async def start(message: types.Message, dialog_manager: DialogManager):
    telegram_id = message.from_user.id
    code = None

    # Проверка /start CODE
    if message.text and message.text.startswith("/start "):
        code = message.text.split(" ", 1)[1].strip()

    # Привязка аккаунта
    if code:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{API_URL}auth/telegram/link/",
                    json={"telegram_id": telegram_id, "code": code},
                    timeout=10
                )
                if r.status_code == 200:
                    await message.answer("Аккаунт успешно привязан!")
                else:
                    await message.answer(f"Ошибка сервера: {r.status_code}, {r.text}")
        except Exception as e:
            await message.answer(f"Ошибка привязки: {e}")

   
    try:
        profile = await sync_to_async(UserProfile.objects.select_related('user').get)(
            telegram_id=telegram_id
        )
        await message.answer(f"Профиль найден: {profile.user.username}")
    except UserProfile.DoesNotExist:
        await message.answer(
            "Аккаунт не привязан.\nЗайди на сайт и привяжи Telegram в настройках."
        )
        return

    # Запуск диалога
    await message.answer("Запускаем основной диалог...")
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)
   

# --- Format tasks for main dialog ---
def format_dt(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt.strftime("%d.%m.%Y %H:%M")


async def getter(**kwargs):
    tasks = await api.get_tasks()
    lines = []
    for t in tasks:
        category = t["category"]["name"] if t.get("category") else "Без категории"
        due = format_dt(t["due_date"])
        created_at = format_dt(t["created_at"])
        lines.append(f"{category}\n{t['title']}\n{created_at}\n{due}")
    text = "\n\n".join(lines) or "Нет задач"
    return {"tasks": text}


# --- Main dialog ---
main_dialog = Dialog(
    Window(
        Format("Ваши задачи:\n{tasks}"),
        Row(
            Button(Const("Обновить"), id="refresh"),
            Button(Const("Добавить задачу"), id="add_task",
                   on_click=lambda c, w, m: m.start(AddTaskSG.title))
        ),
        state=MainSG.main,
        getter=getter
    )
)
dialog_router.include_router(main_dialog)


# --- Enter task details ---
async def enter_title(message: types.Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["title"] = message.text
    await manager.next()
   

async def enter_description(message: types.Message, dialog: Dialog, manager: DialogManager):
    desc = "" if message.text == "/skip" else message.text
    manager.current_context().dialog_data["description"] = desc
    await manager.next()
    # await message.answer("Введите дедлайн задачи в формате ДД.MM.ГГГГ ЧЧ:ММ")


def parse_due_date(due_str: str) -> str:
    dt = datetime.strptime(due_str, "%d.%m.%Y %H:%M")
    return dt.isoformat()


async def enter_due_date(message: types.Message, dialog: Dialog, manager: DialogManager):
    try:
        due_iso = parse_due_date(message.text)
    except ValueError:
        await message.answer("Неправильный формат даты. Используйте ДД.MM.ГГГГ ЧЧ:ММ")
        return
    manager.current_context().dialog_data["due_date"] = due_iso
    await manager.next()  # Переходим к выбору категории


# --- Category selection ---
async def category_getter(**kwargs):
    categories = await api.get_categories()
    categories.append({"id": "none", "name": "Без категории"})
    return {"categories": categories}



async def select_category(c, widget, manager: DialogManager, item_id, **kwargs):
    print("Selected item_id:", item_id)

    # Получаем список категорий с бэкенда
    categories = await api.get_categories()

    # Находим выбранную категорию
    selected_category = next((cat for cat in categories if cat["id"] == item_id), None)

    # Берём ID категории для API (или None, если не выбрали)
    category_id = selected_category["id"] if selected_category else None

    # Берём данные задачи из диалога
    data = manager.current_context().dialog_data
    data["category"] = item_id  # сохраняем для внутреннего использования

    # Создаем задачу через API
    try:
        await api.create_task(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data["due_date"],
            category_id=category_id
        )
    except Exception as e:
        # На случай ошибки API
        await manager.event.bot.send_message(
            manager.event.from_user.id,
            f"Ошибка при создании задачи: {e}"
        )
        return

    # Отправляем сообщение пользователю
    await manager.event.bot.send_message(
        manager.event.from_user.id,
        f"Задача '{data['title']}' успешно добавлена"
    )

    # Завершаем диалог и деактивируем контекст, чтобы кнопки больше не вызывали UnknownIntent
    await manager.done()
# --- Add task dialog ---
add_task_dialog = Dialog(
    Window(
        Const("Введите название задачи:"),
        MessageInput(enter_title),
        state=AddTaskSG.title
    ),
    Window(
        Const("Введите описание задачи (или /skip):"),
        MessageInput(enter_description),
        state=AddTaskSG.description
    ),
    Window(
        Const("Введите дедлайн задачи в формате ДД.MM.ГГГГ ЧЧ:ММ:"),
        MessageInput(enter_due_date),
        state=AddTaskSG.due_date
    ),
    Window(
        Const("Выберите категорию задачи:"),
        Column(
            Select(
                Format("{item[name]}"),
                id="category_select",
                item_id_getter=lambda x: x["id"],
                items="categories",
                on_click=select_category
            )
        ),
        getter=category_getter,
        state=AddTaskSG.category
    )
)
dialog_router.include_router(add_task_dialog)
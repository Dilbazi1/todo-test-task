
from celery import shared_task
from django.utils import timezone
from backend.todo.models import Task, UserProfile
from bot.bot import bot
from asgiref.sync import async_to_sync

@shared_task
def send_due_task_notifications():
    tasks = Task.objects.filter(is_done=False, due_date__lte=timezone.now(), notified=False)

    for task in tasks:
        try:
            user_profile = UserProfile.objects.get(user=task.user)
            telegram_id = user_profile.telegram_id

            if telegram_id:
                # Оборачиваем async функцию бота в sync
                async_to_sync(bot.send_message)(
                    telegram_id,
                    f"Задача '{task.title}' просрочена! 🕒"
                )

            # Отмечаем задачу как уведомлённую
            task.notified = True
            task.save()

        except UserProfile.DoesNotExist:
            continue
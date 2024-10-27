from background_task.models import Task
from .views import update_data_for_today
from scrapper.logger_config import logger

def schedule_tasks(sender, **kwargs):
    # Schedule the task only if it doesn't already exist
    logger.warning("scheduling tasks ")
    if not Task.objects.filter(task_name='scrapper.views.update_data_for_today').exists():
        update_data_for_today(repeat=10)  # Schedule your task to run every 24 hours

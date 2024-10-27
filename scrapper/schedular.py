from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .views import update_data_for_today
import atexit
from .logger_config import logger

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the task to run daily at 3:00 PM
    scheduler.add_job(
        update_data_for_today,
        trigger=CronTrigger(hour=14, minute=00),  
        id="daily_task",  
        replace_existing=True,
    )
    scheduler.start()
    logger.warning("Scheduler started!")

    atexit.register(lambda: scheduler.shutdown())

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .views import update_stocks_list_for_today
import atexit
from .logger_config import logger
import time

def a_simple_counter():
    logger.warning("I am active")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule update_stocks_list_for_today to run daily at 00:40
    scheduler.add_job(
        update_stocks_list_for_today,
        trigger=CronTrigger(hour=0, minute=40),  
        id="daily_task",  
        replace_existing=True,
    )
    
    # Schedule a_simple_counter to run every 5 seconds
    scheduler.add_job(
        a_simple_counter,
        trigger=IntervalTrigger(seconds=10),
        id="instant_counter",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.warning("Scheduler started!")

    atexit.register(lambda: scheduler.shutdown())

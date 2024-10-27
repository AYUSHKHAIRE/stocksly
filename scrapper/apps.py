from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'scrapper'

    def ready(self):
        from .schedular import start_scheduler
        start_scheduler()

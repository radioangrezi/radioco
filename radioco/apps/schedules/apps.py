from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    name = 'radioco.apps.schedules'

    def ready(self):
        from radioco.apps.schedules import signals

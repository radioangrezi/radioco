from django.apps import AppConfig


class Schedules(AppConfig):
    name = 'radioco.schedules'

    def ready(self):
        from radioco.schedules import signals

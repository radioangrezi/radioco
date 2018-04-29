from django.apps import AppConfig


class Programmes(AppConfig):
    name = 'radioco.programmes'

    def ready(self):
        from radioco.programmes import signals


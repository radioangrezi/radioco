from django.apps import AppConfig


class ProgrammesConfig(AppConfig):
    name = 'radioco.apps.programmes'

    def ready(self):
        from radioco.apps.programmes import signals


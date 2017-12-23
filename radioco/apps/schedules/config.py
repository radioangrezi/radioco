from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    name = 'radioco.apps.schedules'

    def ready(self):
        from radioco.apps.programmes.models import Programme
        from radioco.apps.programmes.signals import pre_archive
        from radioco.apps.schedules import utils

        pre_archive.connect(utils.archive_schedules, sender=Programme)

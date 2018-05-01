from django.core.management.base import BaseCommand

from radioco.utils import example


class Command(BaseCommand):
    def handle(self, *args, **options):
        example.create_example_data()

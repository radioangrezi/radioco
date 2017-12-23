from django.dispatch import Signal

pre_archive = Signal(providing_args=["instance"])

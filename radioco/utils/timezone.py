from django.utils import timezone


def make_aware(dt):
    if not dt:
        return None

    if not dt.tzinfo:
        return timezone.make_aware(dt)
    return dt


def make_aware_from_settings(dt):
    return timezone.get_default_timezone().localize(dt)


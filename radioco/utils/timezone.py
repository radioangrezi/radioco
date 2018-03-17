from django.utils import timezone

def make_tz_aware(dt):
    if not dt:
        return None

    if not dt.tzinfo:
        return timezone.make_aware(dt)
    return dt


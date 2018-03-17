from django.test import TestCase
from pytz import timezone
import datetime

from radioco.apps.radio.tests import tz_from_settings
from radioco.utils.timezone import make_tz_aware

class UtilsTests(TestCase):
    def test_make_aware_tz(self):
        self.assertEqual(
            make_tz_aware(
                datetime.datetime(2018, 3, 17, 0, 0, tzinfo=timezone('utc'))),
            (datetime.datetime(2018, 3, 17, 0, 0, tzinfo=timezone('utc'))))

    def test_make_aware_no_tz(self):
        self.assertEqual(
            make_tz_aware(datetime.datetime(2018, 3, 17, 0, 0)),
            tz_from_settings(datetime.datetime(2018, 3, 17, 0, 0)))

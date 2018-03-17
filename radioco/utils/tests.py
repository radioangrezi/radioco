from django.test import TestCase
import datetime
import pytz

import radioco.utils.timezone


class UtilsTests(TestCase):
    def test_timezone_make_aware(self):
        self.assertEqual(
            radioco.utils.timezone.make_aware(
                datetime.datetime(
                    2018, 3, 17, 0, 0, tzinfo=pytz.timezone('utc'))),
            datetime.datetime(2018, 3, 17, 0, 0, tzinfo=pytz.timezone('utc')))

    def test_timezone_make_aware_no_tz(self):
        self.assertEqual(
            radioco.utils.timezone.make_aware(
                datetime.datetime(2018, 3, 17, 0, 0)),
            radioco.utils.timezone.make_aware_from_settings(
                datetime.datetime(2018, 3, 17, 0, 0)))

    def test_make_aware_none(self):
        self.assertIsNone(radioco.utils.timezone.make_aware(None))

    def test_timezone_make_aware_from_settings_no_tz(self):
        self.assertEqual(
            radioco.utils.timezone.make_aware_from_settings(
                datetime.datetime(2018, 3, 17, 0, 0)),
            pytz.timezone('Europe/Berlin').localize(
                datetime.datetime(2018, 3, 17, 0, 0)))

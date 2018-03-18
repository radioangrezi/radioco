# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo, Stefan Walluhn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import datetime
import mock
import pytz

from django.test import TestCase
import django.utils.timezone

from radioco.apps.programmes.models import Programme
import radioco.utils.timezone
import radioco.utils.example


def now():
    return django.utils.timezone.make_aware(
        datetime.datetime(2014, 1, 1, 13, 30, 0))


class TestDataMixin(object):
    @classmethod
    @mock.patch('django.utils.timezone.now', now)
    def setUpTestData(cls):
        radioco.utils.example.create_example_data()
        cls.programme = Programme.objects.get(name="Classic hits")
        cls.slot = cls.programme.slot_set.first()
        cls.schedule = cls.slot.schedule_set.first()
        cls.episode = cls.programme.episode_set.first()


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

    def test_timezone_make_naive(self):
        self.assertEqual(
            radioco.utils.timezone.make_naive(
                datetime.datetime(
                    2018, 3, 17, 0, 0, tzinfo=pytz.timezone('utc'))),
            datetime.datetime(2018, 3, 17, 1, 0))

    def test_timezone_make_naive_no_tz(self):
        self.assertEqual(
            radioco.utils.timezone.make_naive(
                datetime.datetime(2018, 3, 17, 0, 0)),
            datetime.datetime(2018, 3, 17, 0, 0))

    def test_timezone_make_naive_none(self):
        self.assertIsNone(radioco.utils.timezone.make_naive(None))

    def test_timezone_make_aware_from_settings_no_tz(self):
        self.assertEqual(
            radioco.utils.timezone.make_aware_from_settings(
                datetime.datetime(2018, 3, 17, 0, 0)),
            pytz.timezone('Europe/Berlin').localize(
                datetime.datetime(2018, 3, 17, 0, 0)))

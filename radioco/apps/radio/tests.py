# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
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

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
import datetime
import mock
import utils

from radioco.apps.programmes.models import Programme

def tz_from_settings(dt):
    return timezone.get_default_timezone().localize(dt)

def now():
    return timezone.make_aware(datetime.datetime(2014, 1, 1, 13, 30, 0))

class TestDataMixin(object):
    @classmethod
    @mock.patch('django.utils.timezone.now', now)
    def setUpTestData(cls):
        utils.create_example_data()
        cls.programme = Programme.objects.get(name="Classic hits")
        cls.slot = cls.programme.slot_set.first()
        cls.schedule = cls.slot.schedule_set.first()
        cls.episode = cls.programme.episode_set.first()

class RadioIntegrationTests(TestDataMixin, TestCase):
    def test_index(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


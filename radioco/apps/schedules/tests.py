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

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError, FieldError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete
from django.forms import modelform_factory
from django.test import TestCase
import datetime
import mock
import recurrence

from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.radio.tests import TestDataMixin, now
from radioco.apps.schedules import utils
from radioco.apps.schedules.models import MO, TU, WE, TH, FR, SA, SU
from radioco.apps.schedules.models import Schedule, Transmission


def mock_now():
    return datetime.datetime(2014, 1, 1, 13, 30, 0)


class ScheduleValidationTests(TestDataMixin, TestCase):
    def test_fields(self):
        schedule = Schedule()
        with self.assertRaisesMessage(
            ValidationError,
            "'type': [u'This field cannot be blank.'], "
            "'programme': [u'This field cannot be null.']}"):
            schedule.clean_fields()



class ScheduleModelTests(TestDataMixin, TestCase):
    def setUp(self):
        self.recurrences = recurrence.Recurrence(
            dtstart=datetime.datetime(2014, 1, 6, 14, 0, 0),
            dtend=datetime.datetime(2014, 1, 31, 14, 0, 0),
            rrules=[recurrence.Rule(recurrence.WEEKLY)])

        self.schedule = Schedule.objects.create(
            programme=self.programme,
            type='L',
            recurrences=self.recurrences)

    def test_runtime(self):
        self.assertEqual(datetime.timedelta(hours=+1), self.schedule.runtime)

    def test_runtime_not_set(self):
        schedule = Schedule(programme=Programme())
        with self.assertRaises(FieldError):
            schedule.runtime

    def test_start_date_schedule_board_none(self):
        schedule = Schedule(
            recurrences=self.recurrences,
            programme=Programme())
        self.assertEqual(schedule.start, datetime.datetime(2014, 1, 6, 14, 0))

    def test_start(self):
        self.assertEqual(
            self.schedule.start, datetime.datetime(2014, 1, 6, 14, 0, 0))

    def test_set_start(self):
        self.schedule.start = datetime.datetime(2015, 1, 1, 14, 0, 0)
        self.assertEqual(
            self.schedule.recurrences.dtstart,
            datetime.datetime(2015, 1, 1, 14, 0, 0))

    def test_start_none(self):
        schedule = Schedule(programme=Programme())
        self.assertIsNone(schedule.start)

    def test_end(self):
        self.assertEqual(
            self.schedule.end, datetime.datetime(2014, 1, 31, 14, 0, 0))

    def test_end_none(self):
        schedule = Schedule(programme=Programme())
        self.assertIsNone(schedule.end)

    def test_rr_start(self):
        self.assertEqual(
            self.schedule.rr_start, datetime.datetime(2014, 1, 6, 14, 0, 0))

    def test_set_rr_start(self):
        self.schedule.rr_start = datetime.datetime(2015, 1, 1, 14, 0, 0)
        self.assertEqual(
            self.schedule.recurrences.dtstart,
            datetime.datetime(2015, 1, 1, 14, 0, 0))

    def test_rr_end(self):
        self.assertEqual(
            self.schedule.rr_end, datetime.datetime(2014, 1, 31, 14, 0))

    def test_recurrence_rules(self):
        self.assertListEqual(
            self.schedule.recurrences.rrules, self.recurrences.rrules)

    def test_date_before(self):
        self.assertEqual(
            self.schedule.date_before(datetime.datetime(2014, 1, 14)),
            datetime.datetime(2014, 1, 13, 14, 0))

    def test_date_after(self):
        self.assertEqual(
            self.schedule.date_after(datetime.datetime(2014, 1, 14)),
            datetime.datetime(2014, 1, 20, 14, 0))

    def test_date_after_exclude(self):
        self.assertEqual(
            self.schedule.date_after(
                datetime.datetime(2014, 1, 6, 14, 0), inc=False),
            datetime.datetime(2014, 1, 13, 14, 0))

    def test_dates_between(self):
        self.assertListEqual(
            list(self.schedule.dates_between(
                datetime.datetime(2014, 1, 1),
                datetime.datetime(2014, 1, 14))),
            [datetime.datetime(2014, 1, 6, 14, 0),
             datetime.datetime(2014, 1, 13, 14, 0)])

    def test_dates_between_complex_ruleset(self):
        schedule = Schedule(
            programme=Programme(name="Programme 14:00 - 15:00", runtime=60),
            recurrences=recurrence.Recurrence(
                dtstart=datetime.datetime(2014, 1, 2, 14, 0, 0),
                rrules=[recurrence.Rule(recurrence.DAILY, interval=2)],
                exrules=[recurrence.Rule(
                    recurrence.WEEKLY, byday=[recurrence.MO, recurrence.TU])]))

        self.assertListEqual(
            list(schedule.dates_between(
                datetime.datetime(2014, 1, 1),
                datetime.datetime(2014, 1, 9))),
            [datetime.datetime(2014, 1, 2, 14, 0),
             datetime.datetime(2014, 1, 4, 14, 0),
             datetime.datetime(2014, 1, 8, 14, 0)])

    # hacky workaround, remove after upstream bug is solved
    # https://github.com/django-recurrence/django-recurrence/issues/94
    def test_dates_between_rdate(self):
        schedule = Schedule(
            programme=Programme(name="Programme 14:00 - 15:00", runtime=60),
            recurrences=recurrence.Recurrence(
                dtstart=datetime.datetime(2014, 1, 2, 14, 0, 0),
                rrules=[recurrence.Rule(recurrence.DAILY, interval=2)],
                rdates=[datetime.datetime(2014, 1, 5, 0, 0)]))

        self.assertListEqual(
            list(schedule.dates_between(
                datetime.datetime(2014, 1, 4),
                datetime.datetime(2014, 1, 7))),
            [datetime.datetime(2014, 1, 4, 14, 0),
             datetime.datetime(2014, 1, 5, 14, 0),
             datetime.datetime(2014, 1, 6, 14, 0)])


    # hacky workaround, remove after upstream bug is solved
    # https://github.com/django-recurrence/django-recurrence/issues/94
    def test_dates_between_exdate(self):
        schedule = Schedule(
            programme=Programme(name="Programme 14:00 - 15:00", runtime=60),
            recurrences=recurrence.Recurrence(
                dtstart=datetime.datetime(2014, 1, 2, 14, 0, 0),
                rrules=[recurrence.Rule(recurrence.DAILY)],
                exdates=[datetime.datetime(2014, 1, 5, 0, 0, 0)]))

        self.assertListEqual(
            list(schedule.dates_between(
                datetime.datetime(2014, 1, 4),
                datetime.datetime(2014, 1, 7))),
            [datetime.datetime(2014, 1, 4, 14, 0),
             datetime.datetime(2014, 1, 6, 14, 0)])

    def test_unicode(self):
        self.assertEqual(unicode(self.schedule), 'Monday - 14:00:00')

    @mock.patch('django.utils.timezone.now', now)
    def test_save_rearange_episodes(self):
        self.assertEqual(
            self.episode.issue_date, datetime.datetime(2015, 1, 1, 14, 0))
        self.schedule.save()
        self.episode.refresh_from_db()
        self.assertEqual(
            self.episode.issue_date, datetime.datetime(2014, 1, 6, 14, 0))


class TransmissionModelTests(TestDataMixin, TestCase):
    def setUp(self):
        self.transmission = Transmission(
            self.schedule, datetime.datetime(2015, 1, 6, 14, 0, 0))

    def test_nonexistent_date(self):
        with self.assertRaises(ValueError):
            Transmission(self.schedule,
                         datetime.datetime(2015, 1, 6, 14, 30, 0))

    def test_programme(self):
        self.assertEqual(self.transmission.programme,
                         self.transmission.schedule.programme.name)

    def test_start(self):
        self.assertEqual(self.transmission.start,
                         datetime.datetime(2015, 1, 6, 14, 0, 0))

    def test_end(self):
        self.assertEqual(self.transmission.end,
                         datetime.datetime(2015, 1, 6, 15, 0, 0))

    def test_slug(self):
        self.assertEqual(self.transmission.slug,
                         self.transmission.schedule.programme.slug)

    def test_summary(self):
        self.assertEqual(self.transmission.summary,
                         self.transmission.episode.summary)

    def test_summary_nonexistent_episode(self):
        transmission = Transmission(self.schedule,
                                    datetime.datetime(2016, 1, 1, 14, 0))
        self.assertEqual(transmission.summary, self.programme.synopsis)

    def test_title(self):
        self.assertEqual(self.transmission.title,
                         self.transmission.episode.title)

    def test_title_nonexistent_episode(self):
        transmission = Transmission(self.schedule,
                                    datetime.datetime(2016, 1, 1, 14, 0))
        self.assertEqual(transmission.title,
                         self.transmission.schedule.programme.name)

    def test_url(self):
        self.assertEqual(self.transmission.url,
                         reverse(
                             'programmes:detail',
                             args=[self.schedule.programme.slug]))

    def test_get_or_create_existent_episode(self):
        transmission = Transmission(self.schedule,
                                    datetime.datetime(2015, 1, 1, 14, 0))
        self.assertEqual(transmission._get_or_create_episode(), self.episode)

    def test_get_or_create_nonexistent_episode(self):
        transmission = Transmission(self.schedule,
                                    datetime.datetime(2016, 1, 1, 14, 0))
        episode = transmission._get_or_create_episode()
        self.assertIsInstance(episode, Episode)
        self.assertIsNone(episode.id)

    def test_at(self):
        now = Transmission.at(datetime.datetime(2015, 1, 6, 14, 30, 0))
        self.assertListEqual(
            map(lambda t: (t.slug, t.start), list(now)),
            [(u'classic-hits', datetime.datetime(2015, 1, 6, 14, 0))])

    def test_between(self):
        between = Transmission.between(datetime.datetime(2015, 1, 6, 12, 0, 0),
                                       datetime.datetime(2015, 1, 6, 17, 0, 0))
        self.assertListEqual(
            map(lambda t: (t.slug, t.start), list(between)),
            [(u'the-best-wine', datetime.datetime(2015, 1, 6, 12, 0)),
             (u'local-gossips', datetime.datetime(2015, 1, 6, 13, 0)),
             (u'classic-hits', datetime.datetime(2015, 1, 6, 14, 0))])


class ScheduleUtilsTests(TestDataMixin, TestCase):
    def test_available_dates_after(self):
        Schedule.objects.create(
            programme=self.programme,
            type="L",
            recurrences= recurrence.Recurrence(
                dtstart=datetime.datetime(2015, 1, 6, 16, 0, 0),
                dtend=datetime.datetime(2015, 1, 31, 16, 0, 0),
                rrules=[recurrence.Rule(recurrence.WEEKLY)]))

        dates = utils.available_dates(
            self.programme, datetime.datetime(2015, 1, 5))
        self.assertEqual(dates.next(), datetime.datetime(2015, 1, 5, 14, 0))
        self.assertEqual(dates.next(), datetime.datetime(2015, 1, 6, 14, 0))
        self.assertEqual(dates.next(), datetime.datetime(2015, 1, 6, 16, 0))

    def test_available_dates_none(self):
        dates = utils.available_dates(Programme(), datetime.datetime.now())
        with self.assertRaises(StopIteration):
            dates.next()

    def test_rearrenge_episodes(self):
        utils.rearrange_episodes(self.programme, datetime.datetime(2015, 1, 1))
        self.assertListEqual(
            map(lambda e: e.issue_date, self.programme.episode_set.all()[:5]),
            [datetime.datetime(2015, 1, 1, 14, 0),
             datetime.datetime(2015, 1, 2, 14, 0),
             datetime.datetime(2015, 1, 3, 14, 0),
             datetime.datetime(2015, 1, 4, 14, 0),
             datetime.datetime(2015, 1, 5, 14, 0)])

    def test_rearrenge_episodes_new_schedule(self):
        Schedule.objects.create(
            programme=self.programme,
            type="L",
            recurrences= recurrence.Recurrence(
                dtstart=datetime.datetime(2015, 1, 3, 16, 0, 0),
                dtend=datetime.datetime(2015, 1, 31, 16, 0, 0),
                rrules=[recurrence.Rule(recurrence.WEEKLY)]))

        utils.rearrange_episodes(self.programme, datetime.datetime(2015, 1, 1))
        self.assertListEqual(
            map(lambda e: e.issue_date, self.programme.episode_set.all()[:5]),
            [datetime.datetime(2015, 1, 1, 14, 0),
             datetime.datetime(2015, 1, 2, 14, 0),
             datetime.datetime(2015, 1, 3, 14, 0),
             datetime.datetime(2015, 1, 3, 16, 0),
             datetime.datetime(2015, 1, 4, 14, 0)])

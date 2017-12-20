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

from radioco.apps.programmes.models import Episode, Programme
from dateutil import rrule
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from recurrence.fields import RecurrenceField
import datetime
import django.utils.timezone


EMISSION_TYPE = (
    ("L", _("live")),
    ("B", _("broadcast")),
    ("S", _("broadcast syndication")),
    ("R", _("repetition"))
)

MO = 0
TU = 1
WE = 2
TH = 3
FR = 4
SA = 5
SU = 6

WEEKDAY_CHOICES = (
    (MO, _('Monday')),
    (TU, _('Tuesday')),
    (WE, _('Wednesday')),
    (TH, _('Thursday')),
    (FR, _('Friday')),
    (SA, _('Saturday')),
    (SU, _('Sunday')),
)


class Schedule(models.Model):
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    type = models.CharField(verbose_name=_("type"), choices=EMISSION_TYPE, max_length=1)
    recurrences = RecurrenceField(verbose_name=_("recurrences"))
    source = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("source"),
        help_text=_("It is used when is a broadcast.")
    )

    @property
    def runtime(self):
        return self.programme.runtime

    @property
    def start(self):
        return self.rr_start

    @start.setter
    def start(self, start_date):
        self.rr_start = start_date

    @property
    def end(self):
        return self.rr_end

    # XXX refactor
    @property
    def rr_start(self):
        return self.recurrences.dtstart

    @rr_start.setter
    def rr_start(self, start_date):
        self.recurrences.dtstart = start_date

    @property
    def rr_end(self):
        return self.recurrences.dtend


    def dates_between(self, after, before):
        """
            Return a sorted list of dates between after and before
        """
        # hacky workaround, remove after upstream bug is solved
        # https://github.com/django-recurrence/django-recurrence/issues/94
        self.__fix_rdates__()
        return self.recurrences.between(
            self._merge_after(after), self._merge_before(before), inc=True)

    def date_before(self, before):
        # hacky workaround, remove after upstream bug is solved
        # https://github.com/django-recurrence/django-recurrence/issues/94
        self.__fix_rdates__()
        return self.recurrences.before(self._merge_before(before), inc=True)

    def date_after(self, after, inc=True):
        # hacky workaround, remove after upstream bug is solved
        # https://github.com/django-recurrence/django-recurrence/issues/94
        self.__fix_rdates__()
        return self.recurrences.after(self._merge_after(after), inc)

    def save(self, *args, **kwargs):
        import utils
        super(Schedule, self).save(*args, **kwargs)
        utils.rearrange_episodes(self.programme, django.utils.timezone.now())

    def _merge_before(self, before):
        if not self.end:
            return before
        return min(before, self.end)

    # XXX refactor
    def _merge_after(self, after):
        return after

    def __unicode__(self):
        return ' - '.join([self.start.strftime('%A'), self.start.strftime('%X')])

    def __fix_rdates__(self):
        def fix_rdate(rdate):
            return datetime.datetime.combine(rdate, datetime.time(
                self.start.hour,
                self.start.minute,
                self.start.second,
                self.start.microsecond,
                self.start.tzinfo))
        self.recurrences.rdates = map(fix_rdate, self.recurrences.rdates)
        self.recurrences.exdates = map(fix_rdate, self.recurrences.exdates)


class Transmission(object):
    @classmethod
    def at(cls, at):
        # XXX filter schedule start / end
        schedules = Schedule.objects.all()
        for schedule in schedules:
            date = schedule.date_before(at)
            if date is None:
                continue
            if at < date + schedule.runtime:
                yield cls(schedule, date)

    @classmethod
    def between(cls, after, before, schedules=None):
        if schedules is None:
            schedules = Schedule.objects.all()

        for schedule in schedules:
            for date in schedule.dates_between(after, before):
                yield cls(schedule, date)

    def __init__(self, schedule, date):
        if not schedule.date_before(date) == date:
            raise ValueError("no scheduled transmission on given date")

        self.programme = schedule.programme
        self.type = schedule.type
        self.start = date
        self.end = date + self.programme.runtime

        self.episode = self._get_or_create_episode()

    def _get_or_create_episode(self):
        try:
            # XXX do not use sting
            if self.type == 'R':
                _episodes = Episode.objects.filter(
                    programme=self.programme,
                    issue_date__lt=self.start)
                return _episodes.latest('issue_date')

            return Episode.objects.get(
                programme=self.programme, issue_date=self.start)
        except Episode.DoesNotExist:
            return None

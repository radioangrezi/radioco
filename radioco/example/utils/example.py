from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import recurrence

from radioco.global_settings.models import (
    SiteConfiguration, CalendarConfiguration)
from radioco.programmes.models import (
    Programme, Episode, Role, CONTRIBUTOR, Podcast)
from radioco.schedules.models import Slot, Schedule
from radioco.schedules.utils import rearrange_episodes


def create_example_data():
    # Create administrator
    user, created = User.objects.get_or_create(
        username='admin', defaults={
            'is_superuser': True,
            'is_staff': True,
        }
    )
    if created:
        user.set_password('1234')
        user.save()

    # Site config
    site_config = SiteConfiguration.get_global()
    site_config.about_footer = '''
        RadioCo is a broadcasting radio recording scheduling system.
        RadioCo has been intended to provide a solution for a wide range of broadcast projects,
        from community to public and commercial stations.
    '''
    site_config.more_about_us = 'Live shows are recorded and published automatically'
    site_config.address = 'http://radioco.org/'
    site_config.facebook_address = 'https://facebook.com/radioco.org'
    site_config.twitter_address = 'https://twitter.com/RadioCo_org'
    site_config.save()

    # Programme 1
    synopsis = '''
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
        when an unknown printer took a galley of type and scrambled it to make a type specimen book.
    '''
    programme, created = Programme.objects.get_or_create(
        name='Morning News', defaults=dict(
            synopsis=synopsis,
            language='en',
            photo='defaults/example/radio_1.jpg',
            current_season=1,
            category='News & Politics',))

    slot, created = Slot.objects.get_or_create(
        programme=programme, runtime=datetime.timedelta(minutes=60))

    recurrences = recurrence.Recurrence(
        dtstart=timezone.make_aware(datetime.datetime(2015, 1, 1, 8, 0, 0)),
        rrules=[recurrence.Rule(recurrence.DAILY)])

    recurrences_repetition = recurrence.Recurrence(
        dtstart=timezone.make_aware(datetime.datetime(2015, 1, 1, 20, 0, 0)),
        rrules=[recurrence.Rule(recurrence.DAILY)])

    Schedule.objects.get_or_create(
        slot=slot, type='L', recurrences=recurrences)

    Schedule.objects.get_or_create(
        slot=slot,
        type='R',
        recurrences=recurrences_repetition)

    for number in range(1, 4):
        episode, created = Episode.objects.get_or_create(
            title='Episode %s' % number,
            programme=programme,
            summary=synopsis,
            season=1,
            number_in_season=number,
        )
        if number == 1:
            Podcast.objects.get_or_create(
                episode=episode,
                url='https://archive.org/download/Backstate_Wife/1945-08-10_-_1600_-_Backstage_Wife_-_Mary_And_Larry_See_A_Twenty_Year_Old_Portrait_That_Looks_Exactly_Like_Mary_-_32-22_-_14m13s.mp3',
                mime_type='audio/mp3',
                length=0,
                duration=853
            )

    for username_counter in range(1, 6):
        titles = ['', 'Mark Webber', 'Paul Jameson', 'Laura Sommers', 'Martin Blunt', 'John Smith']
        user, created = User.objects.get_or_create(
            username='user_%s' % username_counter,
            defaults={
                'first_name': titles[username_counter]
            }
        )
        user.userprofile.bio = synopsis
        user.userprofile.avatar = 'defaults/example/user_%s.jpg' % username_counter
        user.userprofile.display_personal_page = True
        user.userprofile.save()

        Role.objects.get_or_create(
            person=user,
            programme=programme,
            defaults={
                'role': CONTRIBUTOR,
                'description': synopsis,
            }
        )

    # Programme 2 - 5
    titles = ['', 'Places To Go', 'The best wine', 'Local Gossips', 'Classic hits']
    for programme_counter in range(1, 5):
        programme, created = Programme.objects.get_or_create(
            name=titles[programme_counter],
            synopsis=synopsis,
            language='en',
            photo='defaults/example/radio_%s.jpg' % str(programme_counter + 1),
            current_season=7,
            category='News & Politics',)

        slot, created = Slot.objects.get_or_create(
            programme=programme, runtime=datetime.timedelta(minutes=60))

        recurrences = recurrence.Recurrence(
            dtstart=(
                timezone.make_aware(datetime.datetime(2015, 1, 1, 10, 0, 0)) +
                datetime.timedelta(hours=programme_counter)),
            rrules=[recurrence.Rule(recurrence.DAILY)])

        Schedule.objects.get_or_create(
            slot=slot,
            type='L',
            recurrences=recurrences)

        for season in range(1, 8):
            for number in range(1, 6):
                Episode.objects.get_or_create(
                    title='Episode %s' % number,
                    programme=programme,
                    summary="Summary Season {}, Number {}: {}".format(
                        season, number, synopsis),
                    season=season,
                    number_in_season=number,
                )

    for programme in Programme.objects.all():
        rearrange_episodes(programme,
                           timezone.make_aware(datetime.datetime(1970, 1, 1)))

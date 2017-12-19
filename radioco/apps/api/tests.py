from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.radio.tests import TestDataMixin
from radioco.apps.schedules.models import Schedule, Transmission
from radioco.apps.schedules.models import WE
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
import datetime
import mock
import serializers
import views


def mock_now():
    return datetime.datetime(2015, 1, 6, 14, 30, 0)


class TestSerializers(TestDataMixin, TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer(self.programme)
        self.assertListEqual(
            serializer.data.keys(),
            ['slug', 'name', 'synopsis', 'runtime', 'photo', 'language',
             'website', 'category', 'created_at', 'updated_at'])

    def test_programme_photo_url(self):
        serializer = serializers.ProgrammeSerializer(self.programme)
        self.assertEqual(
            serializer.data['photo'], "/media/defaults/example/radio_5.jpg")

    def test_episode(self):
        serializer = serializers.EpisodeSerializer(self.episode)
        self.assertListEqual(
            serializer.data.keys(),
            ['title', 'programme', 'summary', 'issue_date', 'season',
             'number_in_season', 'created_at', 'updated_at'])

    def test_episode_programme(self):
        serializer = serializers.EpisodeSerializer(self.episode)
        self.assertEqual(serializer.data['programme'], "classic-hits")

    def test_schedule(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertDictEqual(serializer.data, {
            'title': u'Classic hits', 'source': None,
            'start': '2015-01-01T14:00:00',
            'end': datetime.datetime(2015, 1, 1, 15, 0),
            'type': 'L',
            'id': 6,
            'programme': u'classic-hits'})

    def test_transmission(self):
        serializer = serializers.TransmissionSerializer(
            Transmission(self.schedule,
                         datetime.datetime(2015, 1, 6, 14, 0, 0)))
        data = serializer.data

        for key in ['start', 'end', 'schedule', 'programme', 'title', 'slug',
                    'url', 'summary', 'type']:
            self.assertIn(key, data)

        self.assertEqual(data['start'], '2015-01-06T14:00:00')
        self.assertEqual(data['schedule'], 6)
        self.assertEqual(data['programme'], u'Classic hits')
        self.assertEqual(data['title'], u'Episode 1')
        self.assertEqual(data['slug'], u'classic-hits')
        self.assertEqual(data['url'], u'/programmes/classic-hits/')
        self.assertEqual(data['type'], u'L')


class TestAPI(TestDataMixin, APITestCase):
    def setUp(self):
        admin = User.objects.create_user(
            username='klaus', password='topsecret')
        admin.user_permissions.add(
            Permission.objects.get(codename='add_schedule'))

        someone = User.objects.create_user(
            username='someone', password='topsecret')

    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_get_all(self):
        response = self.client.get('/api/2/episodes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_episodes_get_by_programme(self):
        response = self.client.get(
            '/api/2/episodes', {'programme': self.programme.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['programme'], self.programme.slug)

    def test_episodes_post(self):
        response = self.client.post('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_put(self):
        response = self.client.put('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_delete(self):
        response = self.client.delete('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_schedules_get_all(self):
        response = self.client.get('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schedules_get_by_programme(self):
        response = self.client.get(
            '/api/2/schedules', {'programme': self.programme.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.programme.name)

    def test_schedules_get_by_nonexisting_programme(self):
        response = self.client.get(
            '/api/2/schedules', {'programme': 'foo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_get_by_type(self):
        response = self.client.get('/api/2/schedules?type=L')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('L', map(lambda s: s['type'], response.data))
        self.assertFalse(
            filter(lambda s: s != 'L',
                   map(lambda s: s['type'], response.data)))

    def test_schedules_get_by_nonexiting_type(self):
        response = self.client.get('/api/2/schedules?type=B')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_post(self):
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_post_authenticated_no_permission(self):
        self.client.login(username="someone", password="topsecret")
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmissions(self):
        response = self.client.get('/api/2/transmissions')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data)>20)

    def test_transmission_after(self):
        response = self.client.get(
            '/api/2/transmissions', {'after': datetime.date(2015, 02, 01)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(response.data, key=lambda t: t['start'])[0]['start'],
            '2015-02-01T08:00:00')

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_before(self):
        response = self.client.get(
            '/api/2/transmissions', {'before': datetime.date(2015, 01, 14)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(response.data, key=lambda t: t['start'])[-1]['start'],
            '2015-01-14T20:00:00')

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_now(self):
        response = self.client.get('/api/2/transmissions/now')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            map(lambda t: (t['slug'], t['start']), response.data),
            [(u'classic-hits', '2015-01-06T14:00:00')])

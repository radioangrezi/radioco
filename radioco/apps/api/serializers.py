from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, Transmission
from rest_framework import serializers
import datetime


class ProgrammeSerializer(serializers.HyperlinkedModelSerializer):
    runtime = serializers.DurationField()
    photo = serializers.ImageField()
    url = serializers.HyperlinkedIdentityField(
        view_name='api:programme-detail', lookup_field='slug')

    class Meta:
        model = Programme
        fields = ('name', 'synopsis', 'runtime', 'photo', 'language',
                  'website', 'category', 'created_at', 'updated_at', 'url')


class EpisodeSerializer(serializers.HyperlinkedModelSerializer):
    programme = serializers.HyperlinkedRelatedField(
        view_name='api:programme-detail', lookup_field='slug', read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='api:episode-detail')

    class Meta:
        model = Episode
        fields = ('programme', 'title', 'summary', 'issue_date', 'season',
                  'number_in_season', 'created_at', 'updated_at', 'url')


class ScheduleSerializer(serializers.ModelSerializer):
    programme = serializers.HyperlinkedRelatedField(
        view_name='api:programme-detail',
        lookup_field='slug',
        queryset=Programme.objects.all())
    title = serializers.SerializerMethodField()
    # XXX this is a bit hacky...
    start = serializers.DateTimeField(source='rr_start')
    end = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'title', 'programme', 'start', 'end', 'type','source')

    def get_title(self, schedule):
        return schedule.programme.name

    def get_end(self, schedule):
        # XXX temp workaround while dtstart not mandatory
        try:
            return schedule.recurrences.dtstart + schedule.runtime
        except TypeError:
            return None


class TransmissionSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    type = serializers.CharField(max_length=1)
    programme = ProgrammeSerializer()
    episode = EpisodeSerializer()
    schedule = serializers.PrimaryKeyRelatedField(read_only=True)

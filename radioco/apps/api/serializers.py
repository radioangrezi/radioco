from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, Transmission
from rest_framework import serializers
import datetime


class ProgrammeSerializer(serializers.ModelSerializer):
    runtime = serializers.DurationField()
    photo = serializers.ImageField()

    class Meta:
        model = Programme
        fields = ('slug', 'name', 'synopsis', 'runtime', 'photo', 'language',
                  'website', 'category', 'created_at', 'updated_at')


class EpisodeSerializer(serializers.ModelSerializer):
    programme = serializers.SlugRelatedField(
        slug_field='slug', queryset=Programme.objects.all())
    class Meta:
        model = Episode
        fields = ('title', 'programme', 'summary', 'issue_date', 'season',
                  'number_in_season', 'created_at', 'updated_at')


class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    programme = serializers.SlugRelatedField(
        slug_field='slug', queryset=Programme.objects.all())
    # XXX this is a bit hacky...
    start = serializers.DateTimeField(source='rr_start')
    end = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'programme', 'start', 'end', 'title', 'type','source')

    def get_title(self, schedule):
        return schedule.programme.name

    def get_end(self, schedule):
        # XXX temp workaround while dtstart not mandatory
        try:
            return schedule.recurrences.dtstart + schedule.runtime
        except TypeError:
            return None


class TransmissionSerializer(serializers.Serializer):
    programme = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)
    summary = serializers.CharField()
    slug =serializers.SlugField(max_length=100)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    schedule = serializers.IntegerField(source='schedule.id')
    type = serializers.CharField(max_length=1)
    url = serializers.URLField()

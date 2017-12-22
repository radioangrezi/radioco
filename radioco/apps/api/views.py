from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Slot, Schedule, Transmission
from django import forms
from django import utils
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
import datetime
import serializers


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer
    lookup_field = 'slug'


class SlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = serializers.SlotSerializer


class EpisodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = serializers.EpisodeSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    serializer_class = serializers.ScheduleSerializer


class TransmissionForm(forms.Form):
    after = forms.DateField(required=False)
    before = forms.DateField(required=False)

    def clean_after(self):
        after = self.cleaned_data.get('after')
        if after is None:
            return utils.timezone.now().replace(day=1).date()
        return after

    def clean_before(self):
        # XXX raise if before < after
        before = self.cleaned_data.get('before')
        if before is None:
            return self.clean_after() + datetime.timedelta(days=31)
        return before


class TransmissionViewSet(viewsets.GenericViewSet):
    queryset = Schedule.objects.all()
    serializer_class = serializers.TransmissionSerializer

    def list(self, request):
        data = TransmissionForm(request.query_params)
        data.is_valid()

        transmissions = Transmission.between(
            datetime.datetime.combine(
                data.cleaned_data.get('after'), datetime.time(0)),
            datetime.datetime.combine(
                data.cleaned_data.get('before'), datetime.time(23, 59, 59)))
        serializer = self.get_serializer(
            transmissions, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route()
    def now(self, request):
        now = utils.timezone.now()
        transmissions = Transmission.at(now)
        serializer = self.get_serializer(
            transmissions, many=True, context={'request': request})
        return Response(serializer.data)

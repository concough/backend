from rest_framework import serializers

from api.v1.serializers.general_serializers import OrganizationSerializer, EntranceTypeSerializer, \
    EntranceSetSerializer, \
    UUIDSerializer
from api.v1.serializers.product_serializers import ConcoughProductStatisticSerializer
from main.models import EntranceSet, Entrance


class ArchiveEntranceSetSerializer(serializers.ModelSerializer):
    entrance_count = serializers.IntegerField()

    class Meta:
        model = EntranceSet
        fields = ('id', 'title', 'code', 'entrance_count', 'updated')


class ArchiveEntranceSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    unique_key = UUIDSerializer(read_only=True)
    stats = ConcoughProductStatisticSerializer(read_only=True, many=True)
    booklets_count = serializers.IntegerField()
    duration = serializers.IntegerField()

    class Meta:
        model = Entrance
        fields = ("organization", "year", "month", "unique_key", "extra_data", "last_update",
                  "last_published", "stats", "booklets_count", "duration")

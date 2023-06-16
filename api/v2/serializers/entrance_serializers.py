from rest_framework import serializers

from api.v2.serializers.general_serializers import OrganizationSerializer, EntranceTypeSerializer, EntranceSetSerializer, \
    UUIDSerializer

from main.models import Entrance, EntranceLessonTagPackage


class EntranceSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    entrance_type = EntranceTypeSerializer(read_only=True)
    entrance_set = EntranceSetSerializer(read_only=True)
    unique_key = UUIDSerializer(read_only=True)
    booklets_count = serializers.IntegerField()
    duration = serializers.IntegerField()
    product_type = serializers.SerializerMethodField('get_type')

    def get_type(self, obj):
        return "Entrance"


    class Meta:
        model = Entrance
        fields = ("organization", "entrance_type", "entrance_set",
                    "year", "month", "unique_key", "published", "last_update",
                    "last_published", "extra_data", "booklets_count", "duration", "product_type")



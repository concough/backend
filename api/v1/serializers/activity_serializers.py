from rest_framework import serializers

from api.v1.serializers.general_serializers import UUIDSerializer, OrganizationSerializer, EntranceTypeSerializer, \
    EntranceSetSerializer
from api.v1.serializers.product_serializers import ConcoughProductStatisticSerializer
from main.models import ConcoughActivity, Entrance


__author__ = 'abolfazl'


class EntranceActSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    entrance_type = EntranceTypeSerializer(read_only=True)
    entrance_set = EntranceSetSerializer(read_only=True)
    unique_key = UUIDSerializer(read_only=True)
    stats = ConcoughProductStatisticSerializer(read_only=True, many=True)

    class Meta:
        model = Entrance
        fields = ("organization", "entrance_type", "entrance_set",
                    "year", "month", "unique_key", "published", "last_update",
                    "last_published", "extra_data", "stats")


class TargetObjectRelatedField(serializers.RelatedField):
    """
    A Custom field to use for the 'target' generic relationship
    """

    def to_representation(self, value):
        """
        Serialize Target instance base on type

        :param value:
        :return:
        """

        if isinstance(value, Entrance):
            serializer = EntranceActSerializer(value)
        else:
            raise Exception("Unexpected type of target object")

        #print serializer.data
        return serializer.data


class ActivitySerializer(serializers.ModelSerializer):
    target = TargetObjectRelatedField(read_only=True)

    class Meta:
        model = ConcoughActivity
        fields = ('target', 'created', 'activity_type')



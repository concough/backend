from uuid import uuid4

from django.db.models.aggregates import Count, Sum
from rest_framework import serializers

from api.v1.serializers.entrance_serializers import EntranceSerializer
from api.v1.serializers.general_serializers import UUIDSerializer
from main.models import Entrance, ConcoughUserSale

#import rest_framework.utils.serializer_helpers.ReturnDict


class SaleTargetObjectRelatedField(serializers.RelatedField):
    """
    A Custom field to use for the 'target' generic relationship
    """

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        """
        Serialize Target instance base on type

        :param value:
        :return:
        """

        if isinstance(value, Entrance):
            queryset = Entrance.objects.annotate(booklets_count=Count('booklets'), duration=Sum('booklets__duration')) \
                .get(unique_key=value.unique_key)
            serializer = EntranceSerializer(queryset, many=False)
        else:
            raise Exception("Unexpected type of target object")

        return serializer.data


class UserSaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConcoughUserSale
        fields = ('id', 'created', 'pay_amount')


class UserFullSaleSerializer(serializers.ModelSerializer):
    target = SaleTargetObjectRelatedField(read_only=True)

    class Meta:
        model = ConcoughUserSale
        fields = ('id', 'created', 'target', 'pay_amount')
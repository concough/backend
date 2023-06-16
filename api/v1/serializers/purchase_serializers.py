from django.db.models.aggregates import Count, Sum
from rest_framework import serializers

from api.v1.serializers.entrance_serializers import EntranceSerializer
from main.models import ConcoughUserPurchased, Entrance


class PurchaseTargetObjectRelatedField(serializers.RelatedField):
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


class ConcoughUserPurchasedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConcoughUserPurchased
        fields = ('created', 'updated', 'id', 'payed_amount', 'downloaded')


class ConcoughUserPurchasedFullSerializer(serializers.ModelSerializer):
    target = PurchaseTargetObjectRelatedField(read_only=True)

    class Meta:
        model = ConcoughUserPurchased
        fields = ('created', 'updated', 'id', 'payed_amount', 'downloaded', 'target')
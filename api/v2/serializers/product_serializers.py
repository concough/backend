from rest_framework import serializers

from main.models import EntranceSaleData, ConcoughProductStatistic, EntranceTagSaleData


class EntranceSaleDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = EntranceSaleData
        fields = ('updated', 'id', 'cost', 'cost_bon', 'year', 'month')


class EntranceTagsSaleDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = EntranceTagSaleData
        fields = ('updated', 'id', 'cost', 'q_count', 'year', 'month')


class ConcoughProductStatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConcoughProductStatistic
        fields = ('updated', 'downloaded', 'purchased')
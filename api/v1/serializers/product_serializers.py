from rest_framework import serializers

from main.models import EntranceSaleData, ConcoughProductStatistic


class EntranceSaleDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = EntranceSaleData
        fields = ('updated', 'id', 'cost', 'year', 'month')


class ConcoughProductStatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConcoughProductStatistic
        fields = ('updated', 'downloaded', 'purchased')
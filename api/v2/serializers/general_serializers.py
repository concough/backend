from rest_framework import serializers

from api.v2.serializers.product_serializers import EntranceSaleDataSerializer
from main.models import Organization, EntranceType, ExaminationGroup, EntranceSet, EntranceLesson

__author__ = 'abolfazl'


class UUIDSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return instance.get_hex()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('title', 'id')


class EntranceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceType
        fields = ('title', )


class EntranceTypeWithSaleSerializer(serializers.ModelSerializer):
    sale_data = EntranceSaleDataSerializer(read_only=True, many=True)

    class Meta:
        model = EntranceType
        fields = ('id', 'title', 'sale_data')


class EntranceTypeWithIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceType
        fields = ('title', 'id')


class ExaminationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExaminationGroup
        fields = ('title', )


class ExaminationGroupWithIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExaminationGroup
        fields = ('title', 'id')


class EntranceSetSerializer(serializers.ModelSerializer):
    group = ExaminationGroupSerializer(read_only=True)

    class Meta:
        model = EntranceSet
        fields = ('id', 'title', 'group', 'updated')


class EntranceLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceLesson
        fields = ('title', 'full_title', 'id')



from rest_framework import serializers

from api.v2.serializers.entrance_serializers import EntranceSerializer
from api.v2.serializers.general_serializers import EntranceLessonSerializer
from main.models import EntranceBooklet, EntranceBookletDetail


class EntranceBookletSerializer(serializers.ModelSerializer):
    entrance = EntranceSerializer(many=False, read_only=True)

    class Meta:
        model = EntranceBooklet
        fields = ('title', 'id', 'entrance')


class EntranceBookletDetailSerializer(serializers.ModelSerializer):
    lesson = EntranceLessonSerializer(many=False, read_only=True)

    class Meta:
        model = EntranceBookletDetail
        fields = ('lesson', 'q_count', 'id')

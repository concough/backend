from rest_framework import serializers

from api.v2.serializers.entrance_booklet_serializers import EntranceBookletDetailSerializer
from api.v2.serializers.general_serializers import UUIDSerializer
from main.models import EntranceLessonTagPackage


class EntranceTagPackageSerializer(serializers.ModelSerializer):
    unique_key = UUIDSerializer(read_only=True)
    booklet_detail = EntranceBookletDetailSerializer(read_only=True, many=False)
    product_type = serializers.SerializerMethodField('get_type')

    def get_type(self, obj):
        return "EntranceTag"

    class Meta:
        model = EntranceLessonTagPackage
        fields = ("unique_key", "booklet_detail", "create_time", "update_time", "q_count")

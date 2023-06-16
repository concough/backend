# coding=utf-8
from rest_framework import serializers

from api.models import Profile
from api.v2.serializers.auth_serializers import UserSerializer1
from main.models import EntranceType


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceType
        fields = ('title', 'code')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer1()
    grade_string = serializers.SerializerMethodField('get_grade')

    def get_grade(self, obj):
        try:
            t = EntranceType.objects.get(code=obj.grade)
            return t.title
        except:
            return "کارشناسی"

    class Meta:
        model = Profile
        fields = ('user', 'id', 'grade', 'modified', 'gender', 'birthday', 'grade_string')

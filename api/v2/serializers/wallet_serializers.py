from rest_framework import serializers

from main.models import UserWallet


class UserWalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserWallet
        fields = ('created', 'updated', 'cash')

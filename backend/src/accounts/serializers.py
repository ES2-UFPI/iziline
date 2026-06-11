from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    # A força da senha é validada por AUTH_PASSWORD_VALIDATORS no service.
    username = serializers.CharField(max_length=150, validators=[UnicodeUsernameValidator()])
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.get_full_name() or obj.get_username()

from rest_framework import serializers


def username_not_me_validator(value):
    if value == 'me':
        raise serializers.ValidationError("The name 'me' is not available")

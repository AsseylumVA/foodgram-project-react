from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            )
        ]


class UserMeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class UserSingupSerializer(serializers.Serializer):

    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(max_length=254, required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'username ''me'' is not avilable')
        return value


class UserCreateTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True,
    )

import datetime as dt

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.validators import username_not_me_validator


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('__all__')
        model = Title

    def validate_year(self, value):
        year = dt.date.today().year
        if not value <= year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        model = User

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SignupSerializer(serializers.Serializer):

    username = serializers.CharField(validators=[
        UnicodeUsernameValidator, username_not_me_validator])
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        fields = ('username', 'email')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(validators=[
        UnicodeUsernameValidator, username_not_me_validator])
    confirmation_code = serializers.CharField()

    class Meta:
        fields = ('username', 'confirmation_code')

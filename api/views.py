from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, generics
from rest_framework_simplejwt.tokens import AccessToken

from reviews.filters import TitleFilter
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .permissions import (AdminOnly, AdminOrReadOnly,
                          IsOwnerOrAdminOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignupSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)


def rating(title):
    reviews = Review.objects.select_related('author').filter(title=title)
    score = reviews.aggregate(Avg('score'))['score__avg']
    title.rating = int(round(score))
    title.save()


class ListCreateDestroyViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               GenericViewSet):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [AdminOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TitleFilter

    def perform_create(self, serializer):
        category_slug = self.request.data.get('category')
        genre_slugs = self.request.data.getlist('genre')
        category = generics.get_object_or_404(Category, slug=category_slug)
        genre = Genre.objects.filter(slug__in=genre_slugs)
        serializer.save(category=category, genre=genre)

    def perform_update(self, serializer):
        category_slug = self.request.data.get('category')
        genre_slugs = self.request.data.getlist('genre')
        category = generics.get_object_or_404(Category, slug=category_slug)
        genre = Genre.objects.filter(slug__in=genre_slugs)
        serializer.save(category=category, genre=genre)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrAdminOrModeratorOrReadOnly, ]

    def get_queryset(self):
        title = generics.get_object_or_404(Title,
                                           pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = generics.get_object_or_404(Title, pk=title_id)
        if (Review.objects.filter(author=self.request.user,
                                  title=title).exists()):
            raise serializers.ValidationError('Already reviewed')
        serializer.save(author=self.request.user, title=title)
        rating(title)

    def perform_update(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = generics.get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
        rating(title)

    def perform_destroy(self, instance):
        instance.delete()
        title_id = self.kwargs.get('title_id')
        title = generics.get_object_or_404(Title, pk=title_id)
        rating(title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrModeratorOrReadOnly, ]

    def get_queryset(self):
        title = generics.get_object_or_404(Title,
                                           pk=self.kwargs.get('title_id'))
        review = generics.get_object_or_404(Review,
                                            pk=self.kwargs.get('review_id'),
                                            title=title)
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        title = generics.get_object_or_404(Title,
                                           pk=self.kwargs.get('title_id'))
        review = generics.get_object_or_404(Review,
                                            pk=self.kwargs.get('review_id'),
                                            title=title)
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminOnly, ]
    filter_backends = [filters.SearchFilter, ]
    lookup_field = 'username'
    search_fields = ['=username', ]

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=(IsAuthenticated, ))
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user,)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, request.data, partial=True)
            if serializer.is_valid():
                if (user.role != User.ADMIN
                        or user.is_superuser is not True):
                    serializer.validated_data.pop('role', False)
                    serializer.update(instance=user,
                                      validated_data=serializer.validated_data)
                else:
                    serializer.update(instance=user,
                                      validated_data=serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return None


@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if not User.objects.filter(username=request.data['username'],
                                       email=request.data['email']).exists():
                if User.objects.filter(
                    username=request.data['username']
                ).exists():
                    return Response(
                        {'error': 'invalid email'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif User.objects.filter(email=request.data['email']).exists():
                    return Response(
                        {'error': 'invalid username'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    serializer.save()
            user = User.objects.get(username=request.data['username'],
                                    email=request.data['email'])
            confirmation_code = default_token_generator.make_token(user)
            user.email_user(subject='Сonfirmation code',
                            message=f'Code is {confirmation_code}',
                            from_email='administration@yamdb.com')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def token(request):
    if request.method == 'POST':
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, username=request.data['username'])
            confirmation_code = request.data['confirmation_code']
            if default_token_generator.check_token(user, confirmation_code):
                token = AccessToken.for_user(user)
                response = {'username': request.data['username'],
                            'token': str(token)}
                return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

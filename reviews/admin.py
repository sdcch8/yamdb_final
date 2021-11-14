from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, TitleGenre


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'year',
        'description',
        'category',
    )
    search_fields = ('name', 'description')
    list_filter = ('name', 'year', 'genre', 'category')
    empty_value_display = '-empty-'


@admin.register(TitleGenre)
class TitleGenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'genre',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'text',
        'author',
        'score',
        'pub_date',
    )
    search_fields = ('text', 'author')
    list_filter = ('pub_date', 'score')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('text', 'author')
    list_filter = ('pub_date',)

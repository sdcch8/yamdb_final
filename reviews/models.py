from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    description = models.TextField()
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 related_name='categories',
                                 null=True)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews',
                              null=True)
    text = models.TextField()
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               null=True)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-pub_date']
        models.UniqueConstraint(
            fields=['title', 'author'],
            name='only_one_review'
        )


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments', null=True)
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments', null=True)
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-pub_date']

from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(CreatedModel):
    title = models.CharField(
        max_length=200,
        verbose_name="Заглавие",
        help_text="Укажите название группы."
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Название",
        help_text="Укажите название группы."
    )
    description = models.TextField(
        verbose_name="Название",
        help_text="Укажите описание группы"
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    CONSTANT_STR = 15
    text = models.TextField(
        verbose_name="Текст",
        help_text="Укажите текст поста"
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text="Группа поста"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text="Автор поста"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:self.CONSTANT_STR]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        verbose_name='Комментарий поста',
        help_text='Комментарий поста',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст комментария',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:self.CONSTANT_STR]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор подписки',
        help_text='Автор подписки',
    )
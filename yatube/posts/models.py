from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
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


class Post(models.Model):
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

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:self.CONSTANT_STR]

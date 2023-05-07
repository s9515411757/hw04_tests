from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост более 15-и символов',
            group=cls.group,
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user,
        )

    def test_models_post_group_text(self):
        """Проверка магического метода __str__"""
        self.assertEqual(
            str(self.post),
            self.post.text[:Post.CONSTANT_STR]
        )

    def test_post_verbose_name(self):
        """Проверка атрибуты verbose_name для модели Post"""
        field_verboses = [
            ('text', 'Текст'),
            ('group', 'Группа'),
            ('author', 'Автор')
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """Проверка атрибуты help_text для модели Post"""
        field_help_texts = [
            ('text', 'Укажите текст поста'),
            ('group', 'Группа поста'),
            ('author', 'Автор поста')
        ]
        for field, expected_value in field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(
                        field).help_text,
                    expected_value
                )

    def test_group_verbose_name(self):
        """Проверка атрибуты verbose_name для модели Group"""
        group = self.group
        field_verboses = [
            ('title', 'Заглавие'),
            ('slug', 'Название'),
            ('description', 'Название')
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_group_help_text(self):
        """Проверка атрибуты help_tex для модели Group"""
        field_help_texts = [
            ('title', 'Укажите название группы.'),
            ('slug', 'Укажите название группы.'),
            ('description', 'Укажите описание группы')
        ]
        for field, expected_value in field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    expected_value)

    def test_follow_verbose_name(self):
        """Проверка атрибуты verbose_name для модели Follow"""
        field_verboses = [
            ('user', 'Подписчик'),
            ('author', 'Автор подписки'),
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_follow_help_text(self):
        """Проверка атрибуты help_tex для модели Follow"""
        field_help_texts = [
            ('user', 'Подписчик'),
            ('author', 'Автор подписки'),
        ]
        for field, expected_value in field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).help_text,
                    expected_value
                )

    def test_comment_verbose_name(self):
        """Проверка атрибуты verbose_name для модели Comment"""
        field_verboses = [
            ('post', 'Комментарий поста'),
            ('author', 'Автор комментария'),
            ('text', 'Текст комментария')
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_help_text(self):
        """Проверка атрибуты help_tex для модели Comment"""
        field_help_texts = [
            ('post', 'Комментарий поста'),
            ('author', 'Автор комментария'),
            ('text', 'Текст комментария')
        ]
        for field, expected_value in field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    expected_value
                )
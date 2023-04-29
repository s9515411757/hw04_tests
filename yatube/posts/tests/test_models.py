from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, CONSTANT_STR

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='a' * 20,
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            group=cls.group,
            author=cls.user,
        )

    def test_models_post_group_text(self):
        """Проверка магического метода __str__"""
        self.assertEqual(str(PostModelTest.post), 'a' * CONSTANT_STR)
        self.assertEqual(str(PostModelTest.post), 'a' * CONSTANT_STR)

    def test_post_verbose_name(self):
        """Проверка атрибуты verbose_name для модели Post"""
        post = PostModelTest.post
        field_verboses = [
            ('text', 'Текст'),
            ('group', 'Группа'),
            ('author', 'Автор')
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

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
                    PostModelTest.post._meta.get_field(
                        field).help_text,
                    expected_value
                )

    def test_group_verbose_name(self):
        """Проверка атрибуты verbose_name для модели Group"""
        group = PostModelTest.group
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
                    PostModelTest.group._meta.get_field(field).help_text,
                    expected_value)

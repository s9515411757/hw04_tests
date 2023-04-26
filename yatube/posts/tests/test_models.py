from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

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
            text='a' * 20,
            group=cls.group,
            author=cls.user,
        )

    def test_models_post_text(self):
        self.assertEqual(PostModelTest.post.text, 'a' * 15)

    def test_models_group_title(self):
        self.assertEqual(PostModelTest.group.title, 'Тестовая группа')

    def test_post_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_help_text(self):
        field_help_texts = {
            'text': 'Укажите текст поста',
            'group': 'Группа поста',
            'author': 'Автор поста',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(
                        field).help_text,
                    expected_value
                )

    def test_group_verbose_name(self):
        group = PostModelTest.group
        field_verboses = [
            ('title', 'Заглавие'),
            ('slug', 'Название'),
            ('description', 'Название'),
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_group_help_text(self):
        field_help_texts = [
            ('title', 'Укажите название группы.'),
            ('slug', 'Укажите название группы.'),
            ('description', 'Укажите описание группы'),
        ]
        for field, expected_value in field_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(field).help_text, expected_value)

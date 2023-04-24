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
            title='a' * 20,
            slug='test',
            description='Тестовый текст'
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            group=cls.group,
            author=cls.user,


        )

    def test_post_text(self):
        """Содержимое поля title преобразуется в slug."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], 'a' * 15)

    def test_group_title(self):
        group = PostModelTest.group
        self.assertEqual(group.title, 'a' * 20)
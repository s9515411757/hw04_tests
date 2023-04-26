from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cant_create_existing_slug(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост1'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostCreateFormTests.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.get(text='Тестовый пост1')
        self.assertEqual(post.text, 'Тестовый пост1')
        self.assertEqual(post.author.username, 'auth')

    def test_create_existing_slug(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2',
        }
        self.assertEqual(Post.objects.count(), post_count)
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.get(text='Тестовый пост2')
        self.assertEqual(post.text, 'Тестовый пост2')
        self.assertEqual(post.author.username, 'auth')

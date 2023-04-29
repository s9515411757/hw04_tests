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
        """При отправке валидной формы со страницы создания поста
         reverse('posts:create_post') создаётся новая запись в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост1',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.get(text=form_data['text'])
        form_data_result = [
            (post.text, form_data['text']),
            (post.author, self.user),
            (post.group, self.group)
        ]
        for first_object, first_result in form_data_result:
            with self.subTest(context=first_object):
                self.assertEqual(first_object, first_result)

    def test_create_existing_slug(self):
        """При отправке валидной формы со страницы редактирования
         поста reverse('posts:post_edit', args=('post_id',))
         происходит изменение поста с post_id в базе данных."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group.pk
        }
        self.assertEqual(Post.objects.count(), post_count)
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
                ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.get(text='Тестовый пост2')
        form_data_result = [
            (post.text, 'Тестовый пост2'),
            (post.author, self.user),
            (post.group, self.group)
        ]
        for first_object, first_result in form_data_result:
            with self.subTest(context=first_object):
                self.assertEqual(first_object, first_result)


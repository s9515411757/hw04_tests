from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_1 = User.objects.create_user(username='auth_1')
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
        cls.templates_url_names = [
            ('/', 'posts/index.html', 'all'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html', 'all'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html', 'all'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html', 'all'),
            (f'/posts/{cls.post.id}/edit/',
             'posts/create_post.html', 'author'),
            ('/create/', 'posts/create_post.html', 'authorized'),
            ('/unexisting_page/', '', 404)
        ]
        cls.templates_names = [
            ('/', reverse('posts:index')),
            (f'/group/{cls.group.slug}/', reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug})),
            (f'/profile/{cls.user.username}/', reverse(
                'posts:profile', kwargs={'username': cls.user.username})),
            (f'/posts/{cls.post.id}/', reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id})),
            (f'/posts/{cls.post.id}/edit/', reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id})),
            ('/create/', reverse('posts:post_create')),
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

    def test_urls_user_exists_at_desired_location(self):
        """Проверка неавтоизованному/автоизованному пользователю на
        доступные адреса"""
        for url, templates, access in self.templates_url_names:
            with self.subTest(address=url):
                if access in ('all', 'author', 'authorized'):
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, 200)
                if access == 'all':
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, 200)
                if access == 404:
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """Проверка шаблона неавтоизованному/автоизованному пользователю"""
        for url, templates, access in self.templates_url_names:
            with self.subTest(address=url):
                if access in ('all', 'author', 'authorized'):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)
                if access == 'all':
                    response = self.guest_client.get(url)
                    self.assertTemplateUsed(response, templates)

    def test_urls_authorized_client_template_author(self):
        """Проверка автоизованному пользователю на автора"""
        for url, templates, access in self.templates_url_names:
            if access == 'author':
                with self.subTest(address=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)

    def test_urls_authorized_client_template_not_author(self):
        """Проверка автоизованному пользователю на не автора"""
        for url, templates, access in self.templates_url_names:
            if access == 'author':
                with self.subTest(address=url):
                    response = self.authorized_client_1.get(url)
                    self.assertRedirects(
                        response, f'/posts/{self.post.pk}/')
                    self.assertEqual(response.status_code, 302)

    def test_urls_guest_client_correct_template(self):
        """Проверка неавтоизованному пользователю на перенаправления"""
        for url, templates, access in self.templates_url_names:
            if access in ('author', 'authorized'):
                with self.subTest(address=url):
                    response = self.guest_client.get(url)
                    self.assertRedirects(
                        response, f'/auth/login/?next={url}')
                    self.assertEqual(response.status_code, 302)

    def test_urls_guest_client_correct_template_name(self):
        """Проверка шаблонами и адресами"""
        for url, name in PostURLTests.templates_names:
            with self.subTest(address=name):
                self.assertEqual(url, name)

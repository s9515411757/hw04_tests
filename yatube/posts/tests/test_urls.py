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

    def test_urls_authorized_client_correct_template_all(self):
        """Проверка автоизованному пользователю на все доступные страницы"""
        for url, templates, access in self.templates_url_names:
            if access == 'all':
                with self.subTest(address=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)
                    self.assertEqual(response.status_code, 200)

    def test_urls_guest_client_correct_template_all(self):
        """Проверка неавтоизованному пользователю на все доступные страницы"""
        for url, templates, access in self.templates_url_names:
            if access == 'all':
                with self.subTest(address=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)
                    self.assertEqual(response.status_code, 200)

    def test_urls_authorized_client_template_author(self):
        """Проверка автоизованному пользователю на автора"""
        for url, templates, access in self.templates_url_names:
            if access == 'author':
                with self.subTest(address=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)
                    self.assertEqual(response.status_code, 200)

    def test_urls_authorized_client_template_authorized(self):
        """Проверка автоизованному пользователю на создание поста"""
        for url, templates, access in self.templates_url_names:
            if access == 'authorized':
                with self.subTest(address=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)
                    self.assertEqual(response.status_code, 200)

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

    def test_url_guest_client_template_404(self):
        """Проверка несуществующей страницы"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

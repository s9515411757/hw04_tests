from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='user')
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
            (reverse('posts:index'), 'posts/index.html', 'all', 200),
            (reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
             'posts/group_list.html', 'all', 200),
            (reverse('posts:profile', kwargs={'username': cls.user.username}),
             'posts/profile.html', 'all', 200),
            (reverse('posts:post_detail', kwargs={'post_id': cls.post.id}),
             'posts/post_detail.html', 'all', 200),
            (reverse('posts:post_edit', kwargs={'post_id': cls.post.id}),
             'posts/create_post.html', 'author', 200),
            (reverse('posts:post_create'), 'posts/create_post.html',
             'authorized', 200),
            ('/unexisting_page/', '', '404', 404)
        ]
        cls.author = [f'/posts/{cls.post.id}/edit/', f'/posts/{cls.post.pk}/']
        cls.no_author = [
            f'/posts/{cls.post.id}/edit/',
            f'/auth/login/?next=/posts/{cls.post.id}/edit/'
        ]
        cls.authorized = [reverse('posts:post_create'), '/auth/login/?next=/create/']
        cls.redirect_no_authorized = [cls.no_author, cls.authorized]
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

    def test_urls_user_exists_at_desired_location(self):
        """Проверка неавтоизовнному/автоизованному поальзователю на
        доступные адреса"""
        for url, templates, access, status_code in self.templates_url_names:
            with self.subTest(address=url):
                if access in ('author', 'authorized'):
                    response = self.authorized_client.get(url)
                elif access == 'all':
                    response = self.guest_client.get(url)
                elif access == '404':
                    response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """Проверка шаблона неавтоизованному/автоизованному пользователю"""
        for url, templates, access, status_code in self.templates_url_names:
            with self.subTest(address=url):
                if access in ('author', 'authorized'):
                    response = self.authorized_client.get(url)
                elif access == 'all':
                    response = self.guest_client.get(url)
                else:
                    break
                self.assertTemplateUsed(response, templates)

    def test_urls_authorized_client_template_not_author(self):
        """Проверка автоизованному пользователю на не автора"""
        self.authorized_client.force_login(self.user_auth)
        url, redirect = self.author
        self.assertRedirects(self.authorized_client.get(url), redirect)

    def test_urls_guest_client_correct_template(self):
        """Проверка неавтоизованному пользователю на перенаправления"""
        for url, redirect in self.redirect_no_authorized:
            with self.subTest(address=url):
                self.assertRedirects(self.guest_client.get(url), redirect)

    def test_urls_guest_client_correct_template_name(self):
        """Проверка шаблонами и адресами"""
        for url, name in PostURLTests.templates_names:
            with self.subTest(address=name):
                self.assertEqual(url, name)

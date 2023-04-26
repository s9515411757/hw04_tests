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
            ('/', 'posts/index.html', True, 200),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html', True, 200),
            (f'/profile/{cls.user.username}/',
             'posts/profile.html', True, 200),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html', True, 200),
            (f'/posts/{cls.post.id}/edit/',
             'posts/create_post.html', False, 200),
            ('/create/', 'posts/create_post.html', False, 200),
            ('/unexisting_page/', '', True, 404),
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

    def test_urls_authorized_client_correct_template(self):
        for url, templates, access, code_status in \
                PostURLTests.templates_url_names:
            if not access and code_status == 200:
                with self.subTest(address=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, templates)
                with self.subTest(address=url):
                    response = self.guest_client.get(url)
                    self.assertRedirects(
                        response, f'/auth/login/?next={url}')

    def test_urls_guest_client_correct_template(self):
        for i in PostURLTests.templates_url_names:
            if i[2] and i[3] == 200:
                with self.subTest(address=i[0]):
                    response = self.guest_client.get(i[0])
                    self.assertTemplateUsed(response, i[1])

    def test_urls_guest_client_correct_template_status_code(self):
        for i in PostURLTests.templates_url_names:
            if i[2]:
                with self.subTest(address=i[0]):
                    response = self.guest_client.get(i[0])
                    self.assertEqual(response.status_code, i[3])

    def test_urls_guest_client_correct_template_st(self):
        for url, name in PostURLTests.templates_names:
            with self.subTest(address=name):
                self.assertEqual(url, name)

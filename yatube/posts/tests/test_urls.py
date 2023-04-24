from django.contrib.auth import get_user_model
from django.test import TestCase, Client

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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_authorized_client_correct_template(self):
        templates_url_names = PostURLTests.templates_url_names
        for i in templates_url_names:
            if not i[2] and i[3] == 200:
                with self.subTest(address=i[0]):
                    response = self.authorized_client.get(i[0])
                    self.assertTemplateUsed(response, i[1])

    def test_urls_guest_client_correct_template(self):
        templates_url_names = PostURLTests.templates_url_names
        for i in templates_url_names:
            if i[2] and i[3] == 200:
                with self.subTest(address=i[0]):
                    response = self.guest_client.get(i[0])
                    self.assertTemplateUsed(response, i[1])

    def test_urls_guest_client_correct_template_status_code(self):
        templates_url_names = PostURLTests.templates_url_names
        for i in templates_url_names:
            if i[2]:
                with self.subTest(address=i[0]):
                    response = self.guest_client.get(i[0])
                    self.assertEqual(response.status_code, i[3])

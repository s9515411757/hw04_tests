from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_no_post = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание',
        )
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
        cls.template_post = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': cls.user.username})
        ]
        cls.template_group_profile = [
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': cls.user.username})
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def context(self, response):
        context_post = [
            (response.text, self.post.text),
            (response.group, self.group),
            (response.author, self.user)
        ]
        for first_object, reverse_name in context_post:
            with self.subTest(first_object=first_object):
                self.assertEqual(first_object, reverse_name)

    def test_context_post_detail_template(self):
        """Проверка контекста в шаблоне post_detail"""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        )
        self.context(response.context.get('post'))

    def test_context_create_post_template(self):
        """Проверка контекста в шаблоне create_post"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)

    def test_context_index_group_list_profile_template(self):
        """Проверка контекста в шаблонах index, group_list, profile"""
        for reverse_url in self.template_post:
            response = self.authorized_client.get(reverse_url).context.get(
                'page_obj'
            ).object_list[0]
            self.context(response)

    def test_form_for_correct_post(self):
        """Проверка формы на правильный пост"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk})
        )
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)
        self.assertEqual(response.context['form'].instance.pk, self.post.pk)

    def test_post_of_the_second_group(self):
        """Проверка существуют ли посты второй группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_no_post.slug})
        )

        self.assertNotIn(self.post, response.context['page_obj'])


class PostPaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.NUMBER_OF_POST = 20

        cls.post = Post.objects.bulk_create([
            Post(text=f'Тестовый пост {number}',
                 group=cls.group,
                 author=cls.user, )
            for number in range(cls.NUMBER_OF_POST)
        ])

        cls.temlate_name = [
            (reverse('posts:index')),
            (reverse('posts:group_list',
                     kwargs={'slug': cls.group.slug})),
            (reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}))
        ]

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        for reverse_name in self.temlate_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.QUANTITY_POSTS)

    def test_second_page_contains_three_records(self):
        if self.NUMBER_OF_POST % settings.QUANTITY_POSTS == 0:
            page_obj = settings.QUANTITY_POSTS
            page = self.NUMBER_OF_POST // settings.QUANTITY_POSTS
        else:
            page_obj = self.NUMBER_OF_POST % settings.QUANTITY_POSTS
            page = self.NUMBER_OF_POST // settings.QUANTITY_POSTS + 1
        for reverse_name in self.temlate_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + f'?page={page}')
                self.assertEqual(len(response.context['page_obj']), page_obj)

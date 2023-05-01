from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_1 = Group.objects.create(
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
        return [
            (response.text, self.post.text),
            (response.group, self.group),
            (response.author, self.user)
        ]

    def test_task_detail_pages_show_correct_context(self):
        """Проверка контекста в шаблоне post_detail"""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        ).context.get('post')

        for first_object, reverse_name in self.context(response):
            with self.subTest(first_object=first_object):
                self.assertEqual(first_object, reverse_name)

    def test_list_show_correct_context(self):
        """Проверка контекста в шаблоне create_post"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = [
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField)
        ]
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form')
                self.assertIsInstance(form_field, PostForm)

    def test_index_group_list_profile_correct_context(self):
        """Проверка контекста в шаблонах index, group_list, profile"""
        for reverse_url in self.template_post:
            response = self.authorized_client.get(reverse_url).context.get(
                'post'
            )
            for first_object, reverse_name in self.context(response):
                with self.subTest(first_object=first_object):
                    self.assertEqual(first_object, reverse_name)

    def test_form_post_create_show_correct_context(self):
        """Проверка в шаблоне post_create на форму"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_field = response.context['form']
        self.assertIsInstance(form_field, PostForm)

    def test_form_post_detail_correct_context(self):
        """Проверка контекста в шаблоне post_detail"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(response.context['is_edit'])

    def test_group_correct_context(self):
        """Проверка существуют ли посты второй группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_1.slug})
        )
        self.assertFalse(response.context['page_obj'])

    def test_group_profile_detail_object_list_correct_context(self):
        """Проверка контекста на страницах автора и группы"""
        for reverse_url in self.template_group_profile:
            response = self.authorized_client.get(reverse_url)
            for post in response.context['page_obj'].object_list:
                for first_object, reverse_name in self.context(post):
                    with self.subTest(first_object=first_object):
                        self.assertEqual(first_object, reverse_name)


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

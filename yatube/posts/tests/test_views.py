from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
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
        cls.reverse_names = [
            ('posts/index.html', reverse('posts:index')),
            ('posts/group_list.html', reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug})),
            ('posts/profile.html', reverse(
                'posts:profile', kwargs={'username': cls.user.username})),
            ('posts/post_detail.html', reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id})),
            ('posts/create_post.html', reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id})),
            ('posts/create_post.html', reverse('posts:post_create')),
        ]
        cls.template = [
            ('posts/post_detail.html', reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id})),
            ('posts/create_post.html', reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id})),
            ('posts/create_post.html', reverse('posts:post_create')),
        ]
        cls.created_post = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': cls.user.username})
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_task_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, PostPagesTests.post.text)
        self.assertEqual(first_object.group, PostPagesTests.group)
        self.assertEqual(first_object.author, PostPagesTests.user)

    def test_task_detail_pages_show_correct_context(self):
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostPagesTests.post.id})))
        self.assertEqual(response.context.get('post').text,
                         PostPagesTests.post.text)
        self.assertEqual(response.context.get('post').group.slug,
                         PostPagesTests.group.slug)
        self.assertEqual(response.context.get('post').author.username,
                         PostPagesTests.post.author.username)

    def test_task_list_show_correct_context(self):
        created_post = PostPagesTests.created_post
        for reverse_name in created_post:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, PostPagesTests.post.text)
                self.assertEqual(first_object.group, PostPagesTests.group)
                self.assertEqual(first_object.author, PostPagesTests.user)

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        context = [
            (response.context['post'].id, self.post.id),
        ]
        for context, reverse_context in context:
            with self.subTest(context=context):
                self.assertEqual(context, reverse_context)

    def test_group_list_profile_correct_context(self):
        for created_post in PostPagesTests.created_post:
            with self.subTest(created_post=created_post):
                first_object = self.guest_client.get(
                    created_post
                ).context['page_obj'][0]
                context = (
                    (first_object.author, PostPagesTests.user),
                    (first_object.text, PostPagesTests.post.text),
                    (first_object.group, PostPagesTests.group),
                )
                for context, reverse_context in context:
                    with self.subTest(reverse_context=reverse_context):
                        self.assertEqual(context, reverse_context)


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
        cls.NUMBER_OF_POST = 13

        cls.post = Post.objects.bulk_create([
            Post(text=f'Тестовый пост {number}',
                 group=cls.group,
                 author=cls.user, )
            for number in range(cls.NUMBER_OF_POST)
        ])

        cls.temlate_name = [
            (reverse('posts:index')),
            (reverse('posts:group_list',
                     kwargs={'slug': PostPaginatorViewsTest.group.slug})),
            (reverse(
                'posts:profile',
                kwargs={'username': PostPaginatorViewsTest.user.username}))

        ]

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        temlate_name = PostPaginatorViewsTest.temlate_name
        for reverse_name in temlate_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.QUANTITY_POSTS)

    def test_second_page_contains_three_records(self):
        temlate_name = PostPaginatorViewsTest.temlate_name
        page_obj = (PostPaginatorViewsTest.NUMBER_OF_POST %
                    settings.QUANTITY_POSTS)
        page = (PostPaginatorViewsTest.NUMBER_OF_POST //
                settings.QUANTITY_POSTS + 1)
        for reverse_name in temlate_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name+f'?page={page}')
                self.assertEqual(len(response.context['page_obj']), page_obj)

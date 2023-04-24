from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

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

    def test_pages_uses_correct_template(self):
        reverse_names = PostPagesTests.reverse_names
        for template, reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_task_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        task_author_0 = first_object.author
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_group_0, PostPagesTests.group)
        self.assertEqual(task_author_0, PostPagesTests.user)

    def test_task_detail_pages_show_correct_context(self):
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostPagesTests.post.id})))
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').group.slug,
                         PostPagesTests.group.slug)

    def test_task_list_show_correct_context(self):
        created_post = PostPagesTests.created_post
        for reverse_name in created_post:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                task_text_0 = first_object.text
                task_group_0 = first_object.group
                task_author_0 = first_object.author
                self.assertEqual(task_text_0, 'Тестовый пост')
                self.assertEqual(task_group_0, PostPagesTests.group)
                self.assertEqual(task_author_0, PostPagesTests.user)


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

        for i in range(13):
            Post.objects.create(
                text=f'Тестовый пост {i}',
                group=cls.group,
                author=cls.user,
            )

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
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        temlate_name = PostPaginatorViewsTest.temlate_name
        for reverse_name in temlate_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

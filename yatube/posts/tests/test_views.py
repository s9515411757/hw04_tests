import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


from ..models import Post, Group, Follow
from ..forms import PostForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def context(self, response):
        context_post = [
            (response.text, self.post.text),
            (response.group, self.group),
            (response.author, self.user),
            (response.image, self.post.image)
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

    def test_cache(self):
        """Проверка кэша"""
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            text='Новый тестовый пост',
            author=self.user,
        )
        content_second = self.authorized_client.get(reverse('posts:index')
                                                    ).content
        self.assertEqual(
            response.content,
            content_second
        )
        cache.clear()
        self.assertNotEqual(
            content_second,
            self.authorized_client.get(reverse('posts:index')).content
        )


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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
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


class FollowTestsPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.first_user = User.objects.create_user(username='first_auth')
        cls.second_user = User.objects.create_user(username='second_auth')
        cls.first_author = User.objects.create_user(username='first_author')
        cls.second_author = User.objects.create_user(username='second_author')
        cls.first_post = Post.objects.create(
            author=cls.first_author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.second_post = Post.objects.create(
            author=cls.second_author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.first_author_profile_follow = (
            'posts:profile_follow', [cls.first_author.username])
        cls.first_author_profile_unfollow = (
            'posts:profile_unfollow', [cls.first_author.username])
        cls.first_user_profile_follow = (
            'posts:profile_follow', [cls.first_user.username])
        cls.second_author_profile_follow = (
            'posts:profile_follow', [cls.second_author.username])
        cls.follow_index = ('posts:follow_index', None)

    def setUp(self):
        self.guest_client = Client()
        self.first_authorized_client = Client()
        self.second_authorized_client = Client()
        self.first_authorized_client.force_login(self.first_user)
        self.second_authorized_client.force_login(self.second_user)

    def tearDown(self):
        cache.clear()

    def test_follow(self):
        """Проверка создания/удаления подписки"""
        follow_count = Follow.objects.count()
        self.first_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.first_author.username}))
        self.assertEqual(Follow.objects.count(),
                         follow_count + 1)
        self.first_authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.first_author.username})
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_user_can_subscribe_only_once(self):
        """Проверка пользователь может подписаться только один раз"""
        follow_count = Follow.objects.count()
        self.first_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.first_author.username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        follow_count = Follow.objects.count()
        self.first_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.first_author.username})
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_user_cannot_subscribe_to_himself(self):
        """Проверка пользователь не может подписаться сам на себя"""
        follow_count = Follow.objects.count()
        self.first_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.first_user.username}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_subscription_list_context(self):
        """Проверка на контекст списка подписок"""
        self.first_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.first_author.username}))
        response = self.first_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.context['page_obj'][0].id,
                         self.first_post.id)

    def test_follow_correct_context_of_list_subscriptions_and_posts(self):
        """Проверка на корректный контекст списка подписок и постов"""
        self.first_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.first_author.username}))
        self.second_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.second_author.username}))
        response = self.second_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(response.context['page_obj'][0].id,
                            self.first_post.id)

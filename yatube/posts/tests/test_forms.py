import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cant_create_existing_slug(self):
        """При отправке валидной формы со страницы создания поста
         reverse('posts:create_post') создаётся новая запись в базе данных"""
        form_data = {
            'text': 'Тестовый пост1',
            'group': self.group.pk
        }
        Post.objects.all().delete()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(
            Post.objects.all().count(),
            1
        )
        post = Post.objects.first()
        form_data_result = [
            (post.text, form_data['text']),
            (post.author, self.user),
            (post.group.pk, form_data['group'])
        ]
        for first_object, first_result in form_data_result:
            with self.subTest(first_object=first_object):
                self.assertEqual(first_object, first_result)

    def test_create_existing_slug(self):
        """При отправке валидной формы со страницы редактирования
         поста reverse('posts:post_edit', args=('post_id',))
         происходит изменение поста с post_id в базе данных."""
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group.pk
        }
        post_count = Post.objects.all().count()
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.all().count(),
            post_count
        )
        post = Post.objects.get(id=self.post.pk)
        form_data_result = [
            (post.text, form_data['text']),
            (post.author, self.post.author),
            (post.group.pk, form_data['group'])
        ]
        for first_object, first_result in form_data_result:
            with self.subTest(first_object=first_object):
                self.assertEqual(first_object, first_result)

    def test_create_comments_post(self):
        """Проверка создания комментария авторизованным пользователем"""
        Comment.objects.all().delete()
        form_data = {
            'text': 'Тестовый комментарий',
            'post': self.post.id,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse(
                                 'posts:post_detail',
                                 kwargs={'post_id': self.post.pk})
                             )
        self.assertEqual(
            Comment.objects.all().count(),
            1
        )
        comment = Comment.objects.first()
        form_data_result = (
            (comment.text, form_data['text']),
            (comment.post.id, form_data['post']),
            (comment.author, self.user),
        )
        for first_object, first_result in form_data_result:
            with self.subTest(first_object=first_object):
                self.assertEqual(first_object, first_result)

    def test_no_create_comments_post(self):
        """
        Проверка неавторизованным пользователем не можем создать комментарий
        или изменить текущий
        """
        form_data = {
            'text': 'Тестовый текст комментария',
            'post': self.post.id,
        }
        comment_count = Comment.objects.count()
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(comment_count, Comment.objects.count())
        comment = get_object_or_404(Comment, post=self.post)
        form_data_result = (
            (comment.text, self.comment.text),
            (comment.author, self.user),
        )
        for first_object, first_result in form_data_result:
            with self.subTest(first_object=first_object):
                self.assertEqual(first_object, first_result)

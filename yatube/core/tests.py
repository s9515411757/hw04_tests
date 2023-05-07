from django.test import TestCase
from django.shortcuts import render


class ViewTestClass(TestCase):
    def test_page_not_found(self):
        """Проверка страница 404 отдаёт кастомный шаблон."""
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, 404)

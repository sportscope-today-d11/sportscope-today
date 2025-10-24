from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import News
import datetime
import json

class NewsModelTest(TestCase):
    def setUp(self):
        self.news = News.objects.create(
            title="Test News",
            link="https://example.com",
            author="Budi",
            source="Sportscope",
            publish_time=datetime.date(2024, 2, 16),
            content="This is a test news content.",
            thumbnail="images/thumbnails/thumbnail1.png",
            category="Transfer",
            featured=True,
        )

    def test_str_representation(self):
        self.assertEqual(str(self.news), "Test News")

    def test_thumbnail_url_default(self):
        """Kalau thumbnail = 'default', maka pakai static default image"""
        self.news.thumbnail = "default"
        self.assertIn("images/thumbnails/default.png", self.news.thumbnail_url)

    def test_thumbnail_url_http(self):
        """Kalau thumbnail pakai URL langsung"""
        self.news.thumbnail = "https://cdn.example.com/news.png"
        self.assertEqual(self.news.thumbnail_url, "https://cdn.example.com/news.png")


class NewsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )

        self.news = News.objects.create(
            title="News 1",
            link="https://example.com/1",
            author="Admin",
            source="Sportscope",
            publish_time=datetime.date.today(),
            content="Sample content",
            thumbnail="images/thumbnails/thumb.png",
            category="Match Result",
            featured=False,
        )

    def test_news_list_view(self):
        """Halaman list news bisa diakses"""
        response = self.client.get(reverse("main:news_list"))

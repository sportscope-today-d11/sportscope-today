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
        """__str__() harus menampilkan judul berita"""
        self.assertEqual(str(self.news), "Test News")

    def test_thumbnail_url_default(self):
        """Jika thumbnail='default', gunakan path static default"""
        self.news.thumbnail = "default"
        self.assertIn("images/thumbnails/default.png", self.news.thumbnail_url)

    def test_thumbnail_url_http(self):
        """Jika thumbnail berupa URL, gunakan langsung"""
        self.news.thumbnail = "https://cdn.example.com/news.png"
        self.assertEqual(self.news.thumbnail_url, "https://cdn.example.com/news.png")


class NewsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )
        self.user = User.objects.create_user(
            username="user", password="userpass", is_staff=False
        )

        self.news1 = News.objects.create(
            title="News 1",
            link="https://example.com/1",
            author="Admin",
            source="Sportscope",
            publish_time=datetime.date(2024, 1, 1),
            content="Content 1",
            thumbnail="images/thumbnails/thumb.png",
            category="Transfer",
        )

        self.news2 = News.objects.create(
            title="News 2",
            link="https://example.com/2",
            author="Admin",
            source="Sportscope",
            publish_time=datetime.date(2024, 1, 5),
            content="Content 2",
            thumbnail="images/thumbnails/thumb.png",
            category="Match Result",
        )

    # -----------------------------
    # LIST VIEW
    # -----------------------------
    def test_news_list_view_accessible(self):
        """Halaman news_list bisa diakses dan berisi berita"""
        response = self.client.get(reverse("main:news_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "News 1")
        self.assertContains(response, "News 2")

    def test_news_list_filter_by_category(self):
        """Filter kategori harus menampilkan hanya berita dengan kategori itu"""
        response = self.client.get(reverse("main:news_list") + "?category=Transfer")
        self.assertContains(response, "News 1")
        self.assertNotContains(response, "News 2")

    def test_news_list_sort_oldest(self):
        """Sort 'oldest' harus urut dari tanggal paling lama"""
        response = self.client.get(reverse("main:news_list") + "?sort=oldest")
        news_list = list(response.context["all_news"])
        self.assertEqual(news_list[0].title, "News 1")
        self.assertEqual(news_list[-1].title, "News 2")

    def test_news_list_sort_latest(self):
        """Sort 'latest' harus urut dari tanggal terbaru"""
        response = self.client.get(reverse("main:news_list") + "?sort=latest")
        news_list = list(response.context["all_news"])
        self.assertEqual(news_list[0].title, "News 2")

    def test_news_search(self):
        """Search query harus menampilkan berita yang cocok"""
        response = self.client.get(reverse("main:news_list") + "?q=News 1")
        self.assertContains(response, "News 1")
        self.assertNotContains(response, "News 2")

    # -----------------------------
    # BOOKMARK TESTS
    # -----------------------------
    def test_toggle_bookmark_requires_login(self):
        """User belum login tidak boleh toggle bookmark"""
        url = reverse("main:toggle_bookmark", args=[self.news1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_toggle_bookmark_add_and_remove(self):
        """User login bisa tambah dan hapus bookmark"""
        self.client.login(username="user", password="userpass")
        url = reverse("main:toggle_bookmark", args=[self.news1.id])

        # Tambah bookmark
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "added")

        # Hapus bookmark
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "removed")

    def test_bookmarked_news_view(self):
        """Bookmark page hanya tampilkan berita yang disimpan"""
        session = self.client.session
        session["bookmarks"] = [str(self.news1.id)]
        session.save()

        response = self.client.get(reverse("main:bookmarked_news"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "News 1")
        self.assertNotContains(response, "News 2")

    # -----------------------------
    # DETAIL VIEW
    # -----------------------------
    def test_news_detail_page(self):
        """Halaman detail berita bisa diakses"""
        url = reverse("main:news_detail", args=[self.news1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "News 1")
        self.assertContains(response, "Content 1")

    # -----------------------------
    # ADMIN CREATE / UPDATE / DELETE
    # -----------------------------
    def test_news_create_requires_admin(self):
        """Hanya admin yang bisa buka form create"""
        # Non-admin
        self.client.login(username="user", password="userpass")
        response = self.client.get(reverse("main:news_create"))
        self.assertEqual(response.status_code, 403)

        # Admin
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("main:news_create"))
        self.assertEqual(response.status_code, 200)

    def test_news_update_requires_admin(self):
        """Update hanya boleh admin"""
        self.client.login(username="user", password="userpass")
        response = self.client.get(reverse("main:news_update", args=[self.news1.id]))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("main:news_update", args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)

    def test_news_delete_requires_admin(self):
        """Delete hanya boleh admin"""
        self.client.login(username="user", password="userpass")
        response = self.client.get(reverse("main:news_delete", args=[self.news1.id]))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("main:news_delete", args=[self.news1.id]))
        self.assertEqual(response.status_code, 200)

    # -----------------------------
    # AJAX VIEW
    # -----------------------------
    def test_news_list_ajax_returns_html(self):
        """AJAX view (news_list_ajax) harus kembalikan HTML snippet"""
        response = self.client.get(
            reverse("main:news_list_ajax"), {"category": "Transfer"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("html", data)
        self.assertIn("News 1", data["html"])

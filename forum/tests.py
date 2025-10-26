from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from forum.models import Category, Thread, Comment


class ForumTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="12345")
        self.category = Category.objects.create(name="General Discussion")
        self.thread = Thread.objects.create(
            category=self.category,
            author_name="Tester",
            title="First Thread",
            content="This is a test thread."
        )
        self.comment = Comment.objects.create(
            thread=self.thread,
            author_name="Tester",
            content="This is a comment."
        )

    # -------- MODELS TESTS --------
    def test_category_str(self):
        self.assertEqual(str(self.category), "General Discussion")

    def test_thread_str(self):
        self.assertEqual(str(self.thread), "First Thread")

    def test_comment_str(self):
        expected_str = f"Comment by {self.comment.author_name} on {self.comment.thread}"
        self.assertEqual(str(self.comment), expected_str)

    # -------- VIEW TESTS --------
    def test_category_list_view(self):
        response = self.client.get(reverse('forum:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)

    def test_category_list_json(self):
        response = self.client.get(reverse('forum:category_list_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue("categories" in data)
        self.assertEqual(data["categories"][0]["name"], self.category.name)

    def test_thread_list_view(self):
        response = self.client.get(reverse('forum:thread_list', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread.title)

    def test_thread_detail_view_get(self):
        response = self.client.get(reverse('forum:thread_detail', args=[self.thread.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread.content)

    def test_thread_detail_view_post_comment(self):
        url = reverse('forum:thread_detail', args=[self.thread.slug])
        response = self.client.post(url, {'content': 'New comment'})
        self.assertEqual(response.status_code, 302)  # redirect after comment
        self.assertTrue(Comment.objects.filter(content='New comment').exists())

    def test_create_thread_view_get(self):
        response = self.client.get(reverse('forum:create_thread', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create")

    def test_create_thread_view_post(self):
        url = reverse('forum:create_thread', args=[self.category.slug])
        response = self.client.post(url, {
            'title': 'New Thread',
            'content': 'This is a new thread.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Thread.objects.filter(title='New Thread').exists())

    def test_all_threads_view(self):
        response = self.client.get(reverse('forum:all_threads'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread.title)

    def test_all_threads_filter_by_category(self):
        response = self.client.get(reverse('forum:all_threads') + f'?category={self.category.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread.title)

    def test_create_category_view_post(self):
        url = reverse('forum:create_category')
        response = self.client.post(url, {'name': 'Tech'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Tech').exists())

    def test_create_category_view_get(self):
        response = self.client.get(reverse('forum:create_category'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create")

    # -------- FORM TESTS --------
    def test_thread_form_valid(self):
        from forum.forms import ThreadForm
        form = ThreadForm(data={'title': 'Form Thread', 'content': 'Testing form.'})
        self.assertTrue(form.is_valid())

    def test_comment_form_valid(self):
        from forum.forms import CommentForm
        form = CommentForm(data={'content': 'Form comment.'})
        self.assertTrue(form.is_valid())

    def test_category_form_valid(self):
        from forum.forms import CategoryForm
        form = CategoryForm(data={'name': 'Form Category'})
        self.assertTrue(form.is_valid())

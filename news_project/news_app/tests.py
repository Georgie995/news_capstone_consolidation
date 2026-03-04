from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, CustomUser, Publisher


class SubscribedArticlesAPITests(APITestCase):
    """Automated tests for the subscribed articles API endpoint."""
    def setUp(self):
        """Create users, publishers, and articles used by the API tests."""
        # Create roles
        self.reader = CustomUser.objects.create_user(
            username="reader_test",
            password="password123",
            role=CustomUser.Roles.READER,
        )
        self.journalist = CustomUser.objects.create_user(
            username="journalist_test",
            password="password123",
            role=CustomUser.Roles.JOURNALIST,
        )
        self.other_journalist = CustomUser.objects.create_user(
            username="journalist_other",
            password="password123",
            role=CustomUser.Roles.JOURNALIST,
        )

        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.other_publisher = Publisher.objects.create(name="Other Publisher")

        # Reader subscriptions:
        # - subscribed to self.publisher
        # - subscribed to self.journalist
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        # Articles that SHOULD appear
        self.article_pub = Article.objects.create(
            title="Publisher article",
            content="Content 1",
            publisher=self.publisher,
            author=self.other_journalist,  # different journalist, but publisher matches
            is_approved=True,
            approved_at=timezone.now(),
        )
        self.article_journo = Article.objects.create(
            title="Journalist article",
            content="Content 2",
            publisher=self.other_publisher,  # different publisher, but journalist matches
            author=self.journalist,
            is_approved=True,
            approved_at=timezone.now(),
        )

        # Article that should NOT appear (unsubscribed publisher/journalist)
        self.article_other = Article.objects.create(
            title="Other article",
            content="Content 3",
            publisher=self.other_publisher,
            author=self.other_journalist,
            is_approved=True,
            approved_at=timezone.now(),
        )

        # Article that should NOT appear (unapproved, even if matches subscription)
        self.article_unapproved = Article.objects.create(
            title="Unapproved article",
            content="Content 4",
            publisher=self.publisher,
            author=self.journalist,
            is_approved=False,
        )

        self.url = reverse("api_articles")

    def test_requires_authentication(self):
        """
        Unauthenticated users must not get article data.
        """
        response = self.client.get(self.url)
        # Because of IsAuthenticated and session auth, we expect 403 or a redirect;
        # in the API test client it's usually 403.
        self.assertIn(response.status_code, (status.HTTP_302_FOUND, status.HTTP_403_FORBIDDEN))

    def test_reader_gets_only_subscribed_and_approved_articles(self):
        """
        Reader should receive:
          - articles for subscribed publisher
          - articles for subscribed journalist
        but NOT:
          - articles for other publisher/journalist
          - unapproved articles
        """
        self.client.login(username="reader_test", password="password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {item["title"] for item in response.data}

        # Should include
        self.assertIn(self.article_pub.title, titles)
        self.assertIn(self.article_journo.title, titles)

        # Should NOT include
        self.assertNotIn(self.article_other.title, titles)
        self.assertNotIn(self.article_unapproved.title, titles)

    def test_non_reader_gets_empty_list(self):
        """
        If a non-reader (e.g. journalist) hits the endpoint, they should not
        see reader-specific article lists.
        """
        self.client.login(username="journalist_test", password="password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data), [])

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from journal.models import Tag
from journal.tests.factories import TagFactory, UserFactory


class TagAPITests(APITestCase):
    def setUp(self):
        self.alice = UserFactory(username="alice")
        self.bob = UserFactory(username="bob")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.alice).key}"
        )

    def test_unauthenticated_user_cannot_list_tags(self):
        self.client.credentials()
        response = self.client.get("/api/tags/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listing_returns_only_my_tags(self):
        TagFactory(name="alice-tag", user=self.alice)
        TagFactory(name="bob-tag", user=self.bob)

        response = self.client.get("/api/tags/")
        names = [t["name"] for t in response.data]
        self.assertIn("alice-tag", names)
        self.assertNotIn("bob-tag", names)

    def test_creating_a_tag_assigns_current_user(self):
        response = self.client.post("/api/tags/", {"name": "new-tag"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tag = Tag.objects.get(pk=response.data["id"])
        self.assertEqual(tag.user, self.alice)

    def test_listing_excludes_archived_tags_by_default(self):
        TagFactory(name="active", user=self.alice)
        TagFactory(name="archived", user=self.alice, is_archived=True)

        response = self.client.get("/api/tags/")
        names = [t["name"] for t in response.data]
        self.assertIn("active", names)
        self.assertNotIn("archived", names)

    def test_delete_endpoint_archives_instead_of_destroying(self):
        tag = TagFactory(user=self.alice)

        response = self.client.delete(f"/api/tags/{tag.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        tag.refresh_from_db()
        self.assertTrue(tag.is_archived)

    def test_cannot_delete_another_users_tag(self):
        bob_tag = TagFactory(user=self.bob)

        response = self.client.delete(f"/api/tags/{bob_tag.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        bob_tag.refresh_from_db()
        self.assertFalse(bob_tag.is_archived)

    def test_restore_archived_tag(self):
        tag = TagFactory(user=self.alice, is_archived=True)

        response = self.client.post(f"/api/tags/{tag.pk}/restore/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertFalse(tag.is_archived)
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from journal.tests.factories import EntryFactory, TagFactory, UserFactory


class EntryAPITests(APITestCase):
    def setUp(self):
        self.alice = UserFactory(username="alice")
        self.bob = UserFactory(username="bob")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.alice).key}"
        )

    def test_creating_entry_with_tag_ids_attaches_tags(self):
        work = TagFactory(name="work", user=self.alice)
        home = TagFactory(name="home", user=self.alice)

        response = self.client.post(
            "/api/entries/",
            {"text": "Long day.", "mood": 3, "tag_ids": [work.pk, home.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Response includes nested tag objects, not just IDs
        self.assertEqual(len(response.data["tags"]), 2)
        returned_names = {t["name"] for t in response.data["tags"]}
        self.assertEqual(returned_names, {"work", "home"})

    def test_cannot_attach_another_users_tag(self):
        bob_tag = TagFactory(name="bob-tag", user=self.bob)

        response = self.client.post(
            "/api/entries/",
            {"text": "Trying to steal a tag", "mood": 3, "tag_ids": [bob_tag.pk]},
            format="json",
        )
        # Should fail validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entry_list_is_scoped_to_current_user(self):
        EntryFactory(user=self.alice, text="mine")
        EntryFactory(user=self.bob, text="not mine")

        response = self.client.get("/api/entries/")
        texts = [e["text"] for e in response.data]
        self.assertIn("mine", texts)
        self.assertNotIn("not mine", texts)

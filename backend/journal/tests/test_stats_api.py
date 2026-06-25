from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from journal.tests.factories import EntryFactory, TagFactory, UserFactory


class StatsAPITests(APITestCase):
    def setUp(self):
        self.alice = UserFactory()
        self.alice_token = Token.objects.create(user=self.alice)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.alice_token.key}")

    def test_stats_with_no_entries(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_entries"], 0)
        self.assertIsNone(response.data["average_mood"])

    def test_stats_basic_aggregates(self):
        EntryFactory(user=self.alice, text="a", mood=2)
        EntryFactory(user=self.alice, text="b", mood=4)

        response = self.client.get("/api/stats/")
        self.assertEqual(response.data["total_entries"], 2)
        self.assertEqual(response.data["average_mood"], 3.0)

    def test_mood_by_tag(self):
        work = TagFactory(name="work", user=self.alice)
        e1 = EntryFactory(user=self.alice, text="a", mood=2)
        e2 = EntryFactory(user=self.alice, text="b", mood=4)
        e1.tags.add(work)
        e2.tags.add(work)

        response = self.client.get("/api/stats/")
        mood_by_tag = response.data["mood_by_tag"]

        work_stats = next(row for row in mood_by_tag if row["tag"] == "work")
        self.assertEqual(work_stats["count"], 2)
        self.assertEqual(work_stats["average_mood"], 3.0)

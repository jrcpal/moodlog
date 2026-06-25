from rest_framework.test import APITestCase

from journal.models import Tag
from journal.tests.factories import TagFactory, UserFactory


class TagModelTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_creating_a_tag(self):
        tag = TagFactory(name="work", user=self.user)
        self.assertEqual(tag.name, "work")
        self.assertFalse(tag.is_archived)

    def test_tag_string_representation(self):
        tag = TagFactory(name="anxious", user=self.user)
        self.assertEqual(str(tag), "anxious")

    def test_tag_name_unique_per_user(self):
        TagFactory(name="work", user=self.user)
        with self.assertRaises(Exception):
            TagFactory(name="work", user=self.user)

    def test_different_users_can_have_same_tag_name(self):
        bob = UserFactory()
        TagFactory(name="work", user=self.user)
        TagFactory(name="work", user=bob)

    def test_archiving_does_not_delete_the_row(self):
        tag = TagFactory(name="work", user=self.user)
        tag.is_archived = True
        tag.save()
        self.assertTrue(Tag.objects.filter(pk=tag.pk).exists())

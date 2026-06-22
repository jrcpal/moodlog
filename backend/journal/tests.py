from django.contrib.auth.models import User
from django.test import TestCase

from journal.models import Tag


class TagModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_creating_a_tag(self):
        tag = Tag.objects.create(name="work", user=self.user)
        self.assertEqual(tag.name, "work")
        self.assertFalse(tag.is_archived)

    def test_tag_string_representation(self):
        tag = Tag.objects.create(name="anxious", user=self.user)
        self.assertEqual(str(tag), "anxious")

    def test_tag_name_unique_per_user(self):
        Tag.objects.create(name="work", user=self.user)
        with self.assertRaises(Exception):
            Tag.objects.create(name="work", user=self.user)

    def test_different_users_can_have_same_tag_name(self):
        bob = User.objects.create_user(username="bob", password="pw")
        Tag.objects.create(name="work", user=self.user)
        # Should not raise
        Tag.objects.create(name="work", user=bob)

    def test_archiving_does_not_delete_the_row(self):
        tag = Tag.objects.create(name="work", user=self.user)
        tag.is_archived = True
        tag.save()
        # The row still exists
        self.assertTrue(Tag.objects.filter(pk=tag.pk).exists())
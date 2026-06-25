import factory
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from journal.models import Entry, Tag


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # `Sequence` gives each created user a unique username
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "pw")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag-{n}")
    user = factory.SubFactory(UserFactory)


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entry

    text = factory.Faker("sentence")
    mood = 3
    user = factory.SubFactory(UserFactory)
from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_tag_per_user",
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Entry(models.Model):
    class Mood(models.IntegerChoices):
        TERRIBLE = 1, "Terrible"
        BAD = 2, "Bad"
        OKAY = 3, "Okay"
        GOOD = 4, "Good"
        GREAT = 5, "Great"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    text = models.TextField()
    mood = models.IntegerField(choices=Mood.choices)
    tags = models.ManyToManyField(Tag, related_name="entries", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} – {self.created_at:%Y-%m-%d} – mood {self.mood}"
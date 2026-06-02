from rest_framework import serializers
from .models import Tag, Entry

class TagSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Tag
        fields = ["id", "name", "is_archived", "created_at"]
        read_only_fields = ["id", "is_archived", "created_at"]

class EntrySerializer(serializers.ModelSerializer):
    # Nested tag objects on read
    tags = TagSerializer(many=True, read_only=True)
    # Plain list of tag IDs on write
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Tag.objects.all(),
        source="tags",
        required=False,
    )

    class Meta:
        model = Entry
        fields = [
            "id",
            "text",
            "mood",
            "tags",
            "tag_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Scope tag_ids queryset to the logged-in user
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["tag_ids"].child_relation.queryset = (
                Tag.objects.filter(user=request.user)
            )
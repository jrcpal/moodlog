from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tag, Entry
from .serializers import TagSerializer, EntrySerializer

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only filter tags belonging to the logged-in user
        qs = Tag.objects.filter(user=self.request.user)

        # By default, hide archived tags. Pass ?include_archived=true to see them
        include_archived = self.request.query_params.get("include_archived")
        if include_archived != "true":
            qs = qs.filter(is_archived=False)
        return qs

    def perform_create(self, serializer):
        #Automatically set user to whomever is logged in 
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete: archive instead of removing the row
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        # Restore explicitly looks at archived tags too
        tag = Tag.objects.filter(user=request.user, pk=pk).first()
        if not tag:
            return Response({"detail": "Not found."}, status=404)
        tag.is_archived = False
        tag.save(update_fields=["is_archived"])
        serializer = self.get_serializer(tag)
        return Response(serializer.data)

class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Entry.objects.filter(user=self.request.user).prefetch_related("tags")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
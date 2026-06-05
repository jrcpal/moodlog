from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tag, Entry
from .serializers import TagSerializer, EntrySerializer
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate

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

class StatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        entries = Entry.objects.filter(user=user)

        # Basic totals
        totals = entries.aggregate(
            total_entries=Count("id"),
            average_mood=Avg("mood"),
        )

        # Mood over time, grouped by day
        mood_over_time = (
            entries
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(average_mood=Avg("mood"), count=Count("id"))
            .order_by("date")
        )

        # Tag frequency
        tag_frequency = (
            Tag.objects
            .filter(user=user, is_archived=False)
            .annotate(count=Count("entries"))
            .filter(count__gt=0)
            .order_by("-count")
            .values("name", "count")
        )

        # Average mood per tag
        mood_by_tag = (
            Tag.objects
            .filter(user=user, is_archived=False)
            .annotate(
                average_mood=Avg("entries__mood"),
                count=Count("entries"),
            )
            .filter(count__gt=0)
            .order_by("-count")
            .values("name", "average_mood", "count")
        )

        return Response({
            "total_entries": totals["total_entries"],
            "average_mood": round(totals["average_mood"], 2) if totals["average_mood"] else None,
            "mood_over_time": [
                {
                    "date": row["date"].isoformat() if row["date"] else None,
                    "average_mood": round(row["average_mood"], 2),
                    "count": row["count"],
                }
                for row in mood_over_time
            ],
            "tag_frequency": [
                {"tag": row["name"], "count": row["count"]}
                for row in tag_frequency
            ],
            "mood_by_tag": [
                {
                    "tag": row["name"],
                    "average_mood": round(row["average_mood"], 2),
                    "count": row["count"],
                }
                for row in mood_by_tag
            ],
        })
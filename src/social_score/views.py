from typing import Any

from django.db.models import Q
from django.views.generic import TemplateView
from .models import SocialScore


class LeaderboardView(TemplateView):
    template_name = "social_leaderboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["scores"] = (
            SocialScore.objects.select_related("user")
            .filter(~Q(score=0))
            .order_by("-score")
        )
        return context

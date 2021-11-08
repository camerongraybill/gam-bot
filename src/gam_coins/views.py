from typing import Any

from django.views.generic import TemplateView
from .models import Account, Wager


class LeaderboardView(TemplateView):
    template_name = "coin_leaderboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["accounts"] = (
            Account.objects.select_related("user")
            .filter(user_id__in=Wager.objects.values_list("account_id", flat=True))
            .order_by("-coins")
        )
        return context

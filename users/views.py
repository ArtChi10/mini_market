# users/views.py
from decimal import Decimal

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.shortcuts import redirect
from django.views.generic import TemplateView

from catalog.models import Product


class PortfolioView(LoginRequiredMixin, TemplateView):
    template_name = "users/portfolio.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user

        # Позиции пользователя: подтягиваем товар одним запросом
        holdings = (
            u.holdings
             .select_related("product")
             .annotate(position_value=F("quantity") * F("product__price"))
        )
        total_positions = (
            holdings.aggregate(total=Sum("position_value"))["total"]
            or Decimal("0.00")
        )

        # Правая колонка: товары, созданные пользователем (новые сверху)
        my_products = (
            Product.objects
                   .filter(created_by=u, is_approved=True)
                   .select_related("category")
                   .order_by("-created_at", "-id")
        )

        ctx["holdings"] = holdings
        ctx["total_positions"] = total_positions
        ctx["portfolio_total"] = total_positions  # алиас, если шаблон ждёт это имя
        ctx["my_products"] = my_products
        return ctx


def logout_now(request):
    logout(request)
    return redirect("login")

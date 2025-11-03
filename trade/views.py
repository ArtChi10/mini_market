# trade/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView

from catalog.models import Product
from .forms import BuyForm  # добавь SellForm в forms.py по аналогии с BuyForm
from .models import Transaction
from .services import buy_product, sell_product


@login_required
def buy_view(request, product_id: int):
    """
    POST: покупка товара (qty из BuyForm), вся логика и транзакции — в services.buy_product.
    GET: редиректим на карточку товара.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = BuyForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data["quantity"]
            try:
                buy_product(request.user, product.id, qty)
            except ValidationError as e:
                messages.error(request, e.message)
            else:
                messages.success(request, f"Куплено: {product.title} × {qty}")
        else:
            messages.error(request, "Некорректное количество.")
        return redirect(product.get_absolute_url())

    # GET
    return redirect(product.get_absolute_url())


@login_required
def sell_view(request, product_id: int):
    """
    POST: продажа товара (qty из формы), бизнес-логика в services.sell_product.
    GET: редирект на карточку товара.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        # если уже есть SellForm — раскомментируй эту строку и импортируй SellForm из .forms
        # form = SellForm(request.POST)
        # if form.is_valid():
        #     qty = form.cleaned_data["quantity"]
        # else:
        #     messages.error(request, "Некорректное количество.")
        #     return redirect(product.get_absolute_url())

        # временно (если SellForm ещё не сделали) — используем BuyForm для валидации qty
        form = BuyForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data["quantity"]
            try:
                sell_product(request.user, product.id, qty)
            except ValidationError as e:
                messages.error(request, e.message)
            else:
                messages.success(request, f"Продано: {product.title} × {qty}")
        else:
            messages.error(request, "Некорректное количество.")

    return redirect(product.get_absolute_url())


class TransactionsView(LoginRequiredMixin, ListView):
    """
    История операций текущего пользователя.
    """
    template_name = "trade/transactions.html"
    model = Transaction
    paginate_by = 20

    def get_queryset(self):
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related("product")
            .order_by("-created_at")
        )


transactions_view = TransactionsView.as_view()

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError
from catalog.models import Product
from .forms import BuyForm
from .services import buy_product

@login_required
def buy_view(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    form = BuyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        qty = form.cleaned_data["quantity"]
        try:
            buy_product(request.user, product.id, qty)
        except ValidationError as e:
            messages.error(request, e.message)
        else:
            messages.success(request, f"Куплено: {product.title} × {qty}")
        return redirect(product.get_absolute_url())
    # если кто-то открыл GETом
    return redirect(product.get_absolute_url())

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError
from catalog.models import Product
from .forms import BuyForm
from .services import buy_product, sell_product

@login_required
def sell_view(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 0))
        try:
            sell_product(request.user, product.id, qty)
        except ValidationError as e:
            messages.error(request, e.message)
        else:
            messages.success(request, f"Продано: {product.title} × {qty} (комиссия 10%)")
    return redirect(product.get_absolute_url())


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Transaction

class TransactionsView(LoginRequiredMixin, ListView):
    template_name = "trade/transactions.html"
    model = Transaction
    paginate_by = 20

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related("product")

transactions_view = TransactionsView.as_view()

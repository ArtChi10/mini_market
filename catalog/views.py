from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView

from .forms import ProductStudentForm
from .models import Product, Category
from .services import run_price_tick


class CatalogListView(ListView):
    template_name = "catalog/list.html"
    model = Product
    paginate_by = 10

    def get_queryset(self):
        qs = Product.objects.select_related("category")

        # фильтры по категории и поиску
        cat = self.request.GET.get("category")
        q = self.request.GET.get("q")
        if cat:
            qs = qs.filter(category__slug=cat)
        if q:
            qs = qs.filter(title__icontains=q)

        # правила видимости:
        u = self.request.user
        if not u.is_authenticated:
            qs = qs.filter(is_approved=True)
        elif not u.is_staff:
            qs = qs.filter(Q(is_approved=True) | Q(created_by=u))
        # staff видит всё
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["curr_category"] = self.request.GET.get("category") or ""
        ctx["q"] = self.request.GET.get("q") or ""
        return ctx


class ProductDetailView(DetailView):
    template_name = "catalog/detail.html"
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"

    # не даём смотреть чужие не-одобренные карточки
    def get_queryset(self):
        qs = Product.objects.select_related("category")
        u = self.request.user
        if not u.is_authenticated:
            return qs.filter(is_approved=True)
        if u.is_staff:
            return qs
        return qs.filter(Q(is_approved=True) | Q(created_by=u))


@permission_required("catalog.can_tick_prices")
def price_tick_view(request):
    count = run_price_tick(now=timezone.now())
    messages.success(request, f"Цены обновлены у {count} товаров.")
    return redirect("catalog:list")


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = "catalog/product_form.html"
    form_class = ProductStudentForm
    success_url = reverse_lazy("catalog:my")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        # при желании можно авто-одобрять для staff/группы
        # if self.request.user.is_staff: obj.is_approved = True
        obj.save()
        messages.success(self.request, "Заявка на товар отправлена на проверку.")
        return super().form_valid(form)


class MyProductsView(LoginRequiredMixin, ListView):
    template_name = "catalog/my_products.html"
    model = Product
    paginate_by = 20

    def get_queryset(self):
        return (Product.objects
                .filter(created_by=self.request.user)
                .select_related("category")
                .order_by("-updated_at"))

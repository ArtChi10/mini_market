from django.urls import path
from .views import CatalogListView, ProductDetailView, ProductCreateView, MyProductsView, price_tick_view

app_name = "catalog"
urlpatterns = [
    path("", CatalogListView.as_view(), name="list"),
    path("new/", ProductCreateView.as_view(), name="create"),
    path("mine/", MyProductsView.as_view(), name="my"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="detail"),
    path("tick/", price_tick_view, name="tick"),  # если уже есть — оставь
]

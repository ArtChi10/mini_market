from django.urls import path
from .views import buy_view, sell_view
from .views import transactions_view


app_name = "trade"
urlpatterns = [
    path("buy/<int:product_id>/", buy_view, name="buy"),
    path("sell/<int:product_id>/", sell_view, name="sell"),
    path("history/", transactions_view, name="history"),
]

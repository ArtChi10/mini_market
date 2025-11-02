from django.urls import path
from .views import PortfolioView, logout_now

urlpatterns = [
    path("", PortfolioView.as_view(), name="portfolio"),
    path("logout-now/", logout_now, name="logout_now"),
]
# mini_market/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("users.urls")),
    path("catalog/", include(("catalog.urls", "catalog"), namespace="catalog")),
    path("trade/", include(("trade.urls", "trade"), namespace="trade")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


def default_next_change():
    # разрешим изменить цену через 2 дня от момента создания
    return timezone.now() + timedelta(days=2)


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:list") + f"?category={self.slug}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("10.00"))
    stock = models.PositiveIntegerField(default=100)

    # «тик цен»
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("10000.00"))
    next_change_at = models.DateTimeField(default=default_next_change)

    # контент от детей
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    qrcode = models.ImageField(upload_to="products/", blank=True, null=True)
    description = models.TextField(blank=True, default="")
    ascii_art = models.TextField(blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='products_created',
        help_text='Кто создал карточку товара'
    )
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pending_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="pending_products"
    )
    # кто правил последним (для прозрачности)
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product_edits"
    )
    last_edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        permissions = [
            ("can_tick_prices", "Can run price tick for products"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("catalog:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # надёжно генерируем уникальный slug
        if not self.slug:
            base = slugify(self.title)[:170] or "item"
            cand = base
            i = 2
            while Product.objects.filter(slug=cand).exclude(pk=self.pk).exists():
                cand = f"{base}-{i}"
                i += 1
            self.slug = cand
        super().save(*args, **kwargs)

    @property
    def image_src(self) -> str:
        """Безопасный URL картинки товара или плейсхолдер из media/products."""
        if self.image:  # НЕ трогаем .url, если файла нет
            return self.image.url
        return settings.MEDIA_URL + "products/product_placeholder.svg"


class PriceHistory(models.Model):
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="price_history")
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=32, default="tick")

    class Meta:
        ordering = ["-changed_at"]

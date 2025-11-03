from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Q

class Holding(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="holdings")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="holdings")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("user", "product")]

    def __str__(self):
        return f"{self.user} — {self.product} x {self.quantity}"


class Transaction(models.Model):


    BUY = "BUY"
    SELL = "SELL"
    SELL_REVENUE = "SELL_REVENUE"  # доход автору при покупке его товара

    TYPE_CHOICES = [
        (BUY, "Buy"),
        (SELL, "Sell"),
        (SELL_REVENUE, "Seller revenue"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=12, choices=TYPE_CHOICES)  # было 4 — увеличили до 12
    quantity = models.PositiveIntegerField()
    price_at_trade = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    # чтобы разовый backfill не создавал дубликаты доходов
    original_tx = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_by"
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["type", "original_tx"],
                name="uniq_seller_revenue_per_buy",
                # ВАЖНО: используем строку, а не имя константы
                condition=Q(type="SELL_REVENUE"),
            )
        ]

    def __str__(self):
        return f"{self.type} {self.product} x{self.quantity} @ {self.price_at_trade}"

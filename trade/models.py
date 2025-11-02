from decimal import Decimal
from django.conf import settings
from django.db import models

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
    TYPE_CHOICES = [(BUY, "Buy"), (SELL, "Sell")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price_at_trade = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} {self.product} x{self.quantity} @ {self.price_at_trade}"

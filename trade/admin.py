from django.contrib import admin
from .models import Holding, Transaction

@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity")
    list_filter = ("product", "user")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "product", "type", "quantity", "price_at_trade", "fee_amount")
    list_filter = ("type", "product", "user")
    date_hierarchy = "created_at"

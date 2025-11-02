import json
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from catalog.models import Category, Product

path = "seed_catalog.json"  # если файл в корне проекта

with open(path, "r", encoding="utf-8") as f:
    objs = json.load(f)

# сначала категории
for o in objs:
    if o["model"] == "catalog.category":
        fields = o["fields"]
        Category.objects.update_or_create(
            pk=o["pk"],
            defaults={"name": fields["name"], "slug": fields["slug"]},
        )

# потом товары
for o in objs:
    if o["model"] == "catalog.product":
        flds = o["fields"]
        cat = Category.objects.get(pk=flds["category"])
        Product.objects.update_or_create(
            pk=o["pk"],
            defaults={
                "title": flds["title"],
                "slug": flds["slug"],
                "category": cat,
                "price": Decimal(str(flds["price"])),
                "stock": int(flds["stock"]),
                # поля, которые loaddata не заполняет:
                "next_change_at": timezone.now() + timedelta(days=2),
                # min/max оставь по своим default в модели
            },
        )

print("Импорт завершён.")

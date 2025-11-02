from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from django.db.models import F
import random

from django.conf import settings
from .models import Product, PriceHistory

Q = Decimal

def clamp(val: Decimal, lo: Decimal, hi: Decimal) -> Decimal:
    return max(lo, min(hi, val))

@transaction.atomic
def run_price_tick(now=None) -> int:
    """
    Меняет цену у товаров, у кого наступил срок next_change_at.
    Случайно вверх/вниз на [PRICE_CHANGE_MIN..PRICE_CHANGE_MAX] %, с зажимом в пределах min_price..max_price.
    Возвращает количество обновлённых товаров.
    """
    now = now or timezone.now()
    qs = Product.objects.select_for_update().filter(next_change_at__lte=now)

    changed = 0
    for p in qs:
        direction = Q(random.choice([-1, 1]))                      # -1 или +1
        pct = Q(random.randint(settings.PRICE_CHANGE_MIN, settings.PRICE_CHANGE_MAX)) / Q(100)
        new_price = (p.price * (Q(1) + direction * pct)).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
        new_price = clamp(new_price, p.min_price, p.max_price)

        if new_price != p.price:
            PriceHistory.objects.create(
                product=p, old_price=p.price, new_price=new_price, reason="tick"
            )
            p.price = new_price
            changed += 1

        # следующее разрешённое изменение через 2 дня
        p.next_change_at = now + timezone.timedelta(days=2)
        p.save(update_fields=["price", "next_change_at"])
    return changed

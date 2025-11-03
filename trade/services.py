from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from catalog.models import Product
from .models import Holding, Transaction
from . import FEE_RATE  # комиссия платформы, например Decimal("0.10") = 10%
from decimal import Decimal
from django.db import transaction
from users.models import Profile


Q = Decimal  # сокращение


@transaction.atomic
def buy_product(user, product_id: int, qty: int) -> None:
    """
    Покупка товара:
    - проверяем баланс и склад
    - списываем деньги, уменьшаем stock, увеличиваем Holding
    - создаём Transaction(BUY)
    - если у товара есть author (created_by) и это не сам покупатель —
      начисляем автору доход (с учётом FEE_RATE) и создаём Transaction(SELL_REVENUE)
    """
    if qty < 1:
        raise ValidationError("Количество должно быть ≥ 1")

    # блокируем записи на время операции
    product = Product.objects.select_for_update().get(id=product_id)
    profile = Profile.objects.select_for_update().get(user=user)

    if qty > product.stock:
        raise ValidationError("Недостаточно товара на складе")

    price = Q(product.price)
    total_cost = (price * Q(qty)).quantize(Q("0.01"), rounding=ROUND_HALF_UP)

    if total_cost > profile.balance:
        raise ValidationError("Недостаточно монет для покупки")

    holding, _ = Holding.objects.select_for_update().get_or_create(
        user=user, product=product, defaults={"quantity": 0}
    )

    # 1) списываем баланс
    profile.balance = F("balance") - total_cost
    profile.save(update_fields=["balance"])

    # 2) уменьшаем склад
    product.stock = F("stock") - qty
    product.save(update_fields=["stock"])

    # 3) увеличиваем владение
    holding.quantity = F("quantity") + qty
    holding.save(update_fields=["quantity"])

    # 4) транзакция покупателя (BUY)
    buy_tx = Transaction.objects.create(
        user=user,
        product=product,
        type=Transaction.BUY,
        quantity=qty,
        price_at_trade=price,
        fee_amount=Q("0.00"),
    )

    # 5) начисление автору товара (если есть и не сам покупатель)
    seller = getattr(product, "created_by", None)
    if seller and seller.id != user.id:
        seller_profile = Profile.objects.select_for_update().get(user=seller)

        gross = total_cost
        fee = (gross * Q(str(FEE_RATE))).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
        seller_gain = gross - fee

        seller_profile.balance = F("balance") + seller_gain
        seller_profile.save(update_fields=["balance"])

        Transaction.objects.create(
            user=seller,
            product=product,
            type=Transaction.SELL_REVENUE,
            quantity=qty,
            price_at_trade=price,  # фиксируем цену сделки
            fee_amount=fee,        # комиссия платформы с продавца
            original_tx=buy_tx,    # связь с исходной покупкой
        )


@transaction.atomic
def sell_product(user, product_id: int, qty: int) -> None:
    """
    Продажа из портфеля пользователя:
    - проверяем владение
    - уменьшаем Holding, увеличиваем баланс (за вычетом комиссии FEE_RATE)
    - возвращаем товар на склад
    - создаём Transaction(SELL)
    """
    if qty < 1:
        raise ValidationError("Количество должно быть ≥ 1")

    product = Product.objects.select_for_update().get(id=product_id)
    profile = Profile.objects.select_for_update().get(user=user)
    holding = Holding.objects.select_for_update().get(user=user, product=product)

    if qty > holding.quantity:
        raise ValidationError("Нельзя продать больше, чем есть во владении")

    price = Q(product.price)
    gross = (price * Q(qty)).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
    fee = (gross * Q(str(FEE_RATE))).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
    net = gross - fee

    # 1) списываем количество владения
    holding.quantity = F("quantity") - qty
    holding.save(update_fields=["quantity"])

    # 2) пополняем баланс
    profile.balance = F("balance") + net
    profile.save(update_fields=["balance"])

    # 3) возвращаем товар на склад
    product.stock = F("stock") + qty
    product.save(update_fields=["stock"])

    # 4) транзакция продажи
    Transaction.objects.create(
        user=user,
        product=product,
        type=Transaction.SELL,
        quantity=qty,
        price_at_trade=price,
        fee_amount=fee,
    )

# trade/services.py


# можно менять комиссию тут (0.00 = без комиссии)
FEE_RATE = Decimal("0.00")


def backfill_seller_revenue(dry_run: bool = False, limit: int | None = None) -> tuple[int, int]:
    """
    Создаёт SELL_REVENUE для старых покупок (BUY), если их ещё нет,
    и пополняет баланс автора товара.
    Возвращает (created, skipped).

    dry_run=True — только посчитать без изменений.
    limit=N — обработать первые N покупок.
    """
    created, skipped = 0, 0

    qs = (
        Transaction.objects
        .select_related("product", "user")
        .filter(type=Transaction.BUY)
        .order_by("id")
    )
    if limit:
        qs = qs[:limit]

    with transaction.atomic():
        for t in qs:
            product = t.product
            seller = getattr(product, "created_by", None)

            # нет автора или покупатель = автор — пропускаем
            if not seller or seller.id == t.user_id:
                skipped += 1
                continue

            # уже есть доход по этой покупке?
            if Transaction.objects.filter(type=Transaction.SELL_REVENUE, original_tx=t).exists():
                skipped += 1
                continue

            gross = (t.price_at_trade * t.quantity).quantize(Decimal("0.01"))
            fee = (gross * FEE_RATE).quantize(Decimal("0.01"))
            gain = gross - fee

            if not dry_run:
                # создаём доход автора
                Transaction.objects.create(
                    user=seller,
                    product=product,
                    type=Transaction.SELL_REVENUE,
                    quantity=t.quantity,
                    price_at_trade=t.price_at_trade,
                    fee_amount=fee,
                    original_tx=t,
                )
                # пополняем баланс автора
                sp = Profile.objects.select_for_update().get(user=seller)
                sp.balance += gain
                sp.save(update_fields=["balance"])

            created += 1

    return created, skipped

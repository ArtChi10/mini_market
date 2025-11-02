from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from users.models import Profile
from catalog.models import Product
from .models import Holding, Transaction

Q = Decimal  # сокращение

@transaction.atomic
def buy_product(user, product_id: int, qty: int) -> None:
    if qty < 1:
        raise ValidationError("Количество должно быть ≥ 1")

    # блокируем записи на время операции
    product = Product.objects.select_for_update().get(id=product_id)
    profile = Profile.objects.select_for_update().get(user=user)

    total_cost = (product.price * Q(qty)).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
    if total_cost > profile.balance:
        raise ValidationError("Недостаточно монет для покупки")

    if qty > product.stock:
        raise ValidationError("Недостаточно товара на складе")

    holding, _ = Holding.objects.select_for_update().get_or_create(
        user=user, product=product, defaults={"quantity": 0}
    )

    # списываем баланс, уменьшаем склад, увеличиваем владение
    profile.balance = F("balance") - total_cost
    profile.save(update_fields=["balance"])

    product.stock = F("stock") - qty
    product.save(update_fields=["stock"])

    holding.quantity = F("quantity") + qty
    holding.save(update_fields=["quantity"])

    Transaction.objects.create(
        user=user,
        product=product,
        type=Transaction.BUY,
        quantity=qty,
        price_at_trade=product.price,
        fee_amount=Q("0.00"),
    )


from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from users.models import Profile
from catalog.models import Product
from .models import Holding, Transaction
from . import FEE_RATE

Q = Decimal

@transaction.atomic
def sell_product(user, product_id: int, qty: int) -> None:
    if qty < 1:
        raise ValidationError("Количество должно быть ≥ 1")

    product = Product.objects.select_for_update().get(id=product_id)
    profile = Profile.objects.select_for_update().get(user=user)
    holding = Holding.objects.select_for_update().get(user=user, product=product)

    if qty > holding.quantity:
        raise ValidationError("Нельзя продать больше, чем есть во владении")

    gross = (product.price * Q(qty)).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
    fee = (gross * Q(str(FEE_RATE))).quantize(Q("0.01"), rounding=ROUND_HALF_UP)
    net = gross - fee

    # списываем количество владения, пополняем баланс, возвращаем товар на склад
    holding.quantity = F("quantity") - qty
    holding.save(update_fields=["quantity"])

    profile.balance = F("balance") + net
    profile.save(update_fields=["balance"])

    product.stock = F("stock") + qty
    product.save(update_fields=["stock"])

    Transaction.objects.create(
        user=user,
        product=product,
        type=Transaction.SELL,
        quantity=qty,
        price_at_trade=product.price,
        fee_amount=fee,
    )

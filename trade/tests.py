from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Profile
from catalog.models import Category, Product
from trade.models import Holding, Transaction
from trade.services import buy_product, sell_product

class TradeTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.user = U.objects.create_user("u", password="x")
        cat = Category.objects.create(name="Игрушки", slug="toy")
        self.product = Product.objects.create(title="Юла", slug="yula", category=cat, price=Decimal("100.00"), stock=10)

    def test_buy_and_sell_with_fee(self):
        buy_product(self.user, self.product.id, 2)
        self.user.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(Profile.objects.get(user=self.user).balance, Decimal("800.00"))
        self.assertEqual(Holding.objects.get(user=self.user, product=self.product).quantity, 2)
        self.assertEqual(self.product.stock, 8)

        sell_product(self.user, self.product.id, 1)
        self.user.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(Profile.objects.get(user=self.user).balance, Decimal("890.00"))  # 800 + 100 - 10%
        self.assertEqual(Holding.objects.get(user=self.user, product=self.product).quantity, 1)
        self.assertEqual(self.product.stock, 9)
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 2)

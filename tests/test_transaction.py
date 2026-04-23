from unittest import TestCase

from pit38.domain.transactions.transaction import Transaction
from tests.utils import apple, usd, buy


class TestTransaction(TestCase):
    def test_year_property(self):
        t = buy(apple(1), usd(100), "2023-06-15 12:00")
        self.assertEqual(t.year, 2023)

    def test_mul_by_non_numeric(self):
        t = buy(apple(1), usd(100), "2023-01-01 12:00")
        with self.assertRaises(TypeError):
            t * "abc"

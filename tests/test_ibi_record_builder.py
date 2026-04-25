from unittest import TestCase

import pendulum

from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue
from pit38.domain.transactions import Action, AssetValue
from pit38.plugins.stock.ibi_capital.order_parser import ParsedOrder
from pit38.plugins.stock.ibi_capital.record_builder import build_records


def _order(**overrides) -> ParsedOrder:
    defaults = {
        "order_number": "9000001",
        "company": "acme.com",
        "plan": "Acme 2022 RSU",
        "grant_date": pendulum.datetime(2023, 1, 10),
        "execution_date": pendulum.datetime(2025, 2, 20),
        "shares": 20,
        "sale_price": 100.0,
        "total_amount": 2000.0,
        "total_fees": 6.0,
        "price_for_tax": 0.0,
    }
    defaults.update(overrides)
    return ParsedOrder(**defaults)


class TestBuildRecords(TestCase):
    def test_emits_buy_sell_and_fee(self):
        transactions, fees = build_records(_order(), ticker="ACME")

        self.assertEqual(len(transactions), 2)
        self.assertEqual(len(fees), 1)
        actions = [t.action for t in transactions]
        self.assertIn(Action.BUY, actions)
        self.assertIn(Action.SELL, actions)

    def test_buy_uses_grant_date_and_price_for_tax(self):
        transactions, _ = build_records(
            _order(shares=10, price_for_tax=50.0),
            ticker="ACME",
        )
        buy = next(t for t in transactions if t.action == Action.BUY)

        self.assertEqual(buy.date, pendulum.datetime(2023, 1, 10, 9, 0, 0))
        self.assertEqual(buy.asset, AssetValue(10.0, "ACME"))
        self.assertEqual(buy.fiat_value, FiatValue(500.0, Currency.DOLLAR))

    def test_sell_uses_execution_date_and_total_amount(self):
        transactions, _ = build_records(_order(), ticker="ACME")
        sell = next(t for t in transactions if t.action == Action.SELL)

        self.assertEqual(sell.date, pendulum.datetime(2025, 2, 20, 10, 0, 0))
        self.assertEqual(sell.asset, AssetValue(20.0, "ACME"))
        self.assertEqual(sell.fiat_value, FiatValue(2000.0, Currency.DOLLAR))

    def test_rsu_zero_cost_basis_still_emits_buy(self):
        # price_for_tax = 0 for RSU; we still emit a zero-cost BUY so that
        # the FIFO calculator has something to match the SELL against.
        transactions, _ = build_records(_order(price_for_tax=0.0), ticker="ACME")

        buy = next(t for t in transactions if t.action == Action.BUY)
        self.assertEqual(buy.asset.amount, 20.0)
        self.assertEqual(buy.fiat_value, FiatValue(0.0, Currency.DOLLAR))

    def test_zero_fees_skipped(self):
        _, fees = build_records(_order(total_fees=0.0), ticker="ACME")
        self.assertEqual(fees, [])

    def test_fee_dated_at_execution_time(self):
        _, fees = build_records(_order(total_fees=6.0), ticker="ACME")
        self.assertEqual(fees[0].date, pendulum.datetime(2025, 2, 20, 10, 0, 0))
        self.assertEqual(fees[0].value, FiatValue(6.0, Currency.DOLLAR))

    def test_fifo_order_preserved_when_grant_and_execution_same_day(self):
        # Defensive: when an order is executed on the grant day itself
        # (e.g. same-day sale of newly-vested shares), BUY's 09:00 and
        # SELL's 10:00 keep FIFO deterministic.
        transactions, _ = build_records(
            _order(
                grant_date=pendulum.datetime(2025, 2, 20),
                execution_date=pendulum.datetime(2025, 2, 20),
            ),
            ticker="ACME",
        )
        buy = next(t for t in transactions if t.action == Action.BUY)
        sell = next(t for t in transactions if t.action == Action.SELL)

        self.assertLess(buy.date, sell.date)

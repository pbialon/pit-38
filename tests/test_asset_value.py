from unittest import TestCase

from pit38.domain.transactions.asset import AssetValue


class TestAssetValue(TestCase):
    def test_mul_by_non_numeric(self):
        asset = AssetValue(10, "AAPL")
        with self.assertRaises(TypeError):
            asset * "abc"

    def test_sub_different_assets(self):
        a = AssetValue(10, "AAPL")
        b = AssetValue(5, "GOOGL")
        with self.assertRaises(ValueError):
            a - b

    def test_sub_non_asset(self):
        asset = AssetValue(10, "AAPL")
        with self.assertRaises(TypeError):
            asset - 5

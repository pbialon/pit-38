from unittest import TestCase

from pit38.plugins.stock.ibi_capital.company_ticker import (
    UnknownCompanyError,
    _load_mapping,
    resolve_ticker,
)


class TestResolveTicker(TestCase):
    def test_packaged_json_resolves_monday_com(self):
        # Smoke test that the shipped seed actually loads and contains
        # the reference case we verified against real IBI PDFs.
        self.assertEqual(resolve_ticker("monday.com"), "MNDY")

    def test_case_insensitive_lookup(self):
        self.assertEqual(
            resolve_ticker("MONDAY.COM", mapping={"monday.com": "MNDY"}),
            "MNDY",
        )
        self.assertEqual(
            resolve_ticker("Monday.Com", mapping={"monday.com": "MNDY"}),
            "MNDY",
        )

    def test_surrounding_whitespace_trimmed(self):
        self.assertEqual(
            resolve_ticker("  monday.com  ", mapping={"monday.com": "MNDY"}),
            "MNDY",
        )

    def test_override_wins_over_mapping(self):
        self.assertEqual(
            resolve_ticker("monday.com", override="XXX", mapping={"monday.com": "MNDY"}),
            "XXX",
        )

    def test_override_wins_even_for_unknown_company(self):
        # User escape hatch: company not in seed, pass --ticker and move on.
        self.assertEqual(
            resolve_ticker("unknown llc", override="UNK", mapping={}),
            "UNK",
        )

    def test_unknown_company_raises_with_helpful_message(self):
        with self.assertRaises(UnknownCompanyError) as ctx:
            resolve_ticker("unknown llc", mapping={"monday.com": "MNDY"})
        msg = str(ctx.exception)
        self.assertIn("unknown llc", msg)
        self.assertIn("--ticker", msg)
        self.assertIn("companies.json", msg)

    def test_load_mapping_normalises_keys(self):
        _load_mapping.cache_clear()
        mapping = _load_mapping()
        # All keys must already be lowercase so resolve_ticker's lookup
        # stays hot-path simple.
        for key in mapping:
            self.assertEqual(key, key.lower())

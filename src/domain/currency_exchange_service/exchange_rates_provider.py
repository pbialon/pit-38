import json
from collections import defaultdict
from typing import Dict
from loguru import logger

import pendulum
import requests as requests

from domain.calendar_service.calendar import year_start, year_end
from domain.currency_exchange_service.currencies import Currency


class ExchangeRatesProvider:
    # todo: rates a, b, or c?
    # todo: query for each year
    NBP_API_URL = "https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}/?format=json"

    def __init__(self, start_year: int, end_year: int):
        self.start_year = start_year
        self.end_year = end_year
        self._rates = defaultdict(dict)

    def get_rate(self, currency: Currency, day: pendulum.Date) -> float:
        if currency not in self._rates or day not in self._rates[currency]:
            self._rates[currency].update(self._fetch_rates(currency, day.year))

        if day not in self._rates[currency]:
            raise ValueError("No rate for {} on {}".format(currency, day))

        return self._rates[currency][day]

    def _fetch_rates(self, currency: str, year: int) -> Dict[pendulum.Date, float]:

        api_url = self._prepare_url(currency, year_start(year), year_end(year))
        logger.debug("Querying NBP API: {}", api_url)
        payload = self._fetch_payload(api_url)
        return self._parse(payload)

    def _prepare_url(self, currency: str, start_date: pendulum.Date, end_date: pendulum.Date) -> str:
        return self.NBP_API_URL.format(currency=currency, start_date=start_date, end_date=end_date)

    def _fetch_payload(self, api_url: str) -> Dict[str, any]:
        response = requests.get(api_url)
        response.raise_for_status()
        return json.loads(response.text)

    def _parse(self, payload: Dict[str, any]) -> Dict[pendulum.Date, float]:
        rates = {
            pendulum.parse(rate["effectiveDate"]).date(): rate["mid"]
            for rate in payload["rates"]
        }
        logger.debug(f"Fetched rates for {len(rates)} days", )
        return rates

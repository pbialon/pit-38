import json
from typing import Dict

import pendulum
import requests as requests


class ExchangeRatesProvider:
    # todo: rates a, b, or c?
    NBP_API_URL = "https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}/?format=json"

    def __init__(self, start_date: pendulum.Date, end_date: pendulum.Date):
        self.start_date = start_date
        self.end_date = end_date
        self._rates = {}

    def get_rate(self, currency: str, day: pendulum.Date) -> float:
        if currency not in self._rates:
            self._rates[currency] = self._fetch_rates(currency)

        if day not in self._rates[currency]:
            raise ValueError("No rate for {} on {}".format(currency, day))

        return self._rates[currency][day]

    def _fetch_rates(self, currency: str) -> Dict[pendulum.Date, float]:
        api_url = self._prepare_url(currency, self.start_date.to_date_string(), self.end_date.to_date_string())
        payload = self._fetch_payload(api_url)
        return self._parse(payload)

    def _prepare_url(self, currency: str, start_date: pendulum.Date, end_date: pendulum.Date) -> str:
        return self.NBP_API_URL.format(currency=currency, start_date=start_date, end_date=end_date)

    def _fetch_payload(self, api_url: str) -> Dict[str, any]:
        response = requests.get(api_url)
        response.raise_for_status()
        return json.loads(response.text)

    def _parse(self, payload: Dict[str, any]) -> Dict[pendulum.Date, float]:
        return {
            pendulum.parse(rate["effectiveDate"]).date(): rate["mid"]
            for rate in payload["rates"]
        }

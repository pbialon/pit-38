import json
from typing import Dict

import pendulum
import requests as requests


class ExchangeRatesProvider:
    # todo: rates a, b, or c?
    NBP_API_URL = "https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}/?format=json"

    def _prepare_url(self, currency, start_date, end_date):
        return self.NBP_API_URL.format(currency=currency, start_date=start_date, end_date=end_date)

    def __init__(self, start_date: pendulum.Date, end_date: pendulum.Date):
        self.start_date = start_date
        self.end_date = end_date
        self._rates = {}

    def get_rate(self, currency, day) -> float:
        if currency not in self._rates:
            self._rates[currency] = self._fetch_rates(currency)

        return self._rates[currency][day]

    def _fetch_rates(self, currency) -> Dict[pendulum.Date, float]:
        api_url = self._prepare_url(currency, self.start_date.to_date_string(), self.end_date.to_date_string())
        response = requests.get(api_url)
        response.raise_for_status()
        payload = json.loads(response.text)
        return {
            # todo: mid with 4 digits after comma or 2?
            pendulum.parse(rate["effectiveDate"]).date(): rate["mid"]
            for rate in payload["rates"]
        }

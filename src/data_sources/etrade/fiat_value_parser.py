from domain.currency_exchange_service.currencies import Currency, FiatValue


class FiatValueParser:
    SYMBOL_TO_CURRENCY = {
        "$": Currency.DOLLAR,
        "€": Currency.EURO,
    }

    @classmethod
    def _resolve_currency(cls, raw_currency: str) -> Currency:
        currency_symbol = raw_currency[0]
        return cls.SYMBOL_TO_CURRENCY.get(currency_symbol)

    @classmethod
    def _clean_up_raw_number(cls, raw_fiat_value: str) -> str:
        without_currency_symbol = raw_fiat_value[1:]
        without_spaces = without_currency_symbol.replace(" ", "")
        corrected_commas = without_spaces.replace(",", ".")

        return corrected_commas

    @classmethod
    def parse(cls, raw_fiat_value: str) -> FiatValue:
        currency = cls._resolve_currency(raw_fiat_value)
        cleaned_raw_number = cls._clean_up_raw_number(raw_fiat_value)

        return FiatValue(amount=float(cleaned_raw_number), currency=currency)

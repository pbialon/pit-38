class TaxYearResult:
    def __init__(self,
                 tax_year: int,
                 income: int,
                 cost: int,
                 deductible_loss: int,
                 base_for_tax: int,
                 tax: float):
        self.tax_year = tax_year
        self.income = income
        self.cost = cost
        self.deductible_loss = deductible_loss
        self.base_for_tax = base_for_tax
        self.tax = tax

    def __str__(self):
        return f"[Tax year {self.tax_year}]: \n" \
               f"income: +{self.income} ZŁ, outcome: -{self.cost}\n" \
               f"deductible loss: {self.deductible_loss} ZŁ\n" \
               f"base for tax: {self.base_for_tax} ZŁ\n" \
               f"tax: {self.tax} ZŁ"

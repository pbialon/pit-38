class TaxYearResult:
    def __init__(self,
                 tax_year: int,
                 income: int,
                 cost: int,
                 deductable_loss: int,
                 base_for_tax: int,
                 tax: float):
        self.tax_year = tax_year
        self.income = income
        self.cost = cost
        self.deductable_loss = deductable_loss
        self.base_for_tax = base_for_tax
        self.tax = tax

    def __str__(self):
        return f"[Tax year {self.tax_year}]: \n" \
               f"income: +{self.income} ZŁ, outcome: -{self.cost}\n" \
               f"deductable loss: {self.deductable_loss} ZŁ\n" \
               f"base for tax: {self.base_for_tax} ZŁ\n" \
               f"tax: {self.tax} ZŁ"

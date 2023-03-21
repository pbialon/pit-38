
class AssetValue:
    def __init__(self, amount: float, asset_name: str):
        self.amount = amount
        self.asset_name = asset_name

    def __str__(self):
        return f"{self.amount} {self.asset_name}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            new_amount = self.amount * other
            return AssetValue(new_amount, self.asset_name)
        raise Exception("Cannot multiply by non-numeric value")

    def __sub__(self, other):
        if isinstance(other, AssetValue):
            if other.asset_name != self.asset_name:
                raise Exception("Cannot subtract different assets")
            new_amount = self.amount - other.amount
            return AssetValue(new_amount, self.asset_name)
        raise Exception("Cannot subtract non-asset value")
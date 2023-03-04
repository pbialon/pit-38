import json


def save(transactions, filename):
    with open(filename, "w") as f:
        json.dump({"items": transactions}, f)


def merge_stock_transactions_files(files):
    stock_transactions = []
    for filename in files:
        with open(filename, "r") as f:
            data = json.load(f)
        stock_transactions.extend(data["items"])
    return stock_transactions


def merge_crypto_transactions_files(files):
    crypto_transactions = []
    for filename in files:
        with open(filename, "r") as f:
            data = json.load(f)
        crypto_transactions.extend(data)
    return crypto_transactions


def merge_stock_transactions():
    files = ["resources/raw/stock/transactions{}.json".format(i) for i in range(1, 7)]
    stock_transactions = merge_stock_transactions_files(files)
    save(stock_transactions, "stock_transactions.json")


def merge_crypto_transactions():
    files = ["resources/raw/crypto/{}.json".format(crypto) for crypto in
             ["ada", "bch", "btc", "doge", "eth", "ltc", "xlm"]]
    crypto_transactions = merge_crypto_transactions_files(files)
    save(crypto_transactions, "resources/crypto_transactions.json")


if __name__ == "__main__":
    merge_stock_transactions()
    merge_crypto_transactions()

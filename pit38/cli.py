import click

from pit38.stock import stocks
from pit38.crypto import crypto


@click.group()
def main():
    """PIT-38 — Polish investment tax calculator for stocks and cryptocurrency."""
    pass


main.add_command(stocks, name="stock")
main.add_command(crypto, name="crypto")


if __name__ == "__main__":
    main()

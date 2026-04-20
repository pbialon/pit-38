from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pit38.domain.tax_service.tax_year_result import TaxYearResult

console = Console()


def _fmt(amount: float) -> str:
    return f"{amount:,.2f} PLN".replace(",", " ")


def _colored_amount(amount: float, positive_color="green", negative_color="red") -> str:
    formatted = _fmt(abs(amount))
    if amount > 0:
        return f"[{positive_color}]+ {formatted}[/]"
    if amount < 0:
        return f"[{negative_color}]- {formatted}[/]"
    return f"  {formatted}"


def _tax_base_styled(amount: float) -> str:
    formatted = _fmt(abs(amount))
    if amount < 0:
        return f"[bold red]- {formatted}[/]"
    return f"[bold]  {formatted}[/]"


def _tax_styled(amount: float) -> str:
    formatted = _fmt(amount)
    if amount == 0:
        return f"[bold green]  {formatted}[/]"
    return f"[bold red]  {formatted}[/]"


def _build_tax_table(title: str, result: TaxYearResult) -> Table:
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        title=f"[bold]{title}[/]",
        title_style="",
        title_justify="left",
    )
    table.add_column(min_width=22)
    table.add_column(justify="right", min_width=18)

    table.add_row("Income (przychód)", _colored_amount(result.income.amount))
    table.add_row("Cost (koszty)", _colored_amount(-result.cost.amount))
    if result.deductible_loss.amount > 0:
        table.add_row(
            "Deductible loss",
            f"[yellow]- {_fmt(result.deductible_loss.amount)}[/]",
        )
    table.add_row("", "")
    table.add_row("Tax base", _tax_base_styled(result.base_for_tax.amount))
    table.add_row("Tax (19%)", _tax_styled(result.tax.amount))

    return table


def print_stock_result(
    transactions_result: TaxYearResult,
    dividends_result: TaxYearResult,
    num_transactions: int,
    num_files: int,
):
    console.print()
    console.print(
        Panel(
            f"[bold]PIT-38 Stock Tax Summary — {transactions_result.tax_year}[/]",
            style="cyan",
            expand=False,
        )
    )
    console.print()

    console.print(_build_tax_table("Transactions", transactions_result))
    console.print()

    console.print(_build_tax_table("Dividends", dividends_result))
    console.print(
        "  [dim italic]If you paid 30% withholding tax in the US (no W-8BEN),[/]",
    )
    console.print(
        "  [dim italic]no additional Polish tax is due on dividends.[/]",
    )
    console.print()

    console.print(
        f"  [dim]Processed {num_transactions} transactions from {num_files} file(s).[/]"
    )
    console.print()


def print_crypto_result(
    result: TaxYearResult,
    num_transactions: int,
    num_files: int,
):
    console.print()
    console.print(
        Panel(
            f"[bold]PIT-38 Crypto Tax Summary — {result.tax_year}[/]",
            style="cyan",
            expand=False,
        )
    )
    console.print()

    console.print(_build_tax_table("Crypto", result))
    console.print()

    console.print(
        f"  [dim]Processed {num_transactions} transactions from {num_files} file(s).[/]"
    )
    console.print()

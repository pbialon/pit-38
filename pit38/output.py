from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pit38.domain.tax_service.tax_year_result import TaxYearResult

console = Console()

SEP_THIN = "───────────────"
SEP_BOLD = "═══════════════"


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


def _build_section(title: str, result: TaxYearResult, note: str = None) -> Panel:
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=True,
    )
    table.add_column(min_width=22)
    table.add_column(justify="right", min_width=17)

    income = result.income.amount
    cost = result.cost.amount
    profit = income - cost

    table.add_row("Income (przychód)", _colored_amount(income))
    table.add_row("Cost (koszty)", _colored_amount(-cost))
    table.add_row("", f"[dim]{SEP_THIN}[/]")
    table.add_row("Profit", _colored_amount(profit))

    if result.deductible_loss.amount > 0:
        table.add_row(
            "Deductible loss",
            f"[yellow]- {_fmt(result.deductible_loss.amount)}[/]",
        )

    table.add_row("", f"[dim]{SEP_BOLD}[/]")
    table.add_row("Tax base", _tax_base_styled(result.base_for_tax.amount))
    table.add_row("Tax (19%)", _tax_styled(result.tax.amount))

    if note:
        table.add_row("", "")
        table.add_row(f"[dim italic]{note}[/]", "")

    return Panel(table, title=f"[bold]{title}[/]", title_align="left", border_style="dim", expand=False, width=52)


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
    console.print(_build_section("Transactions", transactions_result))

    console.print()
    console.print(_build_section("Dividends", dividends_result))
    console.print(
        "  [dim italic]ℹ W-8BEN: 15% US withheld → 4% PL tax due[/]"
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
    console.print(_build_section("Crypto", result))

    console.print()
    console.print(
        f"  [dim]Processed {num_transactions} transactions from {num_files} file(s).[/]"
    )
    console.print()

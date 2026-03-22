from trakt_tools.core.authentication import list_accounts
from trakt_tools.core.console import console

import click


@click.command('account:list')
def account_list():
    """List all saved Trakt accounts."""
    active, accounts = list_accounts()

    if not accounts:
        console.print('[yellow]No accounts saved. Run any command to set up your first account.[/yellow]')
        return

    console.print('[bold]Accounts[/bold]')
    for name in accounts:
        if name == active:
            console.print('  [green]✓[/green] [bold]%s[/bold] [dim](active)[/dim]' % name)
        else:
            console.print('  · %s' % name)

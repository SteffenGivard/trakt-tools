from trakt_tools.core.authentication import switch_account, list_accounts
from trakt_tools.core.console import console

import click


@click.command('account:switch')
@click.argument('name')
def account_switch(name):
    """Switch the active Trakt account."""
    if not switch_account(name):
        exit(1)

    console.print('Switched to [bold]%s[/bold].' % name)

    _, accounts = list_accounts()
    for account_name in accounts:
        if account_name == name:
            console.print('  [green]✓[/green] [bold]%s[/bold] [dim](active)[/dim]' % account_name)
        else:
            console.print('  · %s' % account_name)

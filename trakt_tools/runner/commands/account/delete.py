from trakt_tools.core.authentication import delete_account, list_accounts, _active_name, _load_config
from trakt_tools.core.console import console

import click


@click.command('account:delete')
@click.argument('name')
def account_delete(name):
    """Delete a saved Trakt account."""
    config = _load_config()
    was_active = _active_name(config) == name

    if not delete_account(name):
        exit(1)

    console.print('[red]Account [bold]%s[/bold] deleted.[/red]' % name)

    active, accounts = list_accounts()
    if was_active and active:
        console.print('Switched to [bold]%s[/bold].' % active)

    if accounts:
        for account_name in accounts:
            if account_name == active:
                console.print('  [green]✓[/green] [bold]%s[/bold] [dim](active)[/dim]' % account_name)
            else:
                console.print('  · %s' % account_name)
    else:
        console.print('[yellow]No accounts remaining.[/yellow]')

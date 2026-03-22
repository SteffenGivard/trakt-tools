from trakt_tools.core.authentication import add_account
from trakt_tools.core.console import console

import click


@click.command('account:add')
@click.argument('name', required=False, default=None)
def account_add(name):
    """Add a new Trakt account.

    NAME is an optional label for the account (e.g. 'personal', 'test').
    If omitted, the Trakt username is used automatically.
    """
    if not add_account(name):
        exit(1)

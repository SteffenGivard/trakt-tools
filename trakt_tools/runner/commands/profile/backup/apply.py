from trakt_tools.core.authentication import authenticate
from trakt_tools.core.console import console
from trakt_tools.tasks import CreateApplyTask

import click
import os


@click.command('profile:backup:apply', short_help="Apply backup to a Trakt.tv profile")
@click.argument('backup_zip', type=click.Path(exists=True))
@click.option(
    '--account',
    default=None,
    help='Account name to apply the backup to. (default: active account)'
)
@click.option(
    '--token',
    default=os.environ.get('TRAKT_TOKEN') or None,
    help='Trakt.tv authentication token. (default: "TRAKT_TOKEN" env var, or saved config)'
)
def profile_backup_apply(backup_zip, account, token):
    """Apply backup to a Trakt.tv profile.

    Restores collection, history, ratings, and watchlist from a backup zip.
    Playback progress cannot be restored (no Trakt API endpoint exists for this).

    Note: history already on your profile will be duplicated after applying; run
    `history:duplicates:merge` afterwards to clean up any duplicates.

    BACKUP_ZIP is the location of the zip file created by the profile:backup:create command
    """

    if not token:
        success, token = authenticate(account)

        if not success:
            console.print('[red]Authentication failed[/red]')
            exit(1)


    # Run task
    success = CreateApplyTask(backup_zip).run(token=token)

    if not success:
        exit(1)

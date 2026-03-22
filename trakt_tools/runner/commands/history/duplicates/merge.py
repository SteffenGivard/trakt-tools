
from trakt_tools.core.authentication import authenticate
from trakt_tools.core.console import console
from trakt_tools.core.duration import parse_duration
from trakt_tools.tasks import MergeHistoryDuplicatesTask

import click
import os


@click.command('history:duplicates:merge')
@click.option(
    '-y', '--yes', 'assume_yes',
    is_flag=True,
    help='Automatic yes to confirmation prompts.'
)
@click.option(
    '--account',
    default=None,
    help='Account name to use. (default: active account)'
)
@click.option(
    '--token',
    default=os.environ.get('TRAKT_TOKEN') or None,
    help='Trakt.tv authentication token. (default: "TRAKT_TOKEN" env var, or saved config)'
)
@click.option(
    '--backup-dir',
    default=None,
    help='Directory that backups should be stored in. (default: "./backups")'
)
@click.option(
    '--delta-max',
    default='10m',
    help='Maximum delta between history records to consider as duplicate. (default: 10m)'
)
@click.option(
    '--per-page',
    default=1000,
    help='Request page size. (default: 1000)'
)
@click.option(
    '--backup/--no-backup',
    default=None,
    help='Backup profile before applying any changes. (default: prompt)'
)
@click.option(
    '--review/--no-review',
    default=None,
    help='Review each action before applying them. (default: prompt)'
)
@click.pass_context
def history_duplicates_merge(ctx, assume_yes, account, token, backup_dir, delta_max, per_page, backup, review):
    """Merge duplicate history records"""

    if not token:
        success, token = authenticate(account)

        if not success:
            console.print('[red]Authentication failed[/red]')
            exit(1)

    delta_max_seconds = parse_duration(delta_max)
    if delta_max_seconds is None:
        console.print('[red]Invalid --delta-max value %r. Use a duration like 30s, 10m, 2h, 1d.[/red]' % delta_max)
        exit(1)

    # Set default backup directory
    if not backup_dir:
        backup_dir = os.path.join(os.curdir, 'backups')

    # Ensure backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Run task
    success = MergeHistoryDuplicatesTask(
        backup_dir=backup_dir,
        delta_max=delta_max_seconds,
        per_page=per_page,

        assume_yes=assume_yes,
        debug=ctx.parent.debug,
        rate_limit=ctx.parent.rate_limit
    ).run(
        token=token,
        backup=backup,
        review=review
    )

    if not success:
        exit(1)

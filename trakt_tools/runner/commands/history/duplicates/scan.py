
from trakt_tools.core.authentication import authenticate
from trakt_tools.core.console import console
from trakt_tools.core.duration import parse_duration
from trakt_tools.tasks import ScanHistoryDuplicatesTask

import click
import os


@click.command('history:duplicates:scan')
@click.option(
    '-y', '--yes', 'assume_yes',
    is_flag=True,
    help='Automatic yes to confirmation prompts.'
)
@click.option(
    '--token',
    default=os.environ.get('TRAKT_TOKEN') or None,
    help='Trakt.tv authentication token. (default: "TRAKT_TOKEN" or Prompt)'
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
@click.pass_context
def history_duplicates_scan(ctx, assume_yes, token, delta_max, per_page):
    """Scan for duplicate history records"""

    if not token:
        success, token = authenticate()

        if not success:
            console.print('[red]Authentication failed[/red]')
            exit(1)

    delta_max_seconds = parse_duration(delta_max)
    if delta_max_seconds is None:
        console.print('[red]Invalid --delta-max value %r. Use a duration like 30s, 10m, 2h, 1d.[/red]' % delta_max)
        exit(1)

    # Run task
    success = ScanHistoryDuplicatesTask(
        delta_max=delta_max_seconds,
        per_page=per_page,

        assume_yes=assume_yes,
        debug=ctx.parent.debug,
        rate_limit=ctx.parent.rate_limit
    ).run(
        token=token
    )

    if not success:
        exit(1)

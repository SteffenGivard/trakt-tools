from . import commands
from trakt_tools.core.authentication import configure

import click
import logging
import os
import sys


# Load saved credentials (or env vars) and configure the Trakt client
configure()


# Initialize command-line parser
@click.group()
@click.option('--debug/--no-debug', help='Display debug messages.')
@click.option('--rate-limit', default=20, help='Maximum number of requests per minute. (default: 20)')
@click.pass_context
def cli(ctx, debug, rate_limit):
    # Setup logging level
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARN
    )

    # Update context
    ctx.debug = debug
    ctx.rate_limit = rate_limit


# Add commands
cli.add_command(commands.profile_backup_apply)
cli.add_command(commands.profile_backup_create)
cli.add_command(commands.history_duplicates_merge)
cli.add_command(commands.history_duplicates_scan)


def get_prog():
    try:
        if os.path.basename(sys.argv[0]) in ('__main__.py', '-c'):
            return '%s -m trakt_tools' % sys.executable

except (AttributeError, TypeError, IndexError):
        pass

    return 'trakt_tools'


def main():
    cli(prog_name=get_prog(), obj={}, max_content_width=100)


if __name__ == '__main__':
    main()


from trakt_tools.core.console import console
from trakt_tools.models import Backup, Profile
from trakt_tools.tasks.base import Task
from .handlers import CollectionHandler, HistoryHandler, PlaybackHandler, RatingsHandler, WatchlistHandler

from trakt import Trakt
from zipfile import ZipFile, ZIP_DEFLATED
import logging
import os
import shutil

log = logging.getLogger(__name__)


class CreateBackupTask(Task):
    handlers = [
        CollectionHandler,
        HistoryHandler,
        PlaybackHandler,
        RatingsHandler,
        WatchlistHandler
    ]

    def __init__(self, backup_dir, per_page=1000, debug=False, rate_limit=20):
        super(CreateBackupTask, self).__init__(
            debug=debug,
            rate_limit=rate_limit
        )

        self.backup_dir = backup_dir
        self.per_page = per_page

    def run(self, token):
        log.debug('run()')

        # Process backup download
        with Trakt.configuration.oauth(token=token):
            return self.process()

    def process(self, profile=None):
        log.debug('process()')

        if not profile:
            console.print('[dim]Requesting profile...[/dim]')
            profile = Profile.fetch(
                self.per_page,
                self.rate_limit
            )

        if not profile:
            raise Exception('Unable to fetch profile')

        # Create backup
        return self.create_backup(profile)

    def create_backup(self, profile):
        backup = Backup.create(self.backup_dir, profile.username)

        # Run handlers
        for handler in self.handlers:
            h = handler()

            if not h.run(backup, profile):
                console.print('[red]Unable to backup profile, handler %r failed[/red]' % h)
                return False

            console.print('')

        # Compress backup
        console.print('[dim]Compressing backup...[/dim]')

        dest_path = os.path.join(
            self.backup_dir,
            profile.username,
            '%s.zip' % backup.name
        )

        with ZipFile(dest_path, 'w', ZIP_DEFLATED) as archive:
            # Add backup files
            for root, dirs, files in os.walk(backup.path):
                for filename in files:
                    path = os.path.join(root, filename)

                    # Add file to archive
                    archive.write(path, os.path.relpath(path, backup.path))

        # Delete backup directory
        console.print('[dim]Cleaning up...[/dim]')
        shutil.rmtree(backup.path)

        console.print('[bold green]Backup saved to:[/bold green] "%s"' % dest_path)
        return True

# flake8: noqa: W504
from __future__ import print_function

from trakt_tools.core.console import console

import logging
import os

log = logging.getLogger(__name__)


class CollectionHandler(object):
    def run(self, backup, profile):
        console.print('[bold]Collection[/bold]')

        return (
            self.run_media(backup, profile, 'movies') and
            self.run_media(backup, profile, 'shows')
        )

    def run_media(self, backup, profile, media):
        # Request ratings
        response = profile.get('/sync/collection/%s?extended=metadata' % media)

        if response.status_code != 200:
            console.print('  [red]Invalid response returned[/red]')
            return False

        # Retrieve items
        items = response.json()

        if media == 'movies':
            console.print('  Received [cyan]%d[/cyan] movie(s)' % len(items))
        elif media == 'shows':
            console.print('  Received [cyan]%d[/cyan] show(s)' % len(items))
        else:
            console.print('  Received [cyan]%d[/cyan] item(s)' % len(items))

        # Ensure collection directory exists
        collection_dir = os.path.join(backup.path, 'collection')

        if not os.path.exists(collection_dir):
            os.makedirs(collection_dir)

        # Write collected items to disk
        dest_path = os.path.join('collection', '%s.json' % media)

        console.print('  [dim]Writing to "%s"...[/dim]' % dest_path)

        try:
            return backup.write(dest_path, items)
        except Exception as ex:
            log.error('Unable to write collected items to disk: %s', ex, exc_info=True)

        return False

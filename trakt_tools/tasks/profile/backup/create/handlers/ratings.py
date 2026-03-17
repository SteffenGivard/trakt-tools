from __future__ import print_function

from trakt_tools.core.console import console

import logging

log = logging.getLogger(__name__)


class RatingsHandler(object):
    def run(self, backup, profile):
        console.print('[bold]Ratings[/bold]')

        # Request ratings
        response = profile.get('/sync/ratings')

        if response.status_code != 200:
            console.print('  [red]Invalid response returned[/red]')
            return False

        # Retrieve items
        items = response.json()

        console.print('  Received [cyan]%d[/cyan] item(s)' % len(items))
        console.print('  [dim]Writing to "ratings.json"...[/dim]')

        try:
            return backup.write('ratings.json', items)
        except Exception as ex:
            log.error('Unable to write ratings to disk: %s', ex, exc_info=True)

        return False

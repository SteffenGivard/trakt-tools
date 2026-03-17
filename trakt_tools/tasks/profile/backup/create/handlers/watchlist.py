
from trakt_tools.core.console import console

import logging

log = logging.getLogger(__name__)


class WatchlistHandler(object):
    def run(self, backup, profile):
        console.print('[bold]Watchlist[/bold]')

        items = []

        for i, count, page in profile.get_pages('/sync/watchlist'):
            items.extend(page)

        console.print('  Received [cyan]%d[/cyan] item(s)' % len(items))
        console.print('  [dim]Writing to "watchlist.json"...[/dim]')

        try:
            return backup.write('watchlist.json', items)
        except Exception as ex:
            log.error('Unable to write watchlist to disk: %s', ex, exc_info=True)

        return False

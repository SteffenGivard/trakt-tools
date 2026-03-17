import json
import logging
from zipfile import ZipFile

from trakt import Trakt

from trakt_tools.core.console import console
from trakt_tools.core.input import boolean_input

log = logging.getLogger(__name__)


class WatchlistHandler(object):
    def run(self, backup_zip, batch_size=200):
        console.print('[bold]Applying watchlist[/bold]')

        with ZipFile(backup_zip, 'r') as zf:
            with zf.open('watchlist.json') as fp:
                raw = json.load(fp)

        movies = []
        shows = []
        seasons = []
        episodes = []

        for item in raw:
            item_type = item.get('type')

            if item_type == 'movie':
                movies.append({'ids': item['movie']['ids']})
            elif item_type == 'show':
                shows.append({'ids': item['show']['ids']})
            elif item_type == 'season':
                seasons.append({'ids': item['season']['ids']})
            elif item_type == 'episode':
                episodes.append({'ids': item['episode']['ids']})
            else:
                console.print('[yellow]Skipping unknown type "{}": {}[/yellow]'.format(item_type, item))

        buckets = [
            ('movies',   movies),
            ('shows',    shows),
            ('seasons',  seasons),
            ('episodes', episodes),
        ]

        for label, items in buckets:
            console.print('Adding [cyan]{}[/cyan] {}:'.format(len(items), label))
            for x in range(0, max(len(items), 1), batch_size):
                batch = items[x:x + batch_size]
                if batch and not self._add({label: batch}, label):
                    return False

        return True

    @staticmethod
    def _add(payload, label):
        response = Trakt['sync/watchlist'].add(payload)

        added = response.get('added', {})
        console.print('  [green]Added {}[/green] {}'.format(added.get(label, 0), label))

        not_found = response.get('not_found', {})
        failed = not_found.get(label, [])
        if failed:
            console.print('')
            console.print('[red]Unable to apply {} item(s):[/red]'.format(len(failed)))
            for item in failed:
                console.print('  [dim]- %s[/dim]' % item)
            console.print('')
            if not boolean_input('Would you like to continue anyway?', default=False):
                return False

        return True

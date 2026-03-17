import json
import logging
from zipfile import ZipFile

import six
from trakt import Trakt

from trakt_tools.core.console import console
from trakt_tools.core.input import boolean_input

log = logging.getLogger(__name__)


class CollectionHandler(object):
    def run(self, backup_zip, batch_size=200):
        console.print('[bold]Applying collection[/bold]')

        with ZipFile(backup_zip, 'r') as zf:
            with zf.open('collection/movies.json') as fp:
                raw_movies = json.load(fp)
            with zf.open('collection/shows.json') as fp:
                raw_shows = json.load(fp)

        movies = [self._flatten_movie(m) for m in raw_movies]
        shows = [self._flatten_show(s) for s in raw_shows]

        console.print('Adding [cyan]{}[/cyan] movie(s) in batches of {}:'.format(len(movies), batch_size))
        for x in six.moves.xrange(0, max(len(movies), 1), batch_size):
            batch = movies[x:x + batch_size]
            if batch and not self._add({'movies': batch}, 'movies'):
                return False

        console.print('Adding [cyan]{}[/cyan] show(s) in batches of {}:'.format(len(shows), batch_size))
        for x in six.moves.xrange(0, max(len(shows), 1), batch_size):
            batch = shows[x:x + batch_size]
            if batch and not self._add({'shows': batch}, 'shows'):
                return False

        return True

    @staticmethod
    def _flatten_movie(item):
        result = {'ids': item['movie']['ids']}
        if item.get('collected_at'):
            result['collected_at'] = item['collected_at']
        metadata = item.get('metadata') or {}
        result.update(metadata)
        return result

    @staticmethod
    def _flatten_show(item):
        seasons = []
        for season in item.get('seasons', []):
            episodes = []
            for ep in season.get('episodes', []):
                ep_entry = {'number': ep['number']}
                if ep.get('collected_at'):
                    ep_entry['collected_at'] = ep['collected_at']
                metadata = ep.get('metadata') or {}
                ep_entry.update(metadata)
                episodes.append(ep_entry)
            seasons.append({'number': season['number'], 'episodes': episodes})
        return {'ids': item['show']['ids'], 'seasons': seasons}

    @staticmethod
    def _add(payload, label):
        response = Trakt['sync/collection'].add(payload)

        added = response.get('added', {})
        console.print('  [green]Added {}[/green] movie(s), [green]{}[/green] episode(s)'.format(
            added.get('movies', 0),
            added.get('episodes', 0),
        ))

        not_found = response.get('not_found', {})
        failed = not_found.get('movies', []) + not_found.get('shows', []) + not_found.get('episodes', [])
        if failed:
            console.print('')
            console.print('[red]Unable to apply {} item(s):[/red]'.format(len(failed)))
            for item in failed:
                console.print('  [dim]- %s[/dim]' % item)
            console.print('')
            if not boolean_input('Would you like to continue anyway?', default=False):
                return False

        return True

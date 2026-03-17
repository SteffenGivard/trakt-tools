from __future__ import print_function

from trakt_tools.core.console import console

import logging

log = logging.getLogger(__name__)


class PlaybackHandler(object):
    def run(self, backup, profile):
        console.print('[bold]Playback Progress[/bold]')

        # Request ratings
        response = profile.get('/sync/playback')

        if response.status_code != 200:
            console.print('  [red]Invalid response returned[/red]')
            return False

        # Retrieve items
        items = response.json()

        console.print('  Received [cyan]%d[/cyan] item(s)' % len(items))
        console.print('  [dim]Writing to "playback.json"...[/dim]')

        try:
            return backup.write('playback.json', items)
        except Exception as ex:
            log.error('Unable to write playback progress to disk: %s', ex, exc_info=True)

        return False


from trakt_tools.core.console import console

from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeRemainingColumn, TextColumn

import logging

log = logging.getLogger(__name__)


class HistoryHandler(object):
    def run(self, backup, profile):
        console.print('[bold]History[/bold]')

        items = []

        with Progress(
            TextColumn('[progress.description]{task.description}'),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = None

            for i, count, page in profile.get_pages('/sync/history'):
                if task is None:
                    task = progress.add_task('  Fetching...', total=count)

                items.extend(page)
                progress.update(task, completed=i)

        console.print('  [dim]Writing to "history.json"...[/dim]')

        try:
            return backup.write('history.json', items)
        except Exception as ex:
            log.error('Unable to write watched history to disk: %s', ex, exc_info=True)

        return False


from trakt_tools.core.console import console
from trakt_tools.core.helpers import total_seconds



def _format_delta(seconds):
    seconds = int(abs(seconds))
    if seconds < 60:
        return '%ds' % seconds
    minutes = seconds // 60
    if minutes < 60:
        return '%dm' % minutes
    hours = minutes // 60
    remaining = minutes % 60
    if remaining:
        return '%dh %dm' % (hours, remaining)
    return '%dh' % hours


def _format_timestamp(timestamp_utc, timezone):
    ts = timestamp_utc.astimezone(timezone) if timezone else timestamp_utc
    return ts.strftime('%Y-%m-%d %H:%M')


def _print_records(records, representative_utc, timezone, indent):
    """Print a group of records with keep/drop markers and delta."""
    if len(records) == 1:
        # No duplicates in this group — unique play, won't be touched
        ts = _format_timestamp(representative_utc, timezone)
        console.print('%s[dim]·[/dim]  %s' % (indent, ts))
        return

    for i, record in enumerate(records):
        ts = _format_timestamp(record.watched_at, timezone)
        if i == 0:
            console.print('%s[green]✓[/green]  %s' % (indent, ts))
        else:
            delta = total_seconds(record.watched_at - records[0].watched_at)
            console.print('%s[red]✗[/red]  %s [dim](%s apart)[/dim]' % (
                indent, ts, _format_delta(delta)
            ))


class Formatter(object):
    @classmethod
    def movie(cls, movie, timezone=None):
        plain_title = '"%s" (%r)' % (movie.title, movie.year)

        console.print('[bold]"%s"[/bold] [dim](%r)[/dim]  [cyan]%d[/cyan] plays → [green]%d[/green] plays' % (
            movie.title,
            movie.year,
            len(movie.records),
            len(movie.groups)
        ))

        ids = []

        for timestamp_utc, records in movie.groups.items():
            _print_records(records, timestamp_utc, timezone, indent='  ')
            ids.extend([record.id for record in records[1:]])

        return plain_title, ids

    @classmethod
    def show(cls, show, timezone=None):
        plain_title = '"%s" (%r)' % (show.title, show.year)
        console.print('[bold]"%s"[/bold] [dim](%r)[/dim]' % (show.title, show.year))

        return plain_title, Formatter.episodes(show, timezone=timezone)

    @classmethod
    def episodes(cls, show, timezone=None):
        ids = []

        for x, episode in enumerate(show.children.values()):
            console.print('  [cyan]S%02dE%02d[/cyan]  [cyan]%d[/cyan] plays → [green]%d[/green] plays' % (
                episode.season,
                episode.number,
                len(episode.records),
                len(episode.groups)
            ))

            for timestamp_utc, records in episode.groups.items():
                _print_records(records, timestamp_utc, timezone, indent='    ')
                ids.extend([record.id for record in records[1:]])

            if x < len(show.children) - 1:
                console.print('')

        return ids

from __future__ import print_function

from trakt_tools.core.console import console

import six


class Formatter(object):
    @classmethod
    def movie(cls, movie, timezone=None):
        title = '[bold]"%s"[/bold] [dim](%r)[/dim]' % (
            movie.title,
            movie.year
        )
        plain_title = '"%s" (%r)' % (movie.title, movie.year)

        console.print('%s — [cyan]%d[/cyan] plays → [green]%d[/green] plays' % (
            title,
            len(movie.records),
            len(movie.groups)
        ))

        ids = []

        for timestamp_utc, records in movie.groups.items():
            if timezone:
                timestamp = timestamp_utc.astimezone(timezone)
            else:
                timestamp = timestamp_utc

            console.print('  [dim]%s[/dim] [dim italic](%s)[/dim italic]' % (
                timestamp.strftime('%b %d, %Y %I:%M %p %Z'),
                timestamp_utc.isoformat()
            ))

            ids.extend([
                record.id for record in records[1:]
            ])

        return plain_title, ids

    @classmethod
    def show(cls, show, timezone=None):
        plain_title = '"%s" (%r)' % (show.title, show.year)
        console.print('[bold]"%s"[/bold] [dim](%r)[/dim]' % (show.title, show.year))

        return plain_title, Formatter.episodes(show, timezone=timezone)

    @classmethod
    def episodes(cls, show, timezone=None):
        ids = []

        for x, episode in enumerate(six.itervalues(show.children)):
            console.print('  [cyan]S%02dE%02d[/cyan] — [cyan]%d[/cyan] plays → [green]%d[/green] plays' % (
                episode.season,
                episode.number,
                len(episode.records),
                len(episode.groups)
            ))

            for timestamp_utc, records in episode.groups.items():
                if timezone:
                    timestamp = timestamp_utc.astimezone(timezone)
                else:
                    timestamp = timestamp_utc

                console.print('    [dim]%s[/dim] [dim italic](%s)[/dim italic]' % (
                    timestamp.strftime('%b %d, %Y %I:%M %p %Z'),
                    timestamp_utc.isoformat()
                ))

                ids.extend([
                    record.id for record in records[1:]
                ])

            if x < len(show.children) - 1:
                console.print('')

        return ids

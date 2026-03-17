# trakt-tools

Command-line tools for Trakt.tv.

> [!WARNING]
> I've done my best to ensure there aren't any critical bugs in this application, but please ensure your Trakt.tv profile has been backed up before running any operations.

## Install

```
pip install git+https://github.com/SteffenGivard/trakt-tools.git
```

## Usage

From a command-line, either run:

```
trakt_tools [COMMAND] [ARGS]
```

or:

```
python -m trakt_tools.runner.main [COMMAND] [ARGS]
```

### Commands

```
Usage: trakt_tools [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  Display debug messages.
  --rate-limit INTEGER  Maximum number of requests per minute. (default: 20)
  --help                Show this message and exit.

Commands:
  history:duplicates:merge  Merge duplicate history records
  history:duplicates:scan   Scan for duplicate history records
  profile:backup:apply      Apply backup to a Trakt.tv profile
  profile:backup:create     Create backup of a Trakt.tv profile.
```

#### `history:duplicates:merge`

```
Usage: trakt_tools history:duplicates:merge [OPTIONS]

  Merge duplicate history records

Options:
  --token TEXT            Trakt.tv authentication token. (default: "TRAKT_TOKEN" env var, or saved config)
  --backup-dir TEXT       Directory that backups should be stored in. (default: "./backups")
  --delta-max TEXT        Maximum delta between history records to consider as duplicate. (default: 10m)
  --per-page INTEGER      Request page size. (default: 1000)
  --backup / --no-backup  Backup profile before applying any changes. (default: prompt)
  --review / --no-review  Review each action before applying them. (default: prompt)
  --help                  Show this message and exit.
```

#### `history:duplicates:scan`

```
Usage: trakt_tools history:duplicates:scan [OPTIONS]

  Scan for duplicate history records

Options:
  --token TEXT         Trakt.tv authentication token. (default: "TRAKT_TOKEN" env var, or saved config)
  --delta-max TEXT     Maximum delta between history records to consider as duplicate. (default: 10m)
  --per-page INTEGER   Request page size. (default: 1000)
  --help               Show this message and exit.
```

#### `profile:backup:apply`

```
Usage: trakt_tools profile:backup:apply [OPTIONS] BACKUP_ZIP

  Apply backup to a Trakt.tv profile.

  Restores collection, history, ratings, and watchlist from a backup zip.
  Playback progress cannot be restored (no Trakt API endpoint exists for this).

  Note: history already on your profile will be duplicated after applying; run
  `history:duplicates:merge` afterwards to clean up any duplicates.

  BACKUP_ZIP is the location of the zip file created by the profile:backup:create command

Options:
  --token TEXT  Trakt.tv authentication token. (default: "TRAKT_TOKEN" env var, or saved config)
  --help        Show this message and exit.
```

#### `profile:backup:create`

```
Usage: trakt_tools profile:backup:create [OPTIONS]

  Create backup of a Trakt.tv profile.

Options:
  --token TEXT        Trakt.tv authentication token. (default: "TRAKT_TOKEN" env var, or saved config)
  --backup-dir TEXT   Directory that backups should be stored in. (default: "./backups")
  --per-page INTEGER  Request page size. (default: 1000)
  --help              Show this message and exit.
```


# Changelog

## 0.3.0 (2026-03-17)

**Breaking**
- Dropped Python 2 support — Python 3.9+ required
- Removed `six` dependency

**Added**
- Guided first-run setup: prompts for Trakt API credentials and walks through device auth
- Credentials and access token saved to `~/.config/trakt-tools/auth.json` — no need to re-authenticate on each run
- Automatic token refresh when access token is near expiry (within 7 days); falls back to full re-auth if refresh fails
- Rich terminal output: coloured messages, progress bars with ETA on long-running fetches
- `--delta-max` now accepts human-readable durations (`30s`, `10m`, `2h`, `1d`, `1w`, `1mo`, `1y`) in addition to plain seconds
- `-y/--yes` flag on `history:duplicates:merge` and `history:duplicates:scan` for non-interactive/cron use
- Full restore support in `profile:backup:apply`: collection, ratings, and watchlist (playback progress cannot be restored — no Trakt API endpoint exists)
- Duplicate display now shows ✓ (keep) / ✗ (remove) / · (untouched) markers with time-apart on removed records

**Fixed**
- `ex.message` AttributeError on network errors (Python 3 incompatibility)
- `requests` added as an explicit dependency

**Changed**
- `--delta-max` default changed from `600` (seconds) to `10m`
- Removed redundant "logged in as / would you like to continue" prompts
- Updated package metadata and dropped stale example output from README

## 0.2.4 (2026-03-15)

**Changed**
- Converted `README.rst` and `CHANGES.rst` to Markdown

## 0.2.3 (2022-12-28)

**Changed**
- Upload wheels to GitHub Releases

## 0.2.2 (2022-12-28)

**Added**
- Authentication token can be provided with the `TRAKT_TOKEN` environment variable (@outdooracorn)
- `profile:backup:create` now accepts a `-y/--yes` option to ignore the confirmation input (@glensc)

**Changed**
- Support for click v8.1 (@outdooracorn)
- Support for trakt.py v4.4 (@outdooracorn)

## 0.2.1 (2020-04-22)

**Fixed**
- Updated deployment credentials

## 0.2.0 (2020-04-22)

**Breaking**
- Support has been dropped for Python 2.6, 3.0, 3.1, 3.2, 3.3, 3.4

**Added**
- Support for Python 3.6, 3.7
- History from backups can now be applied to profiles (@outdooracorn)

**Fixed**
- Error writing backup files (#1)

## 0.1.8 (2016-09-20)

**Added**
- History retrieval requests are now automatically retried 3 times if any error is returned (timeouts, server overloaded, etc.); a prompt will be displayed if the request fails more than 3 times

**Fixed**
- Failed profile requests were incorrectly being cached

## 0.1.7 (2016-09-19)

**Fixed**
- Records could be duplicated if watched history changes while the scanner is running

## 0.1.6 (2016-09-19)

**Fixed**
- Added missing "six" requirement

## 0.1.5 (2016-09-19)

**Changed**
- History records are now removed in batches of 200 items (to avoid read timeouts)

**Fixed**
- Connection errors weren't being caught correctly during history removal

## 0.1.4 (2016-09-17)

**Fixed**
- Issue deploying GitHub Releases (possible)

## 0.1.3 (2016-09-17)

**Fixed**
- Issue deploying GitHub Releases

## 0.1.2 (2016-09-17)

**Changed**
- Updated package metadata

## 0.1.1 (2016-09-17)

**Fixed**
- PyPI deployment issue in [.travis.yml]

## 0.1.0 (2016-09-17)

Initial release

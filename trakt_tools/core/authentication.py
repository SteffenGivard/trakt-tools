from __future__ import print_function

from trakt_tools.core.console import console
from trakt import Trakt

import json
import os
import requests
import six
import time


CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'trakt-tools', 'auth.json')

# Refresh when fewer than 7 days remain
_EXPIRY_BUFFER = 7 * 24 * 3600


def _load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def _save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def _token_valid(config):
    """Return True if the saved token exists and is not near expiry."""
    if not config.get('access_token'):
        return False
    expires_at = config.get('expires_at')
    if expires_at and time.time() >= (expires_at - _EXPIRY_BUFFER):
        return False
    return True


def _refresh_token(config):
    """Attempt a silent token refresh. Returns True and updates config on success."""
    client_id = os.environ.get('TRAKT_CLIENT_ID') or config.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or config.get('client_secret')
    refresh_token = config.get('refresh_token')

    if not all([client_id, client_secret, refresh_token]):
        return False

    try:
        response = requests.post(
            'https://api.trakt.tv/oauth/token',
            json={
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                'grant_type': 'refresh_token',
            },
            timeout=15,
        )
    except requests.RequestException:
        return False

    if response.status_code != 200:
        return False

    data = response.json()
    config['access_token'] = data['access_token']
    config['refresh_token'] = data.get('refresh_token', refresh_token)
    config['expires_at'] = time.time() + data.get('expires_in', 7776000)
    _save_config(config)
    return True


def configure():
    """Load saved credentials and configure the Trakt client. Called at startup."""
    config = _load_config()
    client_id = os.environ.get('TRAKT_CLIENT_ID') or config.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or config.get('client_secret')
    if client_id and client_secret:
        Trakt.configuration.defaults.client(id=client_id, secret=client_secret)


def authenticate():
    config = _load_config()

    # Return saved token if it's still valid
    if _token_valid(config):
        return True, config['access_token']

    # Token exists but is expired or near expiry — try a silent refresh first
    if config.get('access_token'):
        console.print('[yellow]Access token expired, refreshing...[/yellow]')
        if _refresh_token(config):
            console.print('[green]Token refreshed successfully.[/green]')
            return True, config['access_token']
        console.print('[yellow]Token refresh failed, re-authenticating...[/yellow]')
        # Clear the stale token so the device flow runs cleanly
        config.pop('access_token', None)
        config.pop('refresh_token', None)
        config.pop('expires_at', None)
        _save_config(config)

    # Ensure API credentials are available
    client_id = os.environ.get('TRAKT_CLIENT_ID') or config.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or config.get('client_secret')

    if not client_id or not client_secret:
        console.print('')
        console.print('[bold]To use trakt-tools, you need a Trakt API application.[/bold]')
        console.print('')
        console.print('  1. Go to [link=https://trakt.tv/oauth/applications/new]https://trakt.tv/oauth/applications/new[/link]')
        console.print('  2. Give your application a name (e.g. [italic]trakt-tools[/italic])')
        console.print('  3. Set the redirect URI to [bold]urn:ietf:wg:oauth:2.0:oob[/bold]')
        console.print('  4. Save the application and copy the Client ID and Client Secret')
        console.print('')

        client_id = six.moves.input('Client ID: ').strip()
        client_secret = six.moves.input('Client Secret: ').strip()

        if not client_id or not client_secret:
            console.print('[red]ERROR: Client ID and Client Secret are required.[/red]')
            return False, None

        config['client_id'] = client_id
        config['client_secret'] = client_secret
        _save_config(config)

        Trakt.configuration.defaults.client(id=client_id, secret=client_secret)

    # Request a device code
    result = Trakt['oauth/device'].code()

    if not result:
        console.print('[red]ERROR: Unable to request a device code. Check that your Client ID and Client Secret are correct.[/red]')
        console.print('[dim]To reset saved credentials, delete: %s[/dim]' % CONFIG_PATH)
        return False, None

    console.print('')
    console.print('  Navigate to: [bold cyan]%s[/bold cyan]' % result.get('verification_url', 'https://trakt.tv/activate'))
    console.print('  Enter code:  [bold cyan]%s[/bold cyan]' % result['user_code'])
    console.print('')
    six.moves.input('Press ENTER once you have authorized the application...')

    # Exchange device code for access token
    authorization = Trakt['oauth/device'].token(result['device_code'])

    if not authorization or not authorization.get('access_token'):
        console.print('[red]ERROR: Failed to obtain access token. Please try again.[/red]')
        return False, None

    config['access_token'] = authorization['access_token']
    config['refresh_token'] = authorization.get('refresh_token')
    config['expires_at'] = time.time() + authorization.get('expires_in', 7776000)
    _save_config(config)

    return True, authorization['access_token']

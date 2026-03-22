
from trakt_tools.core.console import console
from trakt import Trakt

import json
import os
import requests
import time


CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'trakt-tools', 'auth.json')

# Refresh when fewer than 7 days remain
_EXPIRY_BUFFER = 7 * 24 * 3600


def _load_config():
    if not os.path.exists(CONFIG_PATH):
        return {'accounts': {}}
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    # Migrate old flat format
    if 'client_id' in data or 'access_token' in data:
        data = {'active': 'default', 'accounts': {'default': data}}
        _save_config(data)
    return data


def _save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def _active_name(config):
    accounts = config.get('accounts', {})
    return config.get('active') or (next(iter(accounts)) if accounts else None)


def _get_account(config, name=None):
    """Return (name, account_dict) for the given name, or the active account."""
    accounts = config.get('accounts', {})
    name = name or _active_name(config)
    if not name or name not in accounts:
        return name, {}
    return name, accounts[name]


def _token_valid(account):
    if not account.get('access_token'):
        return False
    expires_at = account.get('expires_at')
    if expires_at and time.time() >= (expires_at - _EXPIRY_BUFFER):
        return False
    return True


def _refresh_token(config, name, account):
    """Attempt a silent token refresh. Updates account in-place and saves on success."""
    client_id = os.environ.get('TRAKT_CLIENT_ID') or account.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or account.get('client_secret')
    refresh_token = account.get('refresh_token')

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
    account['access_token'] = data['access_token']
    account['refresh_token'] = data.get('refresh_token', refresh_token)
    account['expires_at'] = time.time() + data.get('expires_in', 7776000)
    config['accounts'][name] = account
    _save_config(config)
    return True


def _fetch_username(access_token, client_id):
    """Fetch the Trakt username for the authenticated user."""
    try:
        response = requests.get(
            'https://api.trakt.tv/users/me',
            headers={
                'Authorization': 'Bearer %s' % access_token,
                'trakt-api-version': '2',
                'trakt-api-key': client_id,
                'Content-Type': 'application/json',
            },
            timeout=15,
        )
        if response.status_code == 200:
            return response.json().get('username')
    except requests.RequestException:
        pass
    return None


def _prompt_credentials(existing_client_id=None, existing_client_secret=None):
    """Walk the user through getting API credentials. Returns (client_id, client_secret)."""
    console.print('')
    console.print('[bold]To use trakt-tools, you need a Trakt API application.[/bold]')
    console.print('')
    console.print('  1. Go to [link=https://trakt.tv/oauth/applications/new]'
                  'https://trakt.tv/oauth/applications/new[/link]')
    console.print('  2. Give your application a name (e.g. [italic]trakt-tools[/italic])')
    console.print('  3. Set the redirect URI to [bold]urn:ietf:wg:oauth:2.0:oob[/bold]')
    console.print('  4. Save the application and copy the Client ID and Client Secret')
    console.print('')

    if existing_client_id and existing_client_secret:
        console.print('[dim]Leave blank to reuse credentials from the active account.[/dim]')
        console.print('')

    client_id = input('Client ID: ').strip()
    if not client_id and existing_client_id:
        client_id = existing_client_id

    client_secret = input('Client Secret: ').strip()
    if not client_secret and existing_client_secret:
        client_secret = existing_client_secret

    return client_id or None, client_secret or None


def _device_auth_flow(client_id, client_secret):
    """Run device auth and return (access_token, refresh_token, expires_in) or None."""
    Trakt.configuration.defaults.client(id=client_id, secret=client_secret)

    result = Trakt['oauth/device'].code()
    if not result:
        console.print('[red]ERROR: Unable to request a device code. Check your Client ID and Client Secret.[/red]')
        return None

    console.print('')
    url = result.get('verification_url', 'https://trakt.tv/activate')
    console.print('  Navigate to: [bold cyan]%s[/bold cyan]' % url)
    console.print('  Enter code:  [bold cyan]%s[/bold cyan]' % result['user_code'])
    console.print('')
    input('Press ENTER once you have authorized the application...')

    authorization = Trakt['oauth/device'].token(result['device_code'])
    if not authorization or not authorization.get('access_token'):
        console.print('[red]ERROR: Failed to obtain access token. Please try again.[/red]')
        return None

    return authorization


def configure(account_name=None):
    """Load saved credentials and configure the Trakt client. Called at startup."""
    config = _load_config()
    _, account = _get_account(config, account_name)
    client_id = os.environ.get('TRAKT_CLIENT_ID') or account.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or account.get('client_secret')
    if client_id and client_secret:
        Trakt.configuration.defaults.client(id=client_id, secret=client_secret)


def authenticate(account_name=None):
    """Return (success, access_token) for the given account (or active account)."""
    config = _load_config()
    name, account = _get_account(config, account_name)

    # Reconfigure Trakt client for this account
    client_id = os.environ.get('TRAKT_CLIENT_ID') or account.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or account.get('client_secret')
    if client_id and client_secret:
        Trakt.configuration.defaults.client(id=client_id, secret=client_secret)

    # Return saved token if still valid
    if _token_valid(account):
        return True, account['access_token']

    # Token exists but expired — try silent refresh
    if account.get('access_token'):
        console.print('[yellow]Access token expired, refreshing...[/yellow]')
        if name and _refresh_token(config, name, account):
            console.print('[green]Token refreshed successfully.[/green]')
            return True, account['access_token']
        console.print('[yellow]Token refresh failed, re-authenticating...[/yellow]')
        account.pop('access_token', None)
        account.pop('refresh_token', None)
        account.pop('expires_at', None)

    # Ensure API credentials
    if not client_id or not client_secret:
        # Get active account's credentials to offer reuse when adding a second account
        _, active_account = _get_account(config)
        existing_id = active_account.get('client_id') if active_account else None
        existing_secret = active_account.get('client_secret') if active_account else None
        client_id, client_secret = _prompt_credentials(existing_id, existing_secret)
        if not client_id or not client_secret:
            console.print('[red]ERROR: Client ID and Client Secret are required.[/red]')
            return False, None
        account['client_id'] = client_id
        account['client_secret'] = client_secret

    authorization = _device_auth_flow(client_id, client_secret)
    if not authorization:
        return False, None

    account['access_token'] = authorization['access_token']
    account['refresh_token'] = authorization.get('refresh_token')
    account['expires_at'] = time.time() + authorization.get('expires_in', 7776000)

    # Auto-name the account from the Trakt username if we don't have a name yet
    if not name:
        username = _fetch_username(account['access_token'], client_id)
        name = username or 'default'

    config.setdefault('accounts', {})[name] = account
    if not config.get('active'):
        config['active'] = name
    _save_config(config)

    return True, account['access_token']


# ---------------------------------------------------------------------------
# Account management helpers (used by account:* commands)
# ---------------------------------------------------------------------------

def list_accounts():
    """Return (active_name, accounts_dict)."""
    config = _load_config()
    return _active_name(config), config.get('accounts', {})


def add_account(name=None):
    """Add a new account via device auth. Auto-names from Trakt username if name omitted."""
    config = _load_config()
    accounts = config.setdefault('accounts', {})

    # Offer to reuse credentials from active account
    _, active_account = _get_account(config)
    existing_id = active_account.get('client_id') if active_account else None
    existing_secret = active_account.get('client_secret') if active_account else None

    client_id, client_secret = _prompt_credentials(existing_id, existing_secret)
    if not client_id or not client_secret:
        console.print('[red]ERROR: Client ID and Client Secret are required.[/red]')
        return False

    authorization = _device_auth_flow(client_id, client_secret)
    if not authorization:
        return False

    access_token = authorization['access_token']

    # Resolve account name
    if not name:
        username = _fetch_username(access_token, client_id)
        name = username or 'account%d' % (len(accounts) + 1)

    if name in accounts:
        console.print('[red]Account [bold]%s[/bold] already exists. '
                      'Use a different name or delete it first.[/red]' % name)
        return False

    accounts[name] = {
        'client_id': client_id,
        'client_secret': client_secret,
        'access_token': access_token,
        'refresh_token': authorization.get('refresh_token'),
        'expires_at': time.time() + authorization.get('expires_in', 7776000),
    }

    if not config.get('active'):
        config['active'] = name

    _save_config(config)
    console.print('[green]Account [bold]%s[/bold] added successfully.[/green]' % name)
    return True


def switch_account(name):
    """Set the active account."""
    config = _load_config()
    if name not in config.get('accounts', {}):
        console.print('[red]Account [bold]%s[/bold] not found.[/red]' % name)
        return False
    config['active'] = name
    _save_config(config)
    return True


def delete_account(name):
    """Remove an account from the config."""
    config = _load_config()
    accounts = config.get('accounts', {})
    if name not in accounts:
        console.print('[red]Account [bold]%s[/bold] not found.[/red]' % name)
        return False
    del accounts[name]
    # If we deleted the active account, switch to another
    if config.get('active') == name:
        config['active'] = next(iter(accounts)) if accounts else None
    _save_config(config)
    return True

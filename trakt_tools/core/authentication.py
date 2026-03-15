from __future__ import print_function

from trakt import Trakt
import json
import os
import six


CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'trakt-tools', 'auth.json')


def _load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def _save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def configure():
    """Load saved credentials and configure the Trakt client. Called at startup."""
    config = _load_config()
    client_id = os.environ.get('TRAKT_CLIENT_ID') or config.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or config.get('client_secret')
    if client_id and client_secret:
        Trakt.configuration.defaults.client(id=client_id, secret=client_secret)


def authenticate():
    config = _load_config()

    # Return saved token if present
    if config.get('access_token'):
        return True, config['access_token']

    # Ensure API credentials are available
    client_id = os.environ.get('TRAKT_CLIENT_ID') or config.get('client_id')
    client_secret = os.environ.get('TRAKT_CLIENT_SECRET') or config.get('client_secret')

    if not client_id or not client_secret:
        print('To use trakt-tools, you need a Trakt API application.')
        print('')
        print('  1. Go to https://trakt.tv/oauth/applications/new')
        print('  2. Give your application a name (e.g. "trakt-tools")')
        print('  3. Set the redirect URI to "urn:ietf:wg:oauth:2.0:oob"')
        print('  4. Save the application and copy the Client ID and Client Secret')
        print('')

        client_id = six.moves.input('Client ID: ').strip()
        client_secret = six.moves.input('Client Secret: ').strip()

        if not client_id or not client_secret:
            print('ERROR: Client ID and Client Secret are required.')
            return False, None

        config['client_id'] = client_id
        config['client_secret'] = client_secret
        _save_config(config)

        Trakt.configuration.defaults.client(id=client_id, secret=client_secret)

    # Request a device code
    result = Trakt['oauth/device'].code()

    if not result:
        print('ERROR: Unable to request a device code. Check that your Client ID and Client Secret are correct.')
        print('To reset saved credentials, delete: %s' % CONFIG_PATH)
        return False, None

    print('')
    print('  Navigate to: %s' % result.get('verification_url', 'https://trakt.tv/activate'))
    print('  Enter code:  %s' % result['user_code'])
    print('')
    six.moves.input('Press ENTER once you have authorized the application...')

    # Exchange device code for access token
    authorization = Trakt['oauth/device'].token(result['device_code'])

    if not authorization or not authorization.get('access_token'):
        print('ERROR: Failed to obtain access token. Please try again.')
        return False, None

    config['access_token'] = authorization['access_token']
    _save_config(config)

    return True, authorization['access_token']

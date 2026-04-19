"""sync.py — Pull suppressions from D1 via xavigate-api"""

import urllib.request
import json

import config as cfg_mod
import db


def pull() -> dict:
    """
    Fetch all suppressions from D1 via /mailer/suppressions and upsert into local SQLite.
    Returns {added, total}.
    """
    cfg = cfg_mod.load()
    api_base = cfg['api_base'].rstrip('/')
    secret = cfg['mailer_secret']
    url = f'{api_base}/mailer/suppressions'

    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {secret}',
            'User-Agent': 'XaviMail/1.0 (internal sync)',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Sync failed: HTTP {e.code} — {e.read().decode()}')
    except Exception as e:
        raise RuntimeError(f'Sync failed: {e}')

    remote = data.get('suppressions', [])
    before = len(db.get_suppressions())
    db.upsert_suppressions(remote)
    after = len(db.get_suppressions())

    return {'added': after - before, 'total': after, 'remote': len(remote)}

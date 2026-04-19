"""sync.py — Pull suppressions and tracking events from D1 via xavigate-api"""

import urllib.request
import json

import config as cfg_mod
import db


def _get(url, secret):
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {secret}',
            'User-Agent': 'XaviMail/1.0 (internal sync)',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Request failed: HTTP {e.code} — {e.read().decode()}')
    except Exception as e:
        raise RuntimeError(f'Request failed: {e}')


def pull() -> dict:
    """Fetch suppressions + events from D1, upsert into local SQLite."""
    cfg = cfg_mod.load()
    api_base = cfg['api_base'].rstrip('/')
    secret = cfg['mailer_secret']

    # Suppressions
    data = _get(f'{api_base}/mailer/suppressions', secret)
    remote = data.get('suppressions', [])
    before = len(db.get_suppressions())
    db.upsert_suppressions(remote)
    after = len(db.get_suppressions())

    # Events — fetch since last known event
    conn = db._db()
    last_row = conn.execute(
        "SELECT MAX(occurred_at) FROM events"
    ).fetchone()
    since = last_row[0] or '1970-01-01'
    import urllib.parse as _up
    edata = _get(f'{api_base}/mailer/events?since={_up.quote(since)}', secret)
    new_events = edata.get('events', [])
    for e in new_events:
        try:
            db.log_event(
                send_id=e['send_id'],
                email=e['email'],
                event_type=e['event_type'],
                metadata=json.loads(e.get('metadata') or '{}'),
            )
        except Exception:
            pass  # duplicate or schema mismatch — skip

    return {
        'added': after - before,
        'total': after,
        'remote': len(remote),
        'new_events': len(new_events),
    }


def delete_remote(email: str) -> bool:
    """Delete a suppression from D1. Returns True on success."""
    cfg = cfg_mod.load()
    api_base = cfg['api_base'].rstrip('/')
    secret = cfg['mailer_secret']
    import urllib.parse
    url = f'{api_base}/mailer/suppressions/{urllib.parse.quote(email.lower(), safe="@")}'
    req = urllib.request.Request(
        url,
        method='DELETE',
        headers={
            'Authorization': f'Bearer {secret}',
            'User-Agent': 'XaviMail/1.0 (internal sync)',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Delete failed: HTTP {e.code} — {e.read().decode()}')
    except Exception as e:
        raise RuntimeError(f'Delete failed: {e}')

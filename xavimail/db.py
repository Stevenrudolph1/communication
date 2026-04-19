"""db.py — XaviMail SQLite layer"""

import json
import sqlite3
from pathlib import Path
import config as cfg_mod

_conn = None

def _db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        cfg = cfg_mod.load()
        db_path = Path(cfg['db_path'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(db_path))
        _conn.row_factory = sqlite3.Row
        _conn.execute('PRAGMA journal_mode=WAL')
        _conn.execute('PRAGMA foreign_keys=ON')
        init(_conn)
    return _conn


def init(conn: sqlite3.Connection):
    # Migrations for existing databases
    try:
        conn.execute("ALTER TABLE subscribers ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
        conn.commit()
    except Exception:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE subscribers ADD COLUMN attribs TEXT NOT NULL DEFAULT '{}'")
        conn.commit()
    except Exception:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE list_members ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
        conn.commit()
    except Exception:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE sends ADD COLUMN sequence TEXT")
        conn.execute("ALTER TABLE sends ADD COLUMN step_num INTEGER")
        conn.commit()
    except Exception:
        pass  # Columns already exist

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS lists (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS subscribers (
            email       TEXT PRIMARY KEY,
            first_name  TEXT DEFAULT '',
            last_name   TEXT DEFAULT '',
            status      TEXT NOT NULL DEFAULT 'active',
            attribs     TEXT NOT NULL DEFAULT '{}',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS list_members (
            list_id    INTEGER NOT NULL,
            email      TEXT NOT NULL,
            status     TEXT NOT NULL DEFAULT 'active',
            added_at   TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (list_id, email)
        );

        CREATE TABLE IF NOT EXISTS suppressions (
            email      TEXT PRIMARY KEY,
            reason     TEXT NOT NULL DEFAULT 'unsubscribe',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sends (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            list_name       TEXT NOT NULL,
            subject         TEXT NOT NULL,
            body_file       TEXT,
            sent_at         TEXT DEFAULT (datetime('now')),
            recipient_count INTEGER DEFAULT 0,
            skipped_count   INTEGER DEFAULT 0,
            sequence        TEXT,
            step_num        INTEGER
        );

        CREATE TABLE IF NOT EXISTS send_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            send_id    INTEGER NOT NULL,
            email      TEXT NOT NULL,
            sent_at    TEXT DEFAULT (datetime('now')),
            message_id TEXT,
            status     TEXT DEFAULT 'sent'
        );

        CREATE TABLE IF NOT EXISTS sequence_sends (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            sequence     TEXT NOT NULL,
            step_num     INTEGER NOT NULL,
            list_name    TEXT NOT NULL,
            send_id      INTEGER,
            sent_at      TEXT DEFAULT (datetime('now')),
            UNIQUE(sequence, step_num, list_name)
        );

        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            send_id     INTEGER NOT NULL,
            email       TEXT NOT NULL,
            event_type  TEXT NOT NULL,
            occurred_at TEXT DEFAULT (datetime('now')),
            metadata    TEXT NOT NULL DEFAULT '{}'
        );

        CREATE INDEX IF NOT EXISTS idx_list_members_list ON list_members(list_id);
        CREATE INDEX IF NOT EXISTS idx_send_log_send ON send_log(send_id);
        CREATE INDEX IF NOT EXISTS idx_send_log_email ON send_log(email);
        CREATE INDEX IF NOT EXISTS idx_sequence_sends ON sequence_sends(sequence, step_num);
        CREATE INDEX IF NOT EXISTS idx_events_send ON events(send_id);
        CREATE INDEX IF NOT EXISTS idx_events_email ON events(email);
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
    """)
    conn.commit()


# ── Lists ─────────────────────────────────────────────────────────────────────

def get_lists() -> list[dict]:
    rows = _db().execute("""
        SELECT l.id, l.name, l.description, l.created_at,
               COUNT(lm.email) AS subscriber_count
        FROM lists l
        LEFT JOIN list_members lm ON lm.list_id = l.id
        GROUP BY l.id ORDER BY l.name
    """).fetchall()
    return [dict(r) for r in rows]


def get_list_by_name(name: str) -> dict | None:
    row = _db().execute('SELECT * FROM lists WHERE name = ?', (name,)).fetchone()
    return dict(row) if row else None


def create_list(name: str, description: str = '') -> dict:
    db = _db()
    db.execute('INSERT OR IGNORE INTO lists (name, description) VALUES (?, ?)', (name, description))
    db.commit()
    return get_list_by_name(name)


# ── Subscribers ───────────────────────────────────────────────────────────────

def upsert_subscriber(email: str, first_name: str = '', last_name: str = '',
                      status: str = 'active', attribs: dict | None = None):
    db = _db()
    attribs_json = json.dumps(attribs or {})
    db.execute("""
        INSERT INTO subscribers (email, first_name, last_name, status, attribs)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            first_name = CASE WHEN excluded.first_name != '' THEN excluded.first_name ELSE first_name END,
            last_name  = CASE WHEN excluded.last_name  != '' THEN excluded.last_name  ELSE last_name  END,
            status     = CASE WHEN excluded.status != 'active' THEN excluded.status ELSE status END,
            attribs    = CASE WHEN excluded.attribs != '{}' THEN excluded.attribs ELSE attribs END
    """, (email.lower(), first_name, last_name, status, attribs_json))
    db.commit()


def set_subscriber_status(email: str, status: str):
    db = _db()
    db.execute("UPDATE subscribers SET status = ? WHERE email = ?", (status, email.lower()))
    db.commit()


def add_to_list(list_id: int, email: str):
    db = _db()
    db.execute("""
        INSERT OR IGNORE INTO list_members (list_id, email) VALUES (?, ?)
    """, (list_id, email.lower()))
    db.commit()


def remove_from_list(list_id: int, email: str):
    db = _db()
    db.execute('DELETE FROM list_members WHERE list_id = ? AND email = ?', (list_id, email.lower()))
    db.commit()


def unsubscribe_from_list(list_id: int, email: str):
    """Mark member as unsubscribed from this list only (soft — keeps record for audit)."""
    db = _db()
    db.execute(
        "UPDATE list_members SET status = 'unsubscribed' WHERE list_id = ? AND email = ?",
        (list_id, email.lower())
    )
    db.commit()


def get_list_members(list_id: int) -> list[dict]:
    rows = _db().execute("""
        SELECT s.email, s.first_name, s.last_name, s.status AS subscriber_status,
               s.attribs, lm.status AS list_status, lm.added_at
        FROM list_members lm
        JOIN subscribers s ON s.email = lm.email
        WHERE lm.list_id = ?
        ORDER BY s.last_name, s.first_name, s.email
    """, (list_id,)).fetchall()
    return [dict(r) for r in rows]


def get_active_recipients(list_id: int) -> list[dict]:
    """List members minus global suppressions and per-list unsubscribes."""
    rows = _db().execute("""
        SELECT s.email, s.first_name, s.last_name
        FROM list_members lm
        JOIN subscribers s ON s.email = lm.email
        WHERE lm.list_id = ?
          AND lm.status = 'active'
          AND s.email NOT IN (SELECT email FROM suppressions)
        ORDER BY s.last_name, s.first_name, s.email
    """, (list_id,)).fetchall()
    return [dict(r) for r in rows]


# ── Suppressions ──────────────────────────────────────────────────────────────

def get_suppressions() -> list[dict]:
    rows = _db().execute(
        'SELECT email, reason, created_at FROM suppressions ORDER BY created_at DESC'
    ).fetchall()
    return [dict(r) for r in rows]


_SUPPRESSION_TO_STATUS = {
    'unsubscribe': 'unsubscribed',
    'bounce':      'bounced',
    'complaint':   'complained',
}

def add_suppression(email: str, reason: str = 'unsubscribe'):
    db = _db()
    email = email.lower()
    db.execute("""
        INSERT INTO suppressions (email, reason)
        VALUES (?, ?)
        ON CONFLICT(email) DO UPDATE SET reason = excluded.reason, created_at = datetime('now')
    """, (email, reason))
    # Mirror status onto subscriber record if it exists
    sub_status = _SUPPRESSION_TO_STATUS.get(reason, 'unsubscribed')
    db.execute(
        "UPDATE subscribers SET status = ? WHERE email = ?",
        (sub_status, email)
    )
    db.commit()


def upsert_suppressions(suppressions: list[dict]):
    """Bulk upsert suppressions from D1 sync."""
    db = _db()
    db.executemany("""
        INSERT INTO suppressions (email, reason, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            reason     = excluded.reason,
            created_at = excluded.created_at
    """, [(s['email'].lower(), s['reason'], s['created_at']) for s in suppressions])
    db.commit()


# ── Send log ──────────────────────────────────────────────────────────────────

def log_send(list_name: str, subject: str, body_file: str,
             recipient_count: int, skipped_count: int,
             sequence: str = None, step_num: int = None) -> int:
    db = _db()
    cur = db.execute("""
        INSERT INTO sends (list_name, subject, body_file, recipient_count, skipped_count,
                           sequence, step_num)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (list_name, subject, body_file, recipient_count, skipped_count, sequence, step_num))
    db.commit()
    return cur.lastrowid


def log_send_item(send_id: int, email: str, message_id: str, status: str = 'sent'):
    db = _db()
    db.execute("""
        INSERT INTO send_log (send_id, email, message_id, status) VALUES (?, ?, ?, ?)
    """, (send_id, email, message_id, status))
    db.commit()


def get_sends(limit: int = 20) -> list[dict]:
    rows = _db().execute("""
        SELECT id, list_name, subject, sent_at, recipient_count, skipped_count,
               sequence, step_num
        FROM sends ORDER BY sent_at DESC LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]


def already_sent(send_id: int, email: str) -> bool:
    row = _db().execute(
        'SELECT 1 FROM send_log WHERE send_id = ? AND email = ?', (send_id, email)
    ).fetchone()
    return row is not None


# ── Sequence tracking ─────────────────────────────────────────────────────────

def sequence_step_sent(sequence: str, step_num: int, list_name: str) -> dict | None:
    """Return the sequence_sends row if this step was already sent, else None."""
    row = _db().execute(
        'SELECT * FROM sequence_sends WHERE sequence=? AND step_num=? AND list_name=?',
        (sequence, step_num, list_name)
    ).fetchone()
    return dict(row) if row else None


def record_sequence_send(sequence: str, step_num: int, list_name: str, send_id: int):
    db = _db()
    db.execute("""
        INSERT INTO sequence_sends (sequence, step_num, list_name, send_id)
        VALUES (?, ?, ?, ?)
    """, (sequence, step_num, list_name, send_id))
    db.commit()


# ── Events (opens, clicks) ────────────────────────────────────────────────────

def log_event(send_id: int, email: str, event_type: str, metadata: dict = None):
    """Record an open, click, or other tracking event."""
    db = _db()
    db.execute("""
        INSERT INTO events (send_id, email, event_type, metadata)
        VALUES (?, ?, ?, ?)
    """, (send_id, email.lower(), event_type, json.dumps(metadata or {})))
    db.commit()


def get_events(send_id: int = None, email: str = None, event_type: str = None,
               limit: int = 100) -> list[dict]:
    where, params = [], []
    if send_id:   where.append('send_id = ?');    params.append(send_id)
    if email:     where.append('email = ?');      params.append(email.lower())
    if event_type: where.append('event_type = ?'); params.append(event_type)
    sql = 'SELECT * FROM events'
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY occurred_at DESC LIMIT ?'
    params.append(limit)
    rows = _db().execute(sql, params).fetchall()
    return [dict(r) for r in rows]


# ── Sequence tracking ─────────────────────────────────────────────────────────

def get_sequence_history(sequence: str) -> list[dict]:
    rows = _db().execute("""
        SELECT step_num, list_name, sent_at, send_id
        FROM sequence_sends WHERE sequence=?
        ORDER BY step_num, list_name
    """, (sequence,)).fetchall()
    return [dict(r) for r in rows]

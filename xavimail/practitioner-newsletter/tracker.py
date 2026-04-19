#!/usr/bin/env python3
"""
Practitioner Newsletter Tracker
Stores metadata in the XaviMail DB (newsletter_meta table).
Provides a 30-second pre-write scan and a recycling view.

Usage:
  python3 tracker.py status              # variety balance, last 4 weeks
  python3 tracker.py history [N]         # last N sent (default 12)
  python3 tracker.py scan TOPIC-ID       # has this topic run recently?
  python3 tracker.py recycle             # topics ready to reuse (6+ months)
  python3 tracker.py log ...             # record a sent email
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
from collections import Counter

DB = os.path.expanduser("~/.xavimail/xavimail.db")

CATEGORY_NAMES = {
    "A": "Practitioner Skills",
    "B": "Career Spotlights",
    "C": "Practitioner Identity",
    "D": "Framework Comparisons",
    "E": "Books & Resources",
    "F": "Client Situations",
    "G": "Industry Trends",
    "H": "Quick Tips",
    "I": "Self-Care",
    "J": "Personal Branding",
    "K": "Business",
    "L": "Humor",
    "M": "Trainer Program",
}

# Evergreen categories: safe to recycle after 26 weeks
# Timely categories: recycle only after 52 weeks, with heavy reframe
TIMELY_CATEGORIES = {"G", "M"}
RECYCLE_WEEKS_EVERGREEN = 26
RECYCLE_WEEKS_TIMELY = 52

SLOT_NAMES = {"tue": "Tuesday", "thu": "Thursday", "sat": "Saturday"}


def db():
    return sqlite3.connect(DB)


def weeks_ago(date_str):
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (datetime.now() - d).days / 7
    except:
        return 999


def cmd_status():
    con = db()
    rows = con.execute(
        "SELECT send_date, slot, category, topic_id, subject FROM newsletter_meta ORDER BY send_date DESC"
    ).fetchall()
    con.close()

    if not rows:
        print("\n  No emails logged yet.\n")
        return

    now = datetime.now()
    last_4w = [r for r in rows if weeks_ago(r[0]) <= 4]
    last_1w = [r for r in rows if weeks_ago(r[0]) <= 1]

    print(f"\n{'='*60}")
    print(f"  NEWSLETTER STATUS  —  {now.strftime('%Y-%m-%d')}")
    print(f"{'='*60}")
    print(f"  Total sent:    {len(rows)}")
    print(f"  Last 4 weeks:  {len(last_4w)}")
    print(f"  Last 7 days:   {len(last_1w)}")
    print(f"  Most recent:   {rows[0][0]} [{rows[0][1].upper()}] {rows[0][4][:45]}")

    print(f"\n  Category mix (last 4 weeks):")
    cat_counts = Counter(r[2] for r in last_4w)
    all_cats = sorted(set(list(CATEGORY_NAMES.keys())))
    for cat in all_cats:
        n = cat_counts.get(cat, 0)
        if n:
            print(f"    {cat}  {CATEGORY_NAMES.get(cat,'?'):<28}  {'█' * n}  {n}")

    print(f"\n  Slot balance (last 4 weeks):")
    slot_counts = Counter(r[1] for r in last_4w)
    for slot in ["tue", "thu", "sat"]:
        print(f"    {slot.upper()}: {slot_counts.get(slot, 0)}")
    print()


def cmd_history(n=12):
    con = db()
    rows = con.execute(
        "SELECT send_date, slot, category, topic_id, subject, evergreen FROM newsletter_meta ORDER BY send_date DESC LIMIT ?",
        (n,)
    ).fetchall()
    con.close()

    if not rows:
        print("\n  Nothing logged yet.\n")
        return

    print(f"\n{'='*70}")
    print(f"  LAST {len(rows)} EMAILS")
    print(f"{'='*70}")
    for r in rows:
        date, slot, cat, tid, subject, ev = r
        w = weeks_ago(date)
        tag = "E" if ev else "T"  # Evergreen / Timely
        print(f"  {date}  {slot.upper()}  [{cat}:{tag}]  {tid:<6}  {subject[:42]}")
    print()


def cmd_scan(topic_id):
    """Check if a topic has been sent recently — the 30-second pre-write check."""
    con = db()
    cat = topic_id[0] if topic_id else "?"
    threshold = RECYCLE_WEEKS_TIMELY if cat in TIMELY_CATEGORIES else RECYCLE_WEEKS_EVERGREEN

    # Has this exact topic been sent?
    topic_rows = con.execute(
        "SELECT send_date, subject FROM newsletter_meta WHERE topic_id = ? ORDER BY send_date DESC",
        (topic_id,)
    ).fetchall()

    # Has the same category run in the last 2 weeks?
    recent_cat = con.execute(
        "SELECT send_date, slot, subject FROM newsletter_meta WHERE category = ? AND send_date >= ? ORDER BY send_date DESC",
        (cat, (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%d"))
    ).fetchall()

    # Has the same kernel run in the last 4 weeks?
    con.close()

    print(f"\n  SCAN: {topic_id}  [{CATEGORY_NAMES.get(cat, cat)}]")
    print(f"  {'Timely' if cat in TIMELY_CATEGORIES else 'Evergreen'} — recycle threshold: {threshold} weeks\n")

    if topic_rows:
        last_date, last_subject = topic_rows[0]
        w = weeks_ago(last_date)
        if w < threshold:
            print(f"  ✗  Sent {w:.0f} weeks ago — too soon (needs {threshold - w:.0f} more weeks)")
            print(f"     Was: \"{last_subject}\"")
        else:
            print(f"  ✓  Sent {w:.0f} weeks ago — eligible to recycle (reframe recommended)")
            print(f"     Was: \"{last_subject}\"")
        if len(topic_rows) > 1:
            print(f"     (sent {len(topic_rows)} times total)")
    else:
        print(f"  ✓  Never sent — clear to go")

    if recent_cat:
        print(f"\n  Note: Category {cat} ran recently:")
        for d, sl, subj in recent_cat:
            print(f"    {d} [{sl.upper()}] {subj[:50]}")
        print(f"  Check variety — two {cat} emails within 2 weeks can feel repetitive.")
    print()


def cmd_recycle():
    con = db()
    rows = con.execute(
        "SELECT topic_id, category, send_date, subject, evergreen FROM newsletter_meta ORDER BY send_date"
    ).fetchall()
    con.close()

    # Find the most recent send per topic
    latest = {}
    for tid, cat, date, subj, ev in rows:
        if tid not in latest or date > latest[tid][0]:
            latest[tid] = (date, subj, cat, ev)

    eligible = []
    for tid, (date, subj, cat, ev) in latest.items():
        threshold = RECYCLE_WEEKS_TIMELY if cat in TIMELY_CATEGORIES else RECYCLE_WEEKS_EVERGREEN
        w = weeks_ago(date)
        if w >= threshold:
            eligible.append((w, tid, cat, date, subj, ev))

    if not eligible:
        print(f"\n  No topics ready for recycling yet.\n")
        return

    eligible.sort(reverse=True)
    print(f"\n{'='*65}")
    print(f"  READY TO RECYCLE ({len(eligible)} topics)")
    print(f"  Evergreen threshold: {RECYCLE_WEEKS_EVERGREEN}w · Timely threshold: {RECYCLE_WEEKS_TIMELY}w")
    print(f"{'='*65}\n")
    for w, tid, cat, date, subj, ev in eligible:
        tag = "evergreen" if ev else "timely"
        print(f"  [{tid}] {CATEGORY_NAMES.get(cat, cat)} ({tag})")
        print(f"    Last sent {w:.0f} weeks ago: \"{subj}\"")
        print()


def cmd_log(args):
    def get(flag, default=""):
        try:
            i = args.index(flag)
            return args[i + 1]
        except (ValueError, IndexError):
            return default

    date     = get("--date",     datetime.now().strftime("%Y-%m-%d"))
    slot     = get("--slot")
    category = get("--category")
    topic_id = get("--topic-id")
    kernel   = get("--kernel",   "")
    subject  = get("--subject")
    lists    = get("--lists",    "practitioners-en,practitioners-fr")
    notes    = get("--notes",    "")
    timely   = "--timely" in args
    evergreen = 0 if timely else 1

    if not all([slot, category, topic_id, subject]):
        print("\nUsage: tracker.py log --slot tue|thu|sat --category A --topic-id A-07 --subject \"...\" [--date YYYY-MM-DD] [--kernel KRN-XXX] [--timely] [--notes \"...\"] [--lists \"en,fr\"]\n")
        sys.exit(1)

    con = db()
    con.execute(
        "INSERT INTO newsletter_meta (send_date, slot, category, topic_id, kernel, subject, evergreen, notes, lists) VALUES (?,?,?,?,?,?,?,?,?)",
        (date, slot, category, topic_id, kernel, subject, evergreen, notes, lists)
    )
    con.commit()
    con.close()

    print(f"\n  ✓ Logged: {date} [{slot.upper()}] {topic_id} — {subject[:50]}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "status":
        cmd_status()
    elif cmd == "history":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        cmd_history(n)
    elif cmd == "scan":
        if len(sys.argv) < 3:
            print("Usage: tracker.py scan TOPIC-ID")
            sys.exit(1)
        cmd_scan(sys.argv[2])
    elif cmd == "recycle":
        cmd_recycle()
    elif cmd == "log":
        cmd_log(sys.argv[2:])
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

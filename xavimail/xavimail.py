#!/usr/bin/env python3
"""
XaviMail — self-hosted mailing list tool

Usage:
  xavimail lists                                    List all lists with counts
  xavimail list <name>                              Show subscribers in a list
  xavimail add <email> <list> [--name "First Last"] Add subscriber to list
  xavimail remove <email> <list>                    Remove subscriber from list
  xavimail suppress <email> [--reason bounce]       Manually suppress an address
  xavimail import [--list practitioners-en]         Import from contacts.json
  xavimail send <list> <subject> <body.md>          Send campaign
               [--dry-run] [--test-to email]
  xavimail sync                                     Pull suppressions from D1
  xavimail stats                                    Send history + suppression counts
"""

import sys
import os
import argparse
from pathlib import Path

# Add the xavimail directory to path so modules resolve
sys.path.insert(0, str(Path(__file__).parent))

import config as cfg_mod
import db
import sync as sync_mod
import send as send_mod


# ── Helpers ───────────────────────────────────────────────────────────────────

def die(msg: str):
    print(f'Error: {msg}', file=sys.stderr)
    sys.exit(1)


def require_list(name: str) -> dict:
    lst = db.get_list_by_name(name)
    if not lst:
        names = [l['name'] for l in db.get_lists()]
        die(f"List '{name}' not found. Available: {', '.join(names) or '(none)'}")
    return lst


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_lists(args):
    lists = db.get_lists()
    if not lists:
        print('No lists yet. Use `xavimail import` to create and populate lists.')
        return
    print(f'{"List":<30}  {"Subscribers":>11}  {"Description"}')
    print('─' * 70)
    for l in lists:
        print(f'{l["name"]:<30}  {l["subscriber_count"]:>11}  {l["description"]}')


def cmd_list(args):
    lst = require_list(args.name)
    members = db.get_list_members(lst['id'])
    suppressions = {s['email'] for s in db.get_suppressions()}

    if not members:
        print(f'List "{args.name}" is empty.')
        return

    print(f'List: {args.name}  ({len(members)} total)')
    print()
    print(f'  {"Email":<40}  {"Name":<25}  Status')
    print('  ' + '─' * 80)
    for m in members:
        name = f"{m['first_name']} {m['last_name']}".strip() or '—'
        status = '⚠ suppressed' if m['email'] in suppressions else 'active'
        print(f'  {m["email"]:<40}  {name:<25}  {status}')

    active = len(members) - sum(1 for m in members if m['email'] in suppressions)
    print()
    print(f'Active: {active}  |  Suppressed: {len(members) - active}')


def cmd_add(args):
    email = args.email.lower().strip()
    lst = require_list(args.list)

    first_name = last_name = ''
    if args.name:
        parts = args.name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

    db.upsert_subscriber(email, first_name, last_name)
    db.add_to_list(lst['id'], email)
    print(f'✓ {email} added to {args.list}')


def cmd_remove(args):
    email = args.email.lower().strip()
    lst = require_list(args.list)
    db.remove_from_list(lst['id'], email)
    print(f'✓ {email} removed from {args.list}')


def cmd_suppress(args):
    email = args.email.lower().strip()
    reason = args.reason or 'manual'
    db.add_suppression(email, reason)
    print(f'✓ {email} suppressed (reason: {reason})')


def cmd_import(args):
    """Import practitioners from contacts.json into XaviMail lists."""
    cfg = cfg_mod.load()
    contacts_path = Path(cfg['contacts_json'])
    if not contacts_path.exists():
        die(f'contacts.json not found at {contacts_path}')

    import json
    data = json.loads(contacts_path.read_text())
    contacts = data.get('contacts', {})

    # EN list: non-french-practitioner
    # FR list: french-active + french-inactive (combined)
    lists_to_import = {
        'practitioners-en': ['non-french-practitioner'],
        'practitioners-fr': ['french-active', 'french-inactive'],
    }

    if args.list:
        if args.list not in lists_to_import:
            die(f"Unknown list '{args.list}'. Valid: {', '.join(lists_to_import)}")
        lists_to_import = {args.list: lists_to_import[args.list]}

    descriptions = {
        'practitioners-en': 'MN practitioners (English)',
        'practitioners-fr': 'Praticiens MN (Français, actifs + inactifs)',
    }

    total_added = 0
    total_skipped = 0

    for list_name, segments in lists_to_import.items():
        lst = db.get_list_by_name(list_name)
        if not lst:
            lst = db.create_list(list_name, descriptions.get(list_name, ''))
            print(f'Created list: {list_name}')

        added = skipped = 0
        for contact in contacts:
            email = (contact.get('email') or '').lower().strip()
            if not email:
                continue

            seg = contact.get('segment', '')
            if seg not in segments:
                continue

            status = contact.get('status', '')
            if status == 'unsubscribed':
                # Already unsubscribed in MailerLite — suppress them
                db.add_suppression(email, 'unsubscribe')
                skipped += 1
                continue

            name_raw = contact.get('name', '') or ''
            last_raw = contact.get('last_name', '') or ''

            # contacts.json stores full name in 'name' for some entries
            first_name = name_raw.strip()
            last_name = last_raw.strip()
            if not last_name and ' ' in first_name:
                parts = first_name.rsplit(' ', 1)
                first_name, last_name = parts[0], parts[1]

            db.upsert_subscriber(email, first_name, last_name)
            db.add_to_list(lst['id'], email)
            added += 1

        print(f'{list_name}: {added} added, {skipped} already unsubscribed (suppressed)')
        total_added += added
        total_skipped += skipped

    print()
    print(f'Import complete. Total added: {total_added}, suppressed: {total_skipped}')
    print('Run `xavimail lists` to confirm.')


def cmd_send(args):
    import send as send_mod

    if not Path(args.body).expanduser().exists():
        die(f'Body file not found: {args.body}')

    result = send_mod.run_campaign(
        list_name=args.list,
        subject=args.subject,
        body_file=args.body,
        dry_run=args.dry_run,
        test_to=args.test_to,
    )
    return result


def cmd_sync(args):
    print('Syncing suppressions from D1...')
    try:
        result = sync_mod.pull()
        print(f'✓ Sync complete. Remote: {result["remote"]}  |  New local: {result["added"]}  |  Total suppressed: {result["total"]}')
    except RuntimeError as e:
        die(str(e))


def cmd_stats(args):
    sends = db.get_sends(limit=20)
    suppressions = db.get_suppressions()

    print(f'Suppressions: {len(suppressions)} total')
    if suppressions:
        from collections import Counter
        by_reason = Counter(s['reason'] for s in suppressions)
        for reason, count in sorted(by_reason.items()):
            print(f'  {reason}: {count}')

    print()
    if not sends:
        print('No sends yet.')
        return

    print(f'Recent sends (last {len(sends)}):')
    print()
    print(f'  {"Date":<20}  {"List":<22}  {"Sent":>6}  {"Skipped":>8}  Subject')
    print('  ' + '─' * 90)
    for s in sends:
        date = s['sent_at'][:16].replace('T', ' ')
        print(f'  {date:<20}  {s["list_name"]:<22}  {s["recipient_count"]:>6}  {s["skipped_count"]:>8}  {s["subject"]}')


# ── Argument parser ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='xavimail',
        description='XaviMail — self-hosted mailing list for MN practitioners',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', metavar='command')

    # lists
    sub.add_parser('lists', help='Show all lists with subscriber counts')

    # list <name>
    p_list = sub.add_parser('list', help='Show subscribers in a list')
    p_list.add_argument('name', help='List name')

    # add <email> <list>
    p_add = sub.add_parser('add', help='Add subscriber to a list')
    p_add.add_argument('email')
    p_add.add_argument('list')
    p_add.add_argument('--name', default='', help='Full name, e.g. "Marie Dupont"')

    # remove <email> <list>
    p_rem = sub.add_parser('remove', help='Remove subscriber from a list')
    p_rem.add_argument('email')
    p_rem.add_argument('list')

    # suppress <email>
    p_sup = sub.add_parser('suppress', help='Manually suppress an email address')
    p_sup.add_argument('email')
    p_sup.add_argument('--reason', default='manual', help='Reason: manual, bounce, complaint')

    # import
    p_imp = sub.add_parser('import', help='Import from contacts.json')
    p_imp.add_argument('--list', default=None, help='Import only this list (default: all)')

    # send
    p_send = sub.add_parser('send', help='Send a campaign')
    p_send.add_argument('list',    help='List name, e.g. practitioners-en')
    p_send.add_argument('subject', help='Email subject line')
    p_send.add_argument('body',    help='Path to .md file with email body')
    p_send.add_argument('--dry-run',  action='store_true', help='Preview only, no sends')
    p_send.add_argument('--test-to',  default=None,  metavar='EMAIL',
                        help='Send only to this address (test mode)')

    # sync
    sub.add_parser('sync', help='Pull unsubscribes/bounces from D1 into local DB')

    # stats
    sub.add_parser('stats', help='Send history and suppression counts')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        'lists':    cmd_lists,
        'list':     cmd_list,
        'add':      cmd_add,
        'remove':   cmd_remove,
        'suppress': cmd_suppress,
        'import':   cmd_import,
        'send':     cmd_send,
        'sync':     cmd_sync,
        'stats':    cmd_stats,
    }

    try:
        dispatch[args.command](args)
    except KeyboardInterrupt:
        print('\nAborted.')
        sys.exit(1)
    except Exception as e:
        die(str(e))


if __name__ == '__main__':
    main()

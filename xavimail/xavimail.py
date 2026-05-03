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
import datetime
import re
from pathlib import Path

# Add the xavimail directory to path so modules resolve
sys.path.insert(0, str(Path(__file__).parent))

import config as cfg_mod
import db
import render as render_mod
import sync as sync_mod
import send as send_mod
import sequence as seq_mod
from scheduler.cli import (
    cmd_schedule_add, cmd_schedule_list, cmd_schedule_cancel,
    cmd_schedule_run, cmd_schedule_confirm, cmd_schedule_daemon,
)
from scheduler.launchd import install_daemon, uninstall_daemon


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

def cmd_help(args):
    print("""
XaviMail — self-hosted email tool
Sends via AWS SES · Lists in SQLite · Unsubscribes/bounces via Cloudflare D1

━━━ LIST MANAGEMENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  xavimail lists
      Show all lists with subscriber counts.

  xavimail list <name>
      Show all subscribers in a list with status.

  xavimail list <name> --attribs
      Show subscribers with country, cert level, test count instead of status.

  xavimail add <email> <list> [--name "First Last"]
      Add a subscriber to a list.

  xavimail remove <email> <list>
      Remove a subscriber from a list (hard delete).

  xavimail suppress <email> [--reason bounce|complaint|manual]
      Globally suppress an address (excluded from all future sends).

━━━ SENDING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  xavimail preview <body.md>
      Render email to HTML and open in browser. No send.

  xavimail test <list> "<subject>" <body.md>
      Send to yourself only (steven@multiplenatures.com). Inbox check.
      Tracking (open/click) is live so you can verify it works.

  xavimail send <list> "<subject>" <body.md>
      Send campaign to all active members of a list.

  xavimail send <list> "<subject>" <body.md> --dry-run
      Preview recipient list and rendered email. No send.

  xavimail send <list> "<subject>" <body.md> --test-to <email>
      Send to one specific address only.

  Standard send workflow:
      xavimail sync
      xavimail preview email.md
      xavimail test practitioners-en "Subject" email.md
      xavimail send practitioners-en "Subject" email.md

━━━ SEQUENCES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  xavimail sequence list
      List all sequences with step count and progress.

  xavimail sequence status <name>
      Step-by-step send history for a sequence.

  xavimail sequence next <name> [--list en|fr]
      Dry run of the next unsent step.

  xavimail sequence send <name> [--step N] [--list en|fr] [--dry-run] [--confirm]
      Send the next step (shows dry run first, prompts y/N).

━━━ DATA & SYNC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  xavimail sync
      Pull suppressions + tracking events from Cloudflare D1 into local DB.
      Run before every send and after test sends to see open/click events.

  xavimail import [--list practitioners-en|practitioners-fr]
      Import from contacts.json (full re-import, idempotent).

  xavimail import --sync [--list ...]
      Diff-based import: adds new contacts, updates attribs, skips existing.

  xavimail stats
      Send history (last 20) and suppression counts by reason.

━━━ EMAIL FILE FORMAT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  emails/my-email.md:

    ---
    subject: Your subject line here
    ---
    Hi {first_name},

    Body text here. [Links](https://example.com) are tracked automatically.

    Steven

  Variables: {first_name}  {last_name}  {email}  {unsubscribe_url}
  See EMAIL-DESIGN-SPEC.md for full formatting guide.

━━━ FILES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Config:     ~/.xavimail/config.json
  Database:   ~/.xavimail/xavimail.db
  Sequences:  sequences/*.yaml
  Emails:     emails/**/*.md
  Design:     EMAIL-DESIGN-SPEC.md
""")


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
    import json as _json

    lst = require_list(args.name)
    members = db.get_list_members(lst['id'])
    suppressions = {s['email']: s['reason'] for s in db.get_suppressions()}

    if not members:
        print(f'List "{args.name}" is empty.')
        return

    show_attribs = getattr(args, 'attribs', False)
    print(f'List: {args.name}  ({len(members)} total)')
    print()

    if show_attribs:
        print(f'  {"Email":<40}  {"Name":<25}  {"Attribs"}')
        print('  ' + '─' * 100)
        for m in members:
            name = f"{m['first_name']} {m['last_name']}".strip() or '—'
            try:
                attribs = _json.loads(m.get('attribs') or '{}')
            except Exception:
                attribs = {}
            parts = []
            if attribs.get('country'):    parts.append(attribs['country'])
            if attribs.get('cert_level'): parts.append(attribs['cert_level'])
            if attribs.get('mntest_count'): parts.append(f"{attribs['mntest_count']} tests")
            if attribs.get('segment'):    parts.append(attribs['segment'])
            attrib_str = '  ·  '.join(parts) if parts else '—'
            print(f'  {m["email"]:<40}  {name:<25}  {attrib_str}')
    else:
        print(f'  {"Email":<40}  {"Name":<25}  Status')
        print('  ' + '─' * 80)
        for m in members:
            name = f"{m['first_name']} {m['last_name']}".strip() or '—'
            if m['email'] in suppressions:
                reason = suppressions[m['email']]
                status = f'⚠ {reason} (global)'
            elif m.get('list_status', 'active') != 'active':
                status = f'⚠ {m["list_status"]} (this list)'
            elif m.get('subscriber_status', 'active') != 'active':
                status = f'⚠ {m["subscriber_status"]}'
            else:
                status = 'active'
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


def _extract_contact_attribs(contact: dict) -> dict:
    attribs = {}
    if contact.get('country'):  attribs['country']  = contact['country']
    if contact.get('category'): attribs['category'] = contact['category']
    if contact.get('segment'):  attribs['segment']  = contact['segment']
    pd = contact.get('practitioner_data') or {}
    if pd.get('cert_level'):         attribs['cert_level']  = pd['cert_level']
    if pd.get('mntest_count_total'): attribs['mntest_count'] = pd['mntest_count_total']
    return attribs


def _parse_contact_name(contact: dict) -> tuple[str, str]:
    name_raw = (contact.get('name') or '').strip()
    last_raw = (contact.get('last_name') or '').strip()
    first_name, last_name = name_raw, last_raw
    if not last_name and ' ' in first_name:
        parts = first_name.rsplit(' ', 1)
        first_name, last_name = parts[0], parts[1]
    return first_name, last_name


def cmd_import(args):
    """Import practitioners from contacts.json into XaviMail lists."""
    import json as _json

    cfg = cfg_mod.load()
    contacts_path = Path(cfg['contacts_json'])
    if not contacts_path.exists():
        die(f'contacts.json not found at {contacts_path}')

    data = _json.loads(contacts_path.read_text())
    contacts = data.get('contacts', data) if isinstance(data, dict) else data

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

    is_sync = getattr(args, 'sync', False)
    total_added = total_updated = total_skipped = total_suppressed = 0

    # Pre-load current state for diff (sync mode)
    existing_emails = set()
    existing_list_emails = {}
    suppressed_emails = {s['email'] for s in db.get_suppressions()}
    if is_sync:
        for sub in db._db().execute('SELECT email FROM subscribers').fetchall():
            existing_emails.add(sub[0])

    for list_name, segments in lists_to_import.items():
        lst = db.get_list_by_name(list_name)
        if not lst:
            lst = db.create_list(list_name, descriptions.get(list_name, ''))
            print(f'Created list: {list_name}')

        if is_sync:
            members = {m['email'] for m in db.get_list_members(lst['id'])}
            existing_list_emails[list_name] = members

        added = updated = skipped = suppressed = 0
        for contact in contacts:
            email = (contact.get('email') or '').lower().strip()
            if not email:
                continue

            seg = contact.get('segment', '')
            if seg not in segments:
                continue

            status = contact.get('status', '')

            # Handle suppressible statuses
            if status in ('unsubscribed', 'bounced', 'junk'):
                reason = {'unsubscribed': 'unsubscribe', 'bounced': 'bounce', 'junk': 'complaint'}.get(status, 'unsubscribe')
                if email not in suppressed_emails:
                    db.add_suppression(email, reason)
                    suppressed_emails.add(email)
                    suppressed += 1
                else:
                    skipped += 1
                continue

            # Skip already-suppressed
            if email in suppressed_emails:
                skipped += 1
                continue

            first_name, last_name = _parse_contact_name(contact)
            attribs = _extract_contact_attribs(contact)

            if is_sync and email in existing_emails:
                # Update attribs only — don't clobber names if already set
                db.upsert_subscriber(email, first_name, last_name, status='active', attribs=attribs)
                if list_name in existing_list_emails and email not in existing_list_emails[list_name]:
                    db.add_to_list(lst['id'], email)
                    added += 1
                else:
                    updated += 1
            else:
                db.upsert_subscriber(email, first_name, last_name, status='active', attribs=attribs)
                db.add_to_list(lst['id'], email)
                if is_sync:
                    existing_emails.add(email)
                added += 1

        if is_sync:
            print(f'{list_name}: {added} new, {updated} updated, {skipped} skipped, {suppressed} newly suppressed')
        else:
            print(f'{list_name}: {added} added, {skipped + suppressed} skipped/suppressed')
        total_added += added
        total_updated += updated
        total_skipped += skipped
        total_suppressed += suppressed

    print()
    if is_sync:
        print(f'Sync complete. New: {total_added}  Updated: {total_updated}  Suppressed: {total_suppressed}  Skipped: {total_skipped}')
    else:
        print(f'Import complete. Total added: {total_added}, suppressed: {total_suppressed}')
    print('Run `xavimail lists` to confirm.')


def cmd_preview(args):
    """Render email to HTML and open in browser. No send."""
    import json, subprocess
    cfg = cfg_mod.load()
    body_path = Path(args.body).expanduser()
    if not body_path.exists():
        die(f'Body file not found: {args.body}')

    # Use a realistic preview context
    context = {
        'first_name': 'Steven',
        'last_name': '',
        'email': cfg['from_email'],
        'unsubscribe_url': f"{cfg['unsubscribe_base']}?email={cfg['from_email']}&sig=preview",
    }
    _, html = render_mod.render(body_path, context)
    out = Path('/tmp/xavimail-preview.html')
    out.write_text(html, encoding='utf-8')
    subprocess.run(['open', str(out)])
    print(f'✓ Preview opened in browser ({out})')


def cmd_test(args):
    """Send email to yourself only. Quick inbox check before real send."""
    cfg = cfg_mod.load()
    body_path = Path(args.body).expanduser()
    if not body_path.exists():
        die(f'Body file not found: {args.body}')

    to = cfg['from_email']
    result = send_mod.run_campaign(
        list_name=args.list,
        subject=args.subject,
        body_file=str(body_path),
        dry_run=False,
        test_to=to,
    )
    send_id = result.get('send_id')
    if send_id:
        print(f'  send_id={send_id} — run `xavimail sync` after opening to see tracking events.')


def cmd_send(args):
    import send as send_mod

    if not Path(args.body).expanduser().exists():
        die(f'Body file not found: {args.body}')

    # Enforce date+slug filename convention: YYYY-MM-DD-*.md
    body_filename = Path(args.body).name
    if not re.match(r'^\d{4}-\d{2}-\d{2}-.+\.md$', body_filename):
        today = datetime.date.today().isoformat()
        slug = re.sub(r'[^a-z0-9]+', '-', body_filename.replace('.md', '').lower()).strip('-')
        die(f'Email file must be named YYYY-MM-DD-slug.md\n'
            f'  Got:      {body_filename}\n'
            f'  Suggest:  {today}-{slug}.md')

    is_live = not args.dry_run and not args.test_to

    # Guard: full list sends require --live flag + interactive confirmation
    if is_live and not args.live:
        print()
        print('  ✋  LIVE SEND BLOCKED')
        print(f'     List:    {args.list}')
        print(f'     Subject: {args.subject}')
        print()
        print('  To send to the real list you must add --live and confirm.')
        print('  To test first:  xavimail send <list> <subject> <body> --test-to you@email.com')
        print('  To preview:     xavimail send <list> <subject> <body> --dry-run')
        print()
        sys.exit(1)

    if is_live and args.live:
        # Layer 1: duplicate send guard
        recent = db.recent_send(args.list, args.subject, hours=24)
        if recent and not getattr(args, 'force', False):
            print()
            print('  🛑  DUPLICATE SEND BLOCKED')
            print(f'     This subject was already sent to {args.list} on {recent["sent_at"]} ({recent["recipient_count"]} recipients).')
            print(f'     Add --force to override.')
            print()
            sys.exit(1)

        # Count recipients before asking
        conn = db._db()
        count = conn.execute(
            "SELECT COUNT(*) FROM list_members lm "
            "JOIN lists l ON l.id = lm.list_id "
            "JOIN subscribers s ON s.email = lm.email "
            "LEFT JOIN suppressions sup ON sup.email = lm.email "
            "WHERE l.name = ? AND s.status = 'active' AND lm.status = 'active' AND sup.email IS NULL",
            (args.list,)
        ).fetchone()[0]
        print()
        print(f'  ⚠️   LIVE SEND — {count} recipients on {args.list}')
        print(f'  Subject: {args.subject}')
        print()
        confirm = input(f'  Type the list name to confirm: ').strip()
        if confirm != args.list:
            print('  Cancelled — list name did not match.')
            print()
            sys.exit(1)
        print()

    # Auto-prefix [TEST] on test sends (also enforced in run_campaign — belt + suspenders)
    subject = args.subject
    if args.test_to and not subject.lstrip().upper().startswith('[TEST]'):
        subject = f'[TEST] {subject}'

    result = send_mod.run_campaign(
        list_name=args.list,
        subject=subject,
        body_file=args.body,
        dry_run=args.dry_run,
        test_to=args.test_to,
    )
    return result


def cmd_sync(args):
    print('Syncing from D1...')
    try:
        result = sync_mod.pull()
        print(f'✓ Suppressions — remote: {result["remote"]}  new: {result["added"]}  total: {result["total"]}')
        print(f'✓ Events       — new: {result["new_events"]}')
    except RuntimeError as e:
        die(str(e))


def cmd_sequence(args):
    sub = args.seq_command

    if sub == 'list':
        seqs = seq_mod.list_sequences()
        if not seqs:
            print('No sequences yet. Add a .yaml file to sequences/.')
            return
        for s in seqs:
            name = s.get('name', '?')
            desc = s.get('description', '')
            nxt = seq_mod.next_step(s)
            nxt_label = f'next: step {nxt}' if nxt else 'complete'
            steps = len(s.get('steps', []))
            print(f'{name:<35}  {steps} steps  {nxt_label:<18}  {desc}')

    elif sub == 'status':
        seq = seq_mod.load_sequence(args.name)
        rows = seq_mod.sequence_status(seq)
        print(f'Sequence: {seq["name"]}')
        if seq.get('description'):
            print(f'          {seq["description"]}')
        print()
        last_step = None
        for r in rows:
            if r['num'] != last_step:
                print(f'  Step {r["num"]}')
                last_step = r['num']
            status = f'✓ sent {r["sent_at"][:10]}' if r['sent_at'] else '○ pending'
            subject = r['subject'] or '(no subject in frontmatter)'
            print(f'    [{r["alias"]}] {r["list_name"]:<25}  {status:<20}  {subject}')

    elif sub == 'next':
        seq = seq_mod.load_sequence(args.name)
        nxt = seq_mod.next_step(seq)
        if nxt is None:
            print(f'Sequence "{args.name}" is complete — all steps sent.')
            return
        print(f'Next unsent step: {nxt}')
        print()
        seq_mod.send_step(seq, nxt, list_filter=args.list, dry_run=True)

    elif sub == 'send':
        seq = seq_mod.load_sequence(args.name)

        step_num = args.step
        if step_num is None:
            step_num = seq_mod.next_step(seq)
            if step_num is None:
                print(f'Sequence "{args.name}" is complete — all steps sent.')
                print('Use --step N to force-send a specific step.')
                return

        # Always show dry run first
        print(f'─── Dry run: sequence={args.name}  step={step_num} ───')
        seq_mod.send_step(seq, step_num, list_filter=args.list, dry_run=True)
        print()

        if args.dry_run:
            return

        # Confirmation prompt
        if not args.confirm:
            try:
                answer = input('Send for real? [y/N] ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print('\nAborted.')
                return
            if answer != 'y':
                print('Aborted.')
                return

        print()
        print(f'─── Sending: sequence={args.name}  step={step_num} ───')
        seq_mod.send_step(seq, step_num, list_filter=args.list, dry_run=False)


def cmd_schedule(args):
    sub = getattr(args, 'sched_command', None)
    if sub == 'add':
        cmd_schedule_add(args)
    elif sub == 'list':
        cmd_schedule_list(args)
    elif sub == 'cancel':
        cmd_schedule_cancel(args)
    elif sub == 'run':
        cmd_schedule_run(args)
    elif sub == 'confirm':
        cmd_schedule_confirm(args)
    elif sub == 'daemon':
        cmd_schedule_daemon(args)
    elif sub == 'install-daemon':
        install_daemon()
    elif sub == 'uninstall-daemon':
        uninstall_daemon()
    else:
        print('Usage: xavimail schedule <add|list|cancel|run|confirm|daemon|install-daemon|uninstall-daemon>')


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
    print(f'  {"Date":<20}  {"List":<22}  {"Sent":>6}  {"Skipped":>8}  {"Sequence/Step":<18}  Subject')
    print('  ' + '─' * 110)
    for s in sends:
        date = s['sent_at'][:16].replace('T', ' ')
        seq_label = f'{s["sequence"]} #{s["step_num"]}' if s.get('sequence') else '—'
        print(f'  {date:<20}  {s["list_name"]:<22}  {s["recipient_count"]:>6}  {s["skipped_count"]:>8}  {seq_label:<18}  {s["subject"]}')


# ── Argument parser ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='xavimail',
        description='XaviMail — self-hosted mailing list for MN practitioners',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', metavar='command')

    # help
    sub.add_parser('help', help='Show full command reference with examples')

    # lists
    sub.add_parser('lists', help='Show all lists with subscriber counts')

    # list <name>
    p_list = sub.add_parser('list', help='Show subscribers in a list')
    p_list.add_argument('name', help='List name')
    p_list.add_argument('--attribs', action='store_true', help='Show attribs (country, cert level, test count) instead of status')

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
    p_imp.add_argument('--list',  default=None,  help='Import only this list (default: all)')
    p_imp.add_argument('--sync',  action='store_true', help='Diff-based: add new, update attribs, skip existing')

    # preview
    p_prev = sub.add_parser('preview', help='Render email to browser — no send')
    p_prev.add_argument('body', help='Path to .md email file')

    # test
    p_test = sub.add_parser('test', help='Send to yourself only (inbox check)')
    p_test.add_argument('list',    help='List name (for context/subject rendering)')
    p_test.add_argument('subject', help='Email subject line')
    p_test.add_argument('body',    help='Path to .md email file')

    # send
    p_send = sub.add_parser('send', help='Send a campaign')
    p_send.add_argument('list',    help='List name, e.g. practitioners-en')
    p_send.add_argument('subject', help='Email subject line')
    p_send.add_argument('body',    help='Path to .md file with email body')
    p_send.add_argument('--dry-run',  action='store_true', help='Preview only, no sends')
    p_send.add_argument('--test-to',  default=None,  metavar='EMAIL',
                        help='Send only to this address (test mode)')
    p_send.add_argument('--live',     action='store_true',
                        help='Required for full list sends — triggers confirmation prompt')
    p_send.add_argument('--force',    action='store_true',
                        help='Override duplicate send guard (use with caution)')

    # sync
    sub.add_parser('sync', help='Pull unsubscribes/bounces from D1 into local DB')

    # sequence
    p_seq = sub.add_parser('sequence', help='Manage and send sequences')
    seq_sub = p_seq.add_subparsers(dest='seq_command', metavar='subcommand')

    seq_sub.add_parser('list', help='List all sequences with progress')

    p_sstat = seq_sub.add_parser('status', help='Step-by-step send history for a sequence')
    p_sstat.add_argument('name', help='Sequence name')

    p_snext = seq_sub.add_parser('next', help='Dry run of the next unsent step')
    p_snext.add_argument('name', help='Sequence name')
    p_snext.add_argument('--list', default=None, metavar='ALIAS', help='en or fr only')

    p_ssend = seq_sub.add_parser('send', help='Send the next step (or a specific step)')
    p_ssend.add_argument('name', help='Sequence name')
    p_ssend.add_argument('--step',    type=int, default=None, help='Override which step to send')
    p_ssend.add_argument('--list',    default=None, metavar='ALIAS', help='en or fr only')
    p_ssend.add_argument('--dry-run', action='store_true', help='Preview only')
    p_ssend.add_argument('--confirm', action='store_true', help='Skip the y/N prompt')

    # schedule
    p_sched = sub.add_parser('schedule', help='Schedule future sends')
    sched_sub = p_sched.add_subparsers(dest='sched_command', metavar='subcommand')

    p_sadd = sched_sub.add_parser('add', help='Schedule a send')
    p_sadd.add_argument('list',    help='List name, e.g. practitioners-en')
    p_sadd.add_argument('subject', help='Email subject line')
    p_sadd.add_argument('draft',   nargs='?', default=None,
                        help='Path to .md email file (omit to use latest draft in drafts/)')
    p_sadd.add_argument('--at',    required=True, metavar='DATETIME',
                        help='Send time, e.g. "2026-04-25 14:30"')
    p_sadd.add_argument('--tz',    default='Asia/Phnom_Penh', metavar='TZ',
                        help='Timezone (default: Asia/Phnom_Penh)')
    p_sadd.add_argument('--allow-multi', action='store_true', dest='allow_multi',
                        help='Override one-send-per-list-per-day guard (rare)')

    sched_sub.add_parser('list', help='Show all scheduled jobs')

    p_scancel = sched_sub.add_parser('cancel', help='Cancel a pending job')
    p_scancel.add_argument('job_id', help='Job ID from schedule list')

    p_srun = sched_sub.add_parser('run', help='Force-run a job now (recovery)')
    p_srun.add_argument('job_id', help='Job ID from schedule list')

    p_sconfirm = sched_sub.add_parser('confirm', help='Confirm a job so the daemon will fire it')
    p_sconfirm.add_argument('job_id', help='Job ID from schedule list')

    sched_sub.add_parser('daemon', help='Start the scheduler daemon (blocking)')
    sched_sub.add_parser('install-daemon', help='Install macOS LaunchAgent (auto-start)')
    sched_sub.add_parser('uninstall-daemon', help='Remove LaunchAgent and stop daemon')

    # stats
    sub.add_parser('stats', help='Send history and suppression counts')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        'help':     cmd_help,
        'lists':    cmd_lists,
        'list':     cmd_list,
        'add':      cmd_add,
        'remove':   cmd_remove,
        'suppress': cmd_suppress,
        'import':   cmd_import,
        'preview':  cmd_preview,
        'test':     cmd_test,
        'send':     cmd_send,
        'sync':     cmd_sync,
        'sequence': cmd_sequence,
        'schedule': cmd_schedule,
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

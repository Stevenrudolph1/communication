"""send.py — SES email sender for XaviMail"""

import datetime
import hmac
import hashlib
import time
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import boto3
from botocore.config import Config

import config as cfg_mod
import db
import render as render_mod


def unsub_sig(email: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for unsubscribe URL (matches Worker verification)."""
    return hmac.new(
        secret.encode('utf-8'),
        email.lower().encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def unsub_url(email: str, cfg: dict) -> str:
    sig = unsub_sig(email, cfg['mailer_secret'])
    params = urllib.parse.urlencode({'email': email.lower(), 'sig': sig})
    return f"{cfg['unsubscribe_base']}?{params}"


def _ses_client(cfg: dict):
    return boto3.client(
        'ses',
        region_name=cfg['aws_region'],
        aws_access_key_id=cfg['aws_access_key_id'],
        aws_secret_access_key=cfg['aws_secret_access_key'],
        config=Config(retries={'max_attempts': 3}),
    )


def send_one(
    to_email: str,
    subject: str,
    plain_text: str,
    html_text: str,
    unsub_link: str,
    cfg: dict,
    ses=None,
) -> str:
    """Send a single email. Returns the SES MessageId."""
    if ses is None:
        ses = _ses_client(cfg)

    from_addr = f"{cfg['from_name']} <{cfg['from_email']}>"

    msg = MIMEMultipart('alternative')
    msg['From']    = from_addr
    msg['To']      = to_email
    msg['Subject'] = subject
    msg['List-Unsubscribe'] = f'<{unsub_link}>'
    msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'

    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_text,  'html',  'utf-8'))

    resp = ses.send_raw_email(
        Source=from_addr,
        Destinations=[to_email],
        RawMessage={'Data': msg.as_bytes()},
    )
    return resp['MessageId']


def send_campaign_copy(
    subject: str,
    plain_text: str,
    html_text: str,
    list_name: str,
    sent_count: int,
    cfg: dict,
    ses=None,
) -> None:
    """Send a single campaign copy to cc_always recipients after a live send."""
    copy_addrs = cfg.get('cc_always', [])
    if not copy_addrs:
        return
    if ses is None:
        ses = _ses_client(cfg)

    from_addr = f"{cfg['from_name']} <{cfg['from_email']}>"
    copy_subject = f"[Campaign copy — {list_name}, {sent_count} sent] {subject}"

    msg = MIMEMultipart('alternative')
    msg['From']    = from_addr
    msg['To']      = ', '.join(copy_addrs)
    msg['Subject'] = copy_subject

    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_text,  'html',  'utf-8'))

    ses.send_raw_email(
        Source=from_addr,
        Destinations=copy_addrs,
        RawMessage={'Data': msg.as_bytes()},
    )


def run_campaign(
    list_name: str,
    subject: str,
    body_file: str,
    dry_run: bool = False,
    test_to: str = None,
    sequence: str = None,
    step_num: int = None,
) -> dict:
    """
    Send an email to all active members of a list.

    dry_run=True  — prints who would receive it, no sends.
    test_to=email — sends ONLY to this address (uses first real recipient's name/context).

    Returns summary dict: {sent, skipped, suppressed, errors}
    """
    cfg = cfg_mod.load()

    lst = db.get_list_by_name(list_name)
    if not lst:
        raise ValueError(f"List '{list_name}' not found. Run 'xavimail lists' to see available lists.")

    if test_to:
        # Single test send — log it so tracking works in the test email
        u_url = unsub_url(test_to, cfg)
        ctx = {
            'first_name': 'Steven',
            'last_name': '',
            'email': test_to,
            'unsubscribe_url': u_url,
        }
        if dry_run:
            plain, _ = render_mod.render(body_file, ctx)
            print(f'[DRY RUN] Would send to: {test_to}')
            print(f'Subject: {subject}')
            print('─' * 60)
            print(plain[:800])
            return {'sent': 0, 'skipped': 0, 'suppressed': 0, 'errors': 0}
        test_send_id = db.log_send(
            list_name=list_name, subject=subject, body_file=body_file,
            recipient_count=1, skipped_count=0,
            sequence=sequence, step_num=step_num,
        )
        plain, html = render_mod.render(
            body_file, ctx,
            send_id=test_send_id,
            api_base=cfg.get('api_base'),
            mailer_secret=cfg.get('mailer_secret'),
        )
        print(f'Sending test to {test_to}...')
        ses = _ses_client(cfg)
        msg_id = send_one(test_to, subject, plain, html, u_url, cfg, ses)
        db.log_send_item(test_send_id, test_to, msg_id, 'sent')
        print(f'✓ Test sent. MessageId: {msg_id}')
        return {'sent': 1, 'skipped': 0, 'suppressed': 0, 'errors': 0, 'send_id': test_send_id}

    recipients = db.get_active_recipients(lst['id'])
    all_members = db.get_list_members(lst['id'])
    suppressed_count = len(all_members) - len(recipients)

    if not recipients:
        print(f'No active recipients in list "{list_name}" (all suppressed or empty).')
        return {'sent': 0, 'skipped': 0, 'suppressed': suppressed_count, 'errors': 0}

    if dry_run:
        print(f'[DRY RUN] List: {list_name}')
        print(f'Subject: {subject}')
        print(f'Recipients: {len(recipients)}  |  Suppressed/skipped: {suppressed_count}')
        print()
        print('Would send to:')
        for r in recipients:
            name = f"{r['first_name']} {r['last_name']}".strip() or '(no name)'
            print(f'  {r["email"]}  ({name})')
        print()
        # Show a rendered preview using first recipient
        r0 = recipients[0]
        u_url = unsub_url(r0['email'], cfg)
        ctx = {
            'first_name': r0['first_name'],
            'last_name': r0['last_name'],
            'email': r0['email'],
            'unsubscribe_url': u_url,
        }
        plain, _ = render_mod.render(body_file, ctx)
        print('── Preview (first recipient) ──')
        print(plain[:1000])
        return {'sent': 0, 'skipped': 0, 'suppressed': suppressed_count, 'errors': 0}

    # Real send
    send_id = db.log_send(
        list_name=list_name,
        subject=subject,
        body_file=body_file,
        recipient_count=len(recipients),
        skipped_count=suppressed_count,
        sequence=sequence,
        step_num=step_num,
    )

    ses = _ses_client(cfg)
    delay = cfg.get('send_delay_seconds', 0.1)
    sent = skipped = errors = 0

    print(f'Sending "{subject}" to {len(recipients)} recipients in "{list_name}"...')
    print(f'(Suppressed: {suppressed_count})')
    print()

    for i, r in enumerate(recipients, 1):
        # Layer 2: per-recipient dedup — skip if already received in last 24h
        if db.already_received(list_name, subject, r['email'], hours=24):
            skipped += 1
            print(f'  [{i}/{len(recipients)}] ⏭ {r["email"]}  (already received)')
            continue

        u_url = unsub_url(r['email'], cfg)
        ctx = {
            'first_name': r['first_name'],
            'last_name': r['last_name'],
            'email': r['email'],
            'unsubscribe_url': u_url,
        }
        try:
            plain, html = render_mod.render(
                body_file, ctx,
                send_id=send_id,
                api_base=cfg.get('api_base'),
                mailer_secret=cfg.get('mailer_secret'),
            )
            msg_id = send_one(r['email'], subject, plain, html, u_url, cfg, ses)
            db.log_send_item(send_id, r['email'], msg_id, 'sent')
            sent += 1
            print(f'  [{i}/{len(recipients)}] ✓ {r["email"]}')
        except Exception as e:
            db.log_send_item(send_id, r['email'], '', 'error')
            errors += 1
            print(f'  [{i}/{len(recipients)}] ✗ {r["email"]}  — {e}')

        if i < len(recipients):
            time.sleep(delay)

    print()
    print(f'Done. Sent: {sent}  |  Errors: {errors}  |  Suppressed: {suppressed_count}')

    # Append to send register
    if sent > 0:
        register = Path(__file__).parent / 'emails' / 'SEND-REGISTER.md'
        date = datetime.date.today().isoformat()
        row = f'| {date} | {list_name} | {sent} | {subject} | {body_file} |\n'
        with open(register, 'a') as f:
            f.write(row)

    # Send one practitioner-style copy to each review address
    for copy_email in cfg.get('send_copy_to', []):
        try:
            u_url = unsub_url(copy_email, cfg)
            ctx = {'first_name': 'Steven', 'last_name': '', 'email': copy_email, 'unsubscribe_url': u_url}
            plain, html = render_mod.render(body_file, ctx)
            msg_id = send_one(copy_email, subject, plain, html, u_url, cfg, ses)
            print(f'Copy → {copy_email}')
        except Exception as e:
            print(f'Copy failed → {copy_email}: {e}')

    return {'sent': sent, 'skipped': skipped, 'suppressed': suppressed_count, 'errors': errors}

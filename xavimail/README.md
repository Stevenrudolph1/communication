# XaviMail

Self-hosted mailing list tool. Replaces MailerLite for MN practitioner campaigns.

## Architecture

- **Sending:** boto3 → AWS SES (`steven@multiplenatures.com`)
- **Subscribers:** local SQLite (`~/.xavimail/xavimail.db`)
- **Suppressions (unsubscribes + bounces):** Cloudflare D1 via `api.xavigate.com/mailer/*`
- **Bounce handling:** SES → SNS topic → `/mailer/bounce` Worker → D1 → local sync

## Quick Reference

```bash
xavimail lists                                          # all lists + counts
xavimail list practitioners-en                          # subscribers in a list
xavimail add email@example.com practitioners-en --name "First Last"
xavimail remove email@example.com practitioners-en
xavimail suppress email@example.com --reason bounce     # manual suppression

xavimail import                                         # import from contacts.json (EN + FR)
xavimail import --list practitioners-en                 # import one list only

xavimail send practitioners-en "Subject" email.md --dry-run
xavimail send practitioners-en "Subject" email.md --test-to steven@multiplenatures.com
xavimail send practitioners-en "Subject" email.md      # real send

xavimail sync                                           # pull unsubscribes/bounces from D1
xavimail stats                                          # send history + suppression counts
```

## Scheduling — Safeguards (post-2026-04-28 incident)

The scheduler has **four layers of protection** against accidental duplicate or premature sends. All run automatically; do not disable.

### Layer 1 — schedule-time guard
At `xavimail schedule add`, refuses to add a job if the same list already has a job scheduled on the same local day (any subject, any status except cancelled/failed).
- Override: `--allow-multi`. Use rarely; requires conscious choice.

### Layer 2 — fire-time guard (per-list cooldown)
At fire time, the daemon refuses to deliver if the list received any send within the last **20 hours**. Job marked `failed` with cooldown reason; TG alert sent.
- Override: `xavimail schedule run <id>` (only after manual review).

### Layer 3 — confirmation TTL
Confirmations expire after **12 hours**. A job confirmed long before its fire time will be auto-blocked and require re-confirmation.
- Practitioner jobs also require a matching `[TEST]` send for the same list and subject within the previous **24 hours** before `xavimail schedule confirm <job_id>` will proceed.
- Reason: prevents the "schedule + confirm at midnight, fire at 7am with no re-check" pattern.

### Layer 4 — morning digest
Cron at 6am local sends a Telegram message listing the next 24h queue. Flags duplicate-day jobs (`⚠ DUPLICATE DAY`), unconfirmed jobs (`⛔ UNCONFIRMED`), and stale confirmations (`⚠ STALE`).
- Cron: `0 6 * * *` → `python3 -m scheduler.digest`
- Manual run: `cd /Users/stevenrudolph/Projects/communication/xavimail && /opt/homebrew/bin/python3 -m scheduler.digest --stdout`

### Standard scheduling workflow

```bash
# 1. Test-to yourself first (never trust an untested draft)
xavimail send practitioners-en "Subject" draft.md --test-to steven@multiplenatures.com

# 2. Schedule (does not require confirmation yet)
xavimail schedule add practitioners-en "Subject" draft.md \
    --at "2026-05-02 09:00" --tz Asia/Phnom_Penh

# 3. Morning of (within 12h of fire time): confirm
# Requires the matching [TEST] send above within the last 24h.
xavimail schedule confirm <job_id>
# → daemon fires automatically at the scheduled time
```

### TG notification channel

- Bot token: `~/.secrets/xavigate-debug-bot.env` (BOT_TOKEN line)
- Chat ID: `~/.xavimail/config.json` → `tg_chat_id`
- Sends: send-complete, send-failed, blocked-unconfirmed, stale-confirmation, cooldown-blocked, morning digest.
- If TG goes silent: investigate, do not paper over.

### Incident origin

**2026-04-28** — A prior Claude session scheduled the Bob Dylan newsletter (FR + EN) at 23:57 local AND ran `schedule confirm` in the same session. Daemon fired at 7am next morning. FR went to 110 practitioners unintentionally; EN crashed on a SQLite threading bug (since fixed). Three new safeguard layers + the 12h TTL prevent recurrence. See `~/.claude/CLAUDE.md` "XaviMail — Practitioner Email" section for the rules every Claude session must follow.

## Lists

| List | Segments from contacts.json | Description |
|------|-----------------------------|-------------|
| `practitioners-en` | `non-french-practitioner` | EN practitioners |
| `practitioners-fr` | `french-active` + `french-inactive` | FR practitioners |

## Email Body Format

Plain markdown files. Template variables: `{first_name}`, `{last_name}`, `{email}`, `{unsubscribe_url}`.

The unsubscribe footer is appended automatically — don't add it manually.

Example: `emails/email-01-en.md`

```markdown
Hi {first_name},

Body of the email here.

Steven
```

## Send Workflow (every campaign)

1. `xavimail sync` — pull latest unsubscribes/bounces from D1
2. `xavimail send <list> "<subject>" email.md --dry-run` — preview who gets it
3. `xavimail send <list> "<subject>" email.md --test-to steven@multiplenatures.com` — test real send
4. `xavimail send <list> "<subject>" email.md` — full send
5. `xavimail stats` — confirm delivery counts

## Config

`~/.xavimail/config.json` — AWS creds, from address, DB path, MAILER_SECRET.

To switch to `steven@xavigate.com` later: change `from_email` in config.json.

## Infrastructure

- **Cloudflare Worker routes** (in `xavigate-api/src/mailer-routes.js`):
  - `GET /mailer/unsubscribe` — one-click unsubscribe
  - `POST /mailer/bounce` — SNS webhook (SES bounces/complaints)
  - `GET /mailer/suppressions` — CLI sync endpoint
- **D1 table:** `mailer_suppressions` (migration `026-mailer-suppressions.sql`)
- **SNS topic:** `arn:aws:sns:us-east-1:339713035288:xavimail-ses-notifications`
- **MAILER_SECRET:** stored in `~/.xavimail/config.json` and as Cloudflare Worker secret

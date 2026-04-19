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

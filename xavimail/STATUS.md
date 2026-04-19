# XaviMail — Status

**Status:** Live  
**Last updated:** 2026-04-19  
**Location:** `Projects/communication/xavimail/`  
**CLI:** `xavimail` (symlinked to `~/bin/xavimail`)  
**DB:** `~/.xavimail/xavimail.db` (local SQLite)  
**Config:** `~/.xavimail/config.json`

---

## What It Is

Self-hosted mailing list tool. Replaced MailerLite on 2026-04-19.  
Sends via AWS SES from `steven@multiplenatures.com`.  
Unsubscribes and bounces handled via Cloudflare Worker + D1.

---

## Lists

| List | Count | Segments |
|------|-------|---------|
| `practitioners-en` | 12 | `non-french-practitioner` |
| `practitioners-fr` | 104 | `french-active` + `french-inactive` |

---

## Infrastructure

| Component | Location |
|-----------|---------|
| CLI source | `Projects/communication/xavimail/xavimail.py` |
| Worker routes | `xavigate-api/src/mailer-routes.js` |
| D1 migration | `xavigate-api/migrations/026-mailer-suppressions.sql` |
| D1 table | `mailer_suppressions` in `renergence-training` D1 |
| SNS topic | `arn:aws:sns:us-east-1:339713035288:xavimail-ses-notifications` |
| Bounce/unsub endpoint | `https://api.xavigate.com/mailer/bounce` + `/mailer/unsubscribe` |

---

## Todo

- [ ] Add `steven@xavigate.com` as a second sender option (for Xavigate-branded lists)
- [ ] Open/click analytics (tracking pixel + redirect endpoint)
- [ ] XaviMail personalized mode — 1:1 draft-per-contact with Gmail reply scanning
- [ ] Gmail integration: scan inbox for practitioner replies, update last_response in contacts.json

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-19 | Initial build. SES sending, SQLite subscriber DB, D1 suppressions, SNS bounce pipeline. practitioners-en (12) + practitioners-fr (104) imported. |

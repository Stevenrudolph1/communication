# XaviMail — Status

**Status:** Live
**Last updated:** 2026-05-04

## Changelog

### 2026-05-04 — Test-before-confirm gate tightened
- `schedule confirm` now requires a matching `[TEST]` send for the same list+subject within the last 24 hours before practitioner jobs can be confirmed.
- Test sends are logged under `test:<list>` so they cannot trip the production list cooldown.
- `schedule run <id>` now performs the documented manual cooldown override while still keeping confirmation checks in place.
- Partial scheduled sends are marked `partial` instead of `sent`, with TG notification showing sent/error counts.
- Practitioner production lists require confirmation by default even when `~/.xavimail/confirm-required.txt` exists.

### 2026-04-28 — Scheduling safeguards rebuilt (post-Dylan-incident)
- **Incident:** A prior Claude session scheduled FR+EN Dylan newsletter at 23:57 local + ran confirm same session. Daemon fired 7am next morning. FR went to 110 practitioners unintentionally; EN crashed on SQLite threading bug.
- **Fix A — threading:** `db.py` now uses per-thread connections (`threading.local()`). Daemon worker threads no longer share a connection.
- **Fix B — confirmation TTL:** `daemon.py` `CONFIRMATION_TTL_HOURS=12`. Stale confirmations auto-blocked + TG alert + reset to `blocked-unconfirmed`.
- **Fix C — TG notifications:** `tg_chat_id=1192545368` wired in `~/.xavimail/config.json`. Daemon now TGs send/fail/block.
- **Fix D — morning digest:** `scheduler/digest.py`. Cron `0 6 * * *`. Lists next 24h queue with duplicate-day/unconfirmed/stale flags.
- **Fix E — stale crontab:** removed `32 7 25 4 *` line that would re-fire next April.
- **Layer 1 (schedule-time):** `cmd_schedule_add` refuses jobs that conflict with existing same-list-same-day. Override: `--allow-multi`.
- **Layer 2 (fire-time):** Daemon refuses to fire if list sent within `LIST_COOLDOWN_HOURS=20`. Override: `schedule run <id>`.
- **Layer 3 (digest):** Duplicate-day flag in morning TG digest.
- **Documentation:** `~/.claude/CLAUDE.md` "XaviMail — Practitioner Email" section updated. New memory file `feedback_xavimail_scheduling_safeguards.md`. README `Scheduling — Safeguards` section.

### 2026-04-19 — Initial deploy

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

## Sequencing Roadmap

Trigger-based email sequences — an event fires, a timed chain of emails follows automatically. No ConvertKit. Built into XaviMail + Xavigate API.

**Architecture note:** Two systems share the work.
- **Xavigate API** (Cloudflare Worker) owns trigger detection — Stripe webhooks, intake events, cron jobs. Already running for 2 flows.
- **XaviMail** (local CLI + SES) owns send logic, templates, suppression, tracking.
- New sequences extend the API's `recovery_flows` pattern with a new `sequence_flows` table.

---

### SEQ-01 — Free Book Download → Assessment Nurture
**Trigger:** `checkout.session.completed` where product is a free book  
**Goal:** Convert passive readers into assessment takers  
**Audience:** Anyone who downloads a free book (EN or FR)  
**Cadence:** 4 emails over 14 days

| Step | Delay | Content |
|------|-------|---------|
| 1 | Immediately | "Here's your book — one thing to notice as you read it" |
| 2 | Day 3 | Key insight from the book, applied to their situation |
| 3 | Day 7 | "What this usually reveals" — bridge to the assessment |
| 4 | Day 14 | Direct CTA: try the Xavigate Insight Assessment |

**Exit:** Assessment started, book purchased (upsell), or unsubscribe  
**Build:** New flow type `FLOW_BOOK_NURTURE` in API + 4 email templates (EN + FR) + xavimail send integration  
**Status:** Not started — **START HERE (prototype)**

---

### SEQ-02 — Post-Map-Purchase Onboarding
**Trigger:** `checkout.session.completed` where product is the Xavigate Map ($97)  
**Goal:** Deepen relationship, set up practitioner path  
**Audience:** New Map buyers  
**Cadence:** 3 emails over 10 days

| Step | Delay | Content |
|------|-------|---------|
| 1 | Day 1 | "What to do first with your Map" — orientation |
| 2 | Day 4 | "How to read the results" — key sections explained |
| 3 | Day 10 | "What comes next" — natural intro to practitioner track |

**Exit:** Practitioner program inquiry, or sequence complete  
**Build:** Extend existing `onCheckoutCompleted()` handler + 3 email templates (EN + FR)  
**Status:** Not started

---

### SEQ-03 — Assessment Start → Completion Nudge
**Trigger:** Intake form started (`assessment_started_at` set) but not completed after 24h  
**Goal:** Recover incomplete assessments  
**Audience:** Anyone who began the intake form but stopped  
**Cadence:** 2 emails over 72h

| Step | Delay | Content |
|------|-------|---------|
| 1 | 24h | "You started something — here's why finishing it matters" |
| 2 | 72h | Final nudge + direct link back to their intake form |

**Exit:** Assessment completed, or sequence complete  
**Build:** New cron check on `intake_profiles` (started but not completed) + 2 email templates  
**Status:** Not started

---

### SEQ-04 — Practitioner Re-engagement
**Trigger:** Cron — practitioner has not opened any email in 90+ days  
**Goal:** Recover dormant practitioners before they're gone  
**Audience:** practitioners-en + practitioners-fr with no opens in 90 days  
**Cadence:** 3 emails over 21 days

| Step | Delay | Content |
|------|-------|---------|
| 1 | Day 0 | Something genuinely useful — no mention of re-engagement |
| 2 | Day 7 | "Still there?" — direct, short, human |
| 3 | Day 21 | Final: "I'll stop if this isn't useful anymore" + unsubscribe prompt |

**Exit:** Any open or click (re-engaged), unsubscribe, or sequence complete (suppress)  
**Build:** Cron job reading `mailer_events` for last-open date + sequence logic in XaviMail  
**Status:** Not started

---

### SEQ-05 — New Practitioner Welcome
**Trigger:** Manual tag (when someone certifies) or future: webhook from certification system  
**Goal:** Onboard new practitioners into active practice  
**Audience:** Newly certified MN practitioners  
**Cadence:** 5 emails over 4 weeks

| Step | Delay | Content |
|------|-------|---------|
| 1 | Day 0 | Welcome — what being a practitioner actually means |
| 2 | Day 3 | First tool: how to use the Map in a session |
| 3 | Day 7 | Common mistakes new practitioners make |
| 4 | Day 14 | Marketing yourself as an MN practitioner |
| 5 | Day 28 | Check-in — what's working, what's not |

**Exit:** Sequence complete  
**Build:** Tagged list `practitioners-new` + 5 email templates (EN + FR) + sequence YAML  
**Status:** Not started

---

### Build Order

| Priority | Sequence | Trigger type | Est. effort |
|----------|----------|--------------|-------------|
| 1 | SEQ-01 Book Download Nurture | Stripe webhook | Medium |
| 2 | SEQ-02 Post-Map Onboarding | Stripe webhook | Low (extends existing) |
| 3 | SEQ-03 Assessment Completion Nudge | Cron on intake_profiles | Medium |
| 4 | SEQ-04 Practitioner Re-engagement | Cron on mailer_events | Medium |
| 5 | SEQ-05 New Practitioner Welcome | Manual tag / future webhook | Low (YAML sequence) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-19 | Initial build. SES sending, SQLite subscriber DB, D1 suppressions, SNS bounce pipeline. practitioners-en (12) + practitioners-fr (104) imported. |

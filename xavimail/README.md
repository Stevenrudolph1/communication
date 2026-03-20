# XaviMail

**Status:** Concept / Pre-development
**Created:** 2026-02-18
**Owner:** Steven Rudolph
**Location:** `Projects/xavimail/`

---

## What Is XaviMail?

XaviMail is a personalised email system that replaces mass newsletters with individual, context-aware emails to each contact — written by Xavi (Claude) based on what is known about that person, reviewed and approved by Steven before sending.

The core idea: at Steven's scale (200-300 real practitioners and contacts), mass email is the wrong tool. These are people who trained with Steven, attended his events, bought his courses. They deserve emails that treat them as individuals — referencing their actual work, their cert level, their focus area, their country. XaviMail makes that possible without requiring Steven to write each email manually.

---

## How It Works (Concept)

### 1. Contact Intelligence
Each contact in `planning/communication/contacts.json` has enriched data:
- Practitioner cert level and MNTEST usage (from Google Sheet)
- MailerLite engagement history (opens, clicks, groups)
- Website/LinkedIn research (professional focus, clients, how they use MN)
- Relationship notes (how they know Steven, what's happened, what they need)
- Email history (last contacted, last response, next action)

### 2. The Queue
Contacts are prioritised for outreach based on:
- **Warmth** — Xavigate launch attendees first, then inner circle, then active practitioners
- **Strategic value** — e.g. Elena Zlygosteva (Oxford Leadership / Baltic revival), Jan Goodman (US market)
- **Recency** — people who've engaged recently get prioritised
- **Segment logic** — each segment has a defined angle and CTA (see `MAILERLITE-PLAN.md`)

### 3. The Drafting Session
Each session (or on request), Xavi pulls the next 2-3 people from the queue, reads their contact profile, researches any gaps, and drafts a personalised email for each. Emails are short (3-5 sentences), written in Steven's voice, reference something specific about the person.

### 4. Permission Layer (First Contact)
Before the personalised emails begin, Steven sends each contact a brief permission email:

> *"Hi [Name], I've been sending generic newsletters — they don't really serve anyone well. I want to try something different: personalised emails based on what I actually know about your work. Would you be open to that? Just reply yes."*

Anyone who replies yes enters the XaviMail queue. This creates a self-selected engaged list.

### 5. Steven Reviews
Steven reads each draft, makes any edits, confirms send. Xavi sends via `~/bin/send-mail`. The whole review process should take under 10 minutes per batch.

### 6. Tracking
After each email:
- `last_contacted` date logged in contacts.json
- Any response logged as a note
- `next_action` field updated (follow up in X weeks, send Y content, etc.)

---

## Voice & Tone

XaviMail emails are NOT:
- Newsletter copy
- Marketing emails with someone's name inserted
- Formal or structured

XaviMail emails ARE:
- 3-7 sentences
- Written as if Steven noticed something specific about that person
- Direct, warm, no fluff
- Framework-literate when appropriate (the person knows MN)
- Ending with one clear next step or question — never multiple CTAs

### Example (Corinne Jacob)

> Hi Corinne, I noticed you still have the Lyon 2019 conference on your homepage — good memories. A lot has evolved since then. I've published three books that take the frameworks further — Structure, Alignment, Positioning — and I've been writing about it on Substack. Given how you're using MN with corporate teams, I think the Structure framework in particular would resonate. Want me to send you the first book?

---

## The Xavi Disclosure

Steven's policy: be transparent that emails are drafted by an AI agent (Xavi) and reviewed by Steven. This is introduced naturally — either in the permission email or when the personalised emails begin. The framing: *"I work with an AI assistant called Xavi who helps me stay personally connected at scale — these emails are drafted by Xavi based on your profile, reviewed and sent by me."*

---

## Segments & Angles

See `Projects/marketing/mailerlite/MAILERLITE-PLAN.md` for the full segment strategy. In summary:

| Segment | Angle | CTA |
|---------|-------|-----|
| French active practitioners | Leave to Sacha unless specific reason | — |
| French inactive | "A lot has changed, here's where things are heading" | Substack + books |
| Non-French practitioners | Direct Substack pitch | Substack |
| Baltic | Forward-looking, no mention of Rytis | Substack + "reply to reconnect" |
| Xavigate launch attendees | "The work has kept going" | Substack |
| NYN course | Book push (they spend money) | Gateway book → Depth/Instruments |
| Inbound leads | Cold reactivation, one shot | Free Gateway book |
| SOS CV directors | Institutional courtesy update | renergence.com |
| Legacy Quest | One shot, then purge if no response | Free book or Substack |

---

## Tech Stack (Proposed)

| Component | Tool | Notes |
|-----------|------|-------|
| Contact data | `planning/communication/contacts.json` | Master CRM |
| Email sending | `~/bin/send-mail` | AWS SES, from steven@xavigate.com |
| Drafting | Claude (Xavi) in session | Reads contact profile, drafts email |
| Tracking | contacts.json fields | `last_contacted`, `last_response`, `next_action` |
| Queue management | Script or manual per session | TBD |

No new infrastructure needed for MVP. Everything runs on existing tools.

---

## What's Not Built Yet

- [ ] Permission email campaign (first contact to each person)
- [ ] `last_contacted` / `next_action` fields added to contacts.json schema
- [ ] Queue script (auto-select next N contacts by priority)
- [ ] Response tracking (manual for now, possibly Gmail IMAP later)
- [ ] Voice calibration (draft 5-10 emails, Steven edits, Xavi learns the voice)

---

## Files

| File | Purpose |
|------|---------|
| `README.md` | This document |
| `VOICE-GUIDE.md` | Steven's voice — do's, don'ts, examples (to be built) |
| `QUEUE.md` | Current outreach queue and status (to be built) |

---

## Related Projects

| Project | Relationship |
|---------|-------------|
| `planning/communication/contacts.json` | CRM that feeds XaviMail |
| `marketing/mailerlite/MAILERLITE-PLAN.md` | Segment strategy XaviMail executes |
| `marketing/mailerlite/` | Backup data and exports |

---

## Session Protocol

When Steven says "XaviMail session" or "draft this week's emails":
1. Read contacts.json
2. Pull next 2-3 from queue (by priority)
3. Check each person's notes and research any gaps
4. Draft personalised emails
5. Present drafts for Steven's review
6. Send approved emails via send-mail
7. Log sent date and any notes back to contacts.json

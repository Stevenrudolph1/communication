# Practitioner Newsletter — Master Plan

## What this is

A 3x/week email to MN practitioners. Not a newsletter in the traditional sense — no headers, no sections, no "this week in MN." Just a note from Steven. One thing per email. Short. Useful.

Practitioners are trained. They know the framework. Every email should deepen their practice, give them something they can use with clients, or update them on something real.

---

## Cadence

| Day | Slot | Email Type |
|-----|------|-----------|
| Tuesday | Insight | One idea from MN theory or practitioner practice — something to sit with |
| Thursday | Spotlight | A career, a case, a comparison, or a client situation — concrete and usable |
| Saturday | Resource | A tool, article, book, or update — something to use or share |

This is a default rhythm. It can shift. The point is one type per slot so content production is predictable.

---

## Email parameters

**Length:**
- Tuesday Insight: 150–250 words
- Thursday Spotlight: 250–400 words
- Saturday Resource: 150–300 words

Never longer. If it wants to be longer, it's two emails, not one.

**Voice:** Steven's voice. Direct. No "dear practitioners." No "I hope this finds you well." Start with the thing.

**Subject line:** Specific. Concrete. What the email is actually about. No hype words (unlock, discover, transform). No questions as subject lines. Examples:
- "Why the same client thrives in one role and wilts in another"
- "Career spotlight: grief counselor"
- "New book: MN for Educators"

**Opening:** First name (`{first_name}`), then straight in. No preamble.

**CTA:** One per email, max. Usually a link to a resource, article, or book. Never a hard sell.

**Sign-off:** Always Steven.

**Unsubscribe:** Appended automatically by XaviMail. Do not add manually.

---

## Format / HTML

See `templates/email.html` — the base template. All emails render from this.

Design rules:
- Single column, max-width 600px
- White background, dark text
- No images in body (deliverability + load time)
- Small Xavigate wordmark in header only
- Clean footer with unsubscribe link
- Readable on mobile without pinching

---

## Languages

EN is always written and tested first. FR translation follows after EN is approved.

Translation is not word-for-word — it adapts to FR practitioner context. Key terms use canonical MN French terminology (see MN canonical orders in memory).

EN send → Steven approves → FR translate → Steven approves → FR send.

---

## Workflow for each email

**Before writing (30 seconds):**
```
python3 tracker.py status              # variety check — what's run recently?
python3 tracker.py scan A-07           # is this specific topic clear?
```

**Write and send:**
1. Pick topic from `CONTENT-MAP.md`
2. **Invoke `/practitioner-email` skill** — loads full canon before writing, produces audited draft
3. Save EN draft → `drafts/YYYY-MM-DD-{slot}-{slug}-en.md`
4. Test: `xavimail send practitioners-en "Subject" draft.md --test-to steven@multiplenatures.com`
5. Steven approves → translate FR → test FR → Steven approves
6. Send EN → Send FR

**After sending (log immediately):**
```
python3 tracker.py log \
  --slot tue --category A --topic-id A-07 \
  --kernel KRN-003 \
  --subject "Why the same person thrives in one role and depletes in another"
```
Add `--timely` flag for Category G (trends) and M (Trainer Program) emails.

**Move drafts to `published/`.**

---

## Sources

All content draws from these sources (details in `CONTENT-MAP.md`):

| Source | What it provides |
|--------|-----------------|
| MN for Practitioners (unpublished) | Practitioner skills, session examples, case studies, principles |
| Multiple Natures (published ebook) | Framework explanations, client-facing passages |
| MN Handbook for Educators | School/education-specific content |
| MN Handbook for School Counselors | Counselor-specific content |
| Xavigate articles | Framework comparisons, career fit, context |
| Xavigate research section | Research lineage, academic grounding |
| Career database | Offbeat career profiles by MN/MI |
| Xavigate Map | When/how to use the diagnostic with clients |
| Practitioner experience | Steven's direct observations from the field |

---

## What this is NOT

- Not a sales funnel (practitioners are already in)
- Not a content marketing channel (no SEO, no sharing CTAs)
- Not a course module (doesn't build sequentially)
- Not a newsletter with sections and roundups

It is a professional relationship maintained through regular, useful contact.

---

## Continuity rules

**Two thresholds, not a rulebook:**

| Content type | Recycle after | Categories |
|---|---|---|
| Evergreen | 26 weeks | A, B, C, D, E, F, H, I, J, K, L, N, T |
| Timely | 52 weeks | G (trends), M (Trainer Program), P (AI/Tech) |

**Human checks, not automation:**
- `tracker.py scan TOPIC-ID` — run before writing. 5 seconds.
- `tracker.py status` — run weekly. Shows category balance visually.
- `tracker.py recycle` — run monthly. Shows what's eligible to revisit.

**When recycling:** different angle, different subject line, different excerpt. Not a resend.

**The signal to watch:** If practitioners start unsubscribing, the first thing to check is frequency, not content. 3x/week is aggressive — watch the unsubscribe rate monthly.

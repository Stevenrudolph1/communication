# Practitioner Newsletter

3x/week emails to MN practitioners (Tue/Thu/Sat). One thing per email. Short. Useful.

## Files

| File | What it is |
|------|-----------|
| `PLAN.md` | Cadence, parameters, format rules, workflow |
| `CONTENT-MAP.md` | Full topic library — 80+ topics across 6 categories |
| `templates/email.html` | HTML base template for all emails |
| `drafts/` | Emails in progress |
| `published/` | Sent emails (archived) |

## Content categories

| Cat | Topics | Count |
|-----|--------|-------|
| A — Practitioner Skills | From MN for Practitioners (unpublished) | 20 |
| B — Career Spotlights | Offbeat careers mapped to MN + MI | 30 |
| C — Practitioner Identity & Marketing | Practice building, positioning | 15 |
| D — Framework Comparisons | MN vs. MBTI/DISC/Enneagram etc. | 9 |
| E — Books & Resources | Excerpts, tools, updates | 11 |
| F — Client Situations | Fictional case vignettes | 10 |

## Slot defaults

- **Tuesday** → Category A (Insight)
- **Thursday** → Category B, C, F (Spotlight)
- **Saturday** → Category D, E (Resource)

## To produce an email

1. Pick a topic from `CONTENT-MAP.md`, note the kernel
2. Write draft in `drafts/YYYY-MM-DD-{tue|thu|sat}-{slug}.md`
3. Test: `xavimail send practitioners-en "Subject" draft.md --test-to steven@multiplenatures.com`
4. Steven approves → translate to FR → Steven approves → send both
5. Move to `published/`

## First 4 weeks mapped

See bottom of `CONTENT-MAP.md` for the priority order.

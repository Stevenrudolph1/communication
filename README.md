# Communication

External communications: articles, newsletters, partner announcements, practitioner outreach. Multi-channel content distribution.

## What This Is

- **Primary channel**: Substack (renergence.substack.com) — publishing hub
- **Newsletter automation**: MailerLite (reactivation in progress)
- **Social media**: Late API integration (LinkedIn, X)
- **Partner outreach**: Email, announcements, relationship maintenance

## Current State

**Substack** (Primary)
- Status: 5 articles drafted, Shriya uploading to platform
- Editorial calendar: 24 articles planned
- Cadence: 1 article/week (Wednesday publication)
- Process: Claude drafts (OpenAI image generation) → Shriya uploads → Steven approves before live
- URL: renergence.substack.com
- Rule: **Steven sees every post before publication** (never auto-post)

**Social Media** (Late API)
- LinkedIn: 3x/week (automated via Late API, $19/mo)
- X: 4x/week (automated via Late API)
- Week 1 posts: Done and going out (Feb 18)
- Content cross-references: 1 in 6-8 LinkedIn posts, 1 in 8-10 X posts link to Substack

**MailerLite** (Reactivation Prioritized)
- Existing lists: Hundreds of contacts (to be cleaned up)
- Signup: Invitation to move to Substack (2026-02-18, Steven + Shriya)
- Purpose: Keep practitioners informed, cultivate network
- Cost: $10/mo (voluntary subscriber list)
- Status: **High priority — responsible to maintain contact** (not chase features, but stay present)

**Partners/Practitioners**
- Elena Z (Latvia): Strong contender, cultivate connection
- Sacha (France): Established relationship (~$25K/yr), maintain
- MNTEST practitioners: Keep informed via MailerLite

## Directory Structure

```
communication/
├── substack/
│   ├── articles/                  ← Drafted content
│   ├── images/                    ← OpenAI-generated (24 styles)
│   ├── editorial-calendar.md
│   ├── SUBSTACK-PUBLISHING-CANON.md
│   └── GENERATION-PROCESS.md
├── mailerlite/
│   ├── list-segments/
│   └── templates/
├── Partners/
│   └── [partner-specific materials]
├── [email campaigns]
└── [announcements]
```

## Content Governance

- **Brand voice**: GOV-06 applied to all public-facing content
- **Publishing canon**: PUB 01-20 documents (imprint authority, workflow)
- **No auto-posting**: Steven approves all public-facing content before live
- **Practitioner responsibility**: Stay in contact, don't chase features; real relationship, realistic expectations

## Next Steps

1. **MailerLite reactivation** (2026-02-18) — clean lists, send Substack invite
2. **Substack content pipeline** — first article live this week
3. **Social media automation** — Late API posts going out as drafted
4. **Practitioner outreach** — follow up with Elena Z, maintain Sacha relationship

## Key Contacts

| Person | Country | Role | Status |
|--------|---------|------|--------|
| Shriya | Global | Course fulfillment, Substack uploads, content ops | Active |
| Elena Z | Latvia | Practitioner (strong contender) | To cultivate |
| Sacha | France | Revenue partner (~$25K/yr) | Stable |

## Reference

- **Content voice**: `planning/governance/production/GOV-06-brand-voice.md`
- **Publishing workflow**: `planning/governance/production/` (PUB 01-20)
- **Marketing automation**: `marketing/SOCIAL-MEDIA-AUTOMATION-PLAN.md`
- **Product funnel**: `marketing/PRODUCT-FUNNEL-AND-PRACTITIONER-PATHWAY.md`

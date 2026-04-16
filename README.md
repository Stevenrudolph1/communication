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
│   ├── drafts/                    ← Drafted content
│   ├── reviewed/                  ← Steven-reviewed articles
│   ├── published/                 ← Published articles
│   ├── archive/                   ← Older/superseded drafts
│   ├── article-seeds/             ← Raw article ideas and seeds
│   ├── source-index/              ← Source tracking
│   ├── publish-info/              ← Publishing metadata
│   ├── images/                    ← Generated images
│   ├── assets/                    ← Other Substack assets
│   ├── EDITORIAL-CALENDAR-24.md
│   ├── SUBSTACK-PUBLISHING-CANON.md
│   ├── GENERATION-PROCESS.md
│   ├── produce-article.py         ← Article producer (content-system pipeline)
│   ├── generate-article.sh
│   ├── generate-image.py
│   ├── generate-shriya-calendar.py
│   └── sync-from-substack.py
├── linkedin/
│   ├── articles/                  ← LinkedIn article content
│   ├── linkedin-article-generator/ ← Generator pipeline
│   └── LINKEDIN-ARTICLES-PLAN.md
├── mailerlite/
│   ├── campaigns/                 ← Email campaigns
│   ├── sent/                      ← Sent campaign records
│   └── templates/                 ← Email templates
├── xavimail/                      ← Substack state tracking and checks
├── Partners/
│   └── [partner-specific materials]
├── _unsorted/                     ← Unsorted legacy files
└── README.md
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

## Content System Pipeline

All content production flows through the content-system pipeline. Every article, social post, or newsletter traces to an approved kernel.

- **Architecture**: `~/Projects/content-system/CONTENT-SYSTEM-ARCHITECTURE.md`
- **Flow**: Sources -> Insight Engine -> Insight Gate (15/20) -> Kernel Store -> Brief Builder -> Producer -> Ledger
- **Substack producer**: `communication/substack/produce-article.py`
- **LinkedIn producer**: `marketing/linkedin-article-generator/pipeline.py`
- **Kernel lookup**: `python3 content-system/builders/brief-builder.py --list`

## Reference

- **Content voice**: `knowledge/governance/GOV-06-brand-voice.md`
- **Writing method**: `knowledge/governance/GOV-14-writing-method.md`
- **Publishing workflow**: `books/_canon/publishing-canon/` (PUB 01-20)
- **Marketing automation**: `marketing/SOCIAL-MEDIA-AUTOMATION-PLAN.md`
- **Product funnel**: `marketing/PRODUCT-FUNNEL-AND-PRACTITIONER-PATHWAY.md`

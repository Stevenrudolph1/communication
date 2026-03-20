# LinkedIn Article Generator

A multi-pass content pipeline for producing LinkedIn Articles that pass governance, voice, SEO, and platform-specific checks before Steven reviews.

## Architecture

```
Phase 1: CONSTITUTION    Load governance + article plan + book source
Phase 2: DRAFT           Generate article from constitution + prompts
Phase 3: EDITORIAL       Multi-pass editing (voice, clarity, platform, SEO)
Phase 4: COMPLIANCE      renOS checkers + LinkedIn-specific validators
Phase 5: COMPANION       Generate companion post + DM triggers
Phase 6: OUTPUT          Final article + audit trail for Steven review
```

## Usage

```bash
python3 generate.py --article 1
python3 generate.py --article 1 --phase editorial   # re-run from a specific phase
python3 generate.py --article 1 --check-only         # run checkers without regenerating
```

## Directory Structure

```
linkedin-article-generator/
  generate.py              # Main pipeline script
  config.py                # Article plan data, paths, constants
  constitution.py          # Loads all governance docs into context
  writer.py                # Phase 2: Draft generation
  editor.py                # Phase 3: Multi-pass editorial
  checkers/
    voice_checker.py       # GOV-06 brand voice compliance
    linkedin_checker.py    # LinkedIn platform rules (SEO, formatting, limits)
    governance_checker.py  # renOS practitioner invariants + marketing governance
    publish_gate.py        # Final publish gate (4 mandatory checks)
  prompts/
    system.md              # System prompt for writer
    editorial_passes.md    # Editorial pass definitions
    companion_post.md      # Companion post generation prompt
  output/
    article-01/            # Per-article output directory
      draft-v1.md
      editorial-log.md
      compliance-report.md
      final.md
      companion-post.md
```

## Governance Integration

The generator loads and enforces:

| Document | What It Governs |
|----------|----------------|
| GOV-06 | Voice identity, 5 execution tests, prohibited/required language |
| MARKETING-GOVERNANCE | Content ratio (85-90% recognition), encounter creation model |
| CONTENT-LEARNINGS | Proven patterns (max 3 per article), underperformance signals |
| renOS practitioner invariants | No identity hardening, no moralized fit, no placement |
| LINKEDIN-ARTICLES-PLAN | Article specs, SEO targets, architecture template, publish gate |

## Editorial Passes

Each article goes through 5 editing passes:

1. **Voice Pass** — GOV-06 compliance: declarative/structural/grounded, 5 execution tests, prohibited language removal
2. **Clarity Pass** — Plain language: no jargon, no insider terms, every sentence comprehensible to an HR leader who's never heard of Renergence
3. **Platform Pass** — LinkedIn-specific: headline limits, H2 frequency, paragraph length, keyword placement, link positioning
4. **SEO Pass** — Keyword density, H2 keyword inclusion, first-100-words keyword, URL-slug-friendly headline
5. **Cadence Pass** — Steven's writing rhythm: long-short punches, fragment variation, structural wit, lightness test

## Publish Gate

Every article must pass ALL four checks:

1. Plain-language pass (no framework jargon)
2. Two or more concrete examples (specific, recognizable)
3. Single clear CTA (one link, one action)
4. Companion post + DM trigger ready

## Output

The generator produces:
- `final.md` — The article ready for LinkedIn publishing
- `companion-post.md` — LinkedIn Post for publish day
- `editorial-log.md` — All pass scores and revision notes
- `compliance-report.md` — All checker results

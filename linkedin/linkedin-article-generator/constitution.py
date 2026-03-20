"""
LinkedIn Article Generator — Constitution Loader

Loads all governance docs and article plan into a single constitution
string that gets injected into every prompt. This ensures the writer
and editor always operate within governed constraints.
"""

from pathlib import Path
from config import (
    GOV_06_PATH,
    MARKETING_GOV_PATH,
    CONTENT_LEARNINGS_PATH,
    ARTICLES_PLAN_PATH,
    RENOS_ARCHITECTURE_PATH,
)


def _read_if_exists(path: Path) -> str:
    """Read file content or return a warning."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"[WARNING: {path} not found]"


def _extract_section(text: str, start_marker: str, end_marker: str = None) -> str:
    """Extract a section from a document by markers."""
    idx = text.find(start_marker)
    if idx == -1:
        return ""
    chunk = text[idx:]
    if end_marker:
        end_idx = chunk.find(end_marker, len(start_marker))
        if end_idx != -1:
            chunk = chunk[:end_idx]
    return chunk.strip()


def load_constitution(article_num: int = None) -> str:
    """
    Build the full constitution for article generation.

    Returns a single string containing all governance constraints,
    voice rules, content learnings, and article-specific specs.
    """
    sections = []

    # --- GOV-06: Brand Voice ---
    gov06 = _read_if_exists(GOV_06_PATH)
    sections.append(
        "=== BRAND VOICE GOVERNANCE (GOV-06) ===\n\n"
        "The voice in 5 words: Declarative. Structural. Grounded. Spacious. Final.\n\n"
        "FIVE EXECUTION TESTS (every piece of content must pass all 5):\n"
        "1. RECOGNITION TEST — Reader encounters their own experience named, not just information.\n"
        "2. DEMONSTRATION TEST — Shows the reframe in action, doesn't just describe it.\n"
        "3. CADENCE TEST — Long-short punches, fragments, varied paragraph structure.\n"
        "4. STRUCTURAL WIT TEST — Absurdity named plainly, not forced jokes.\n"
        "5. LIGHTNESS TEST — Reader finishes lighter (relief, clarity, spaciousness), not just informed.\n\n"
        "PROHIBITED LANGUAGE:\n"
        "- Self-help/empowerment: 'You've got this,' 'believe in yourself,' 'unlock your potential'\n"
        "- Urgency/scarcity: 'limited time,' 'don't miss out,' countdowns\n"
        "- Promotional: 'revolutionary,' 'game-changing,' 'world-class,' 'groundbreaking'\n"
        "- Pop-psychology: 'toxic,' 'gaslighting,' 'setting intentions,' 'trauma response'\n"
        "- Hedging: 'perhaps,' 'might,' 'could be argued,' 'it seems'\n"
        "- Trait grammar: 'You are creative' (must be interaction grammar — what's happening in a situation)\n"
        "- Prescriptive: 'You should,' 'Try this,' 'Here's what to do,' '5 steps to'\n\n"
        "REQUIRED PATTERNS:\n"
        "- Interaction grammar only (situations, arrangements, dynamics — not traits in a person)\n"
        "- Pain language first, framework second\n"
        "- No outcome guarantees\n"
        "- Personalization error correction: structural reframes of personal attribution\n"
        "- Stop at orientation (name the pattern, don't prescribe the fix)\n"
    )

    # --- Marketing Governance ---
    sections.append(
        "=== MARKETING GOVERNANCE ===\n\n"
        "Core principle: Marketing is encounter creation, not demand generation.\n\n"
        "Content ratio (Steven personal channels):\n"
        "- 85-90% recognition (name what people already feel)\n"
        "- 10-15% directional signal (name product as structural completion)\n"
        "- 0% hard CTA in body (CTA only at article end, never the point of the piece)\n\n"
        "The CTA must feel like an afterthought — the article delivers full value standalone.\n"
        "The reader should feel: 'This person sees something I've been living.'\n"
        "NOT: 'This person is selling me something.'\n"
    )

    # --- Content Learnings ---
    sections.append(
        "=== PROVEN CONTENT PATTERNS ===\n\n"
        "Apply max 3 of these per article:\n"
        "1. Specific protagonist opening ('She was hired...') — 4,603 avg impressions vs 210 without\n"
        "2. Concrete observable detail (platform, time, behavior) — names Slack 4hrs/day not 'reactive'\n"
        "3. Named mechanism (a concept the reader can carry away and use)\n"
        "4. Absolution structure (remove personal attribution before structural reframe) — people share posts that defend them\n"
        "5. Single-sentence verdict ending (lands like a closing argument)\n"
        "6. Workplace > education on LinkedIn (audience skews professional/organizational)\n\n"
        "UNDERPERFORMANCE SIGNALS (avoid):\n"
        "- Abstract opening without protagonist anchor\n"
        "- No human angle\n"
        "- Narrow audience match\n"
        "- Long + abstract without specific scene\n"
    )

    # --- Practitioner Invariants ---
    sections.append(
        "=== PRACTITIONER INVARIANTS (renOS) ===\n\n"
        "These are non-negotiable constraints on all public content:\n"
        "1. You describe, you don't define (no identity hardening — never 'You ARE an X type')\n"
        "2. Fit is not merit (no moralizing about match quality)\n"
        "3. You can name cost, can't place person (no destination suggestion — never 'You should leave/stay')\n"
        "4. Structure explains suffering, doesn't excuse or moralize it\n"
        "5. Nothing predicts what happens next (no trajectories, no promises)\n"
    )

    # --- LinkedIn Platform Rules ---
    sections.append(
        "=== LINKEDIN ARTICLE PLATFORM RULES ===\n\n"
        "HEADLINE:\n"
        "- Max 150 chars (hard limit), target under 80 chars\n"
        "- Front-load primary keyword in first 40 chars\n"
        "- Headline becomes URL slug — keyword-rich headlines improve SEO directly\n"
        "- No ALL CAPS, no clickbait\n\n"
        "STRUCTURE:\n"
        "- H2 subheadings every 200-300 words\n"
        "- H2s must contain secondary keywords or variations\n"
        "- Paragraphs max 3-4 sentences (mobile readability)\n"
        "- Short paragraphs preferred (2-3 sentences)\n"
        "- First sentence under 12 words\n"
        "- Bold key phrases sparingly (1-2 per section max)\n"
        "- No bullet-point listicles (per brand voice)\n"
        "- No emoji (per brand voice)\n\n"
        "SEO:\n"
        "- Primary keyword in headline, first 100 words, and at least one H2\n"
        "- 3-10 natural occurrences of primary keyword in body\n"
        "- Secondary keywords distributed naturally\n"
        "- LinkedIn Article URLs are: linkedin.com/pulse/[headline-slug]-[author]\n\n"
        "LINKING:\n"
        "- NO links in first paragraph (algorithm treats as exit-intent)\n"
        "- 1-2 internal links to other LinkedIn Articles (when they exist)\n"
        "- CTA link at end only, descriptive anchor text\n"
        "- External links: max 4, placed mid-article or later\n\n"
        "CTA:\n"
        "- Single CTA at article end (after full value delivered)\n"
        "- Optional soft mid-article CTA after a strong section\n"
        "- CTA must not be the point of the article\n"
        "- Surround with whitespace\n\n"
        "HASHTAGS:\n"
        "- 3-5 at end of article\n"
        "- Pain language, not framework terms\n"
        "- No engagement bait (#follow #like #comment)\n\n"
        "PUBLISHING:\n"
        "- Tue/Wed/Thu, 8-10 AM target timezone\n"
        "- Stay active 60 minutes after publish (golden hour)\n"
        "- Each Article gets a companion LinkedIn Post\n"
    )

    # --- Article Architecture Template ---
    sections.append(
        "=== ARTICLE ARCHITECTURE ===\n\n"
        "Every article follows this structure:\n"
        "1. HOOK (2-3 sentences) — specific scenario or observation, no abstraction\n"
        "   - Use protagonist opening or contrarian statement\n"
        "   - First sentence under 12 words\n"
        "2. THE PROBLEM — what everyone assumes vs. what's actually happening\n"
        "   - Name the common misattribution (it's personal → it's structural)\n"
        "3. THE FRAMEWORK — introduce the diagnostic lens\n"
        "   - Without framework jargon (plain language only)\n"
        "   - Show the mechanism, don't name the system\n"
        "4. EXAMPLE 1 — concrete, specific, recognizable workplace scenario\n"
        "5. EXAMPLE 2 — different domain or angle (relationship, hobby, creative work)\n"
        "6. THE DISTINCTION — the named mechanism that makes this different from generic advice\n"
        "   - This is the takeaway the reader carries\n"
        "7. CTA — one clear link to xavigate.com resource\n"
        "   - Feels like an afterthought, not a pitch\n"
    )

    # --- Article-specific specs ---
    if article_num:
        from config import ARTICLES
        article = ARTICLES.get(article_num, {})
        if article:
            sections.append(
                f"=== ARTICLE {article_num} SPECIFICATIONS ===\n\n"
                f"Title: {article['title']}\n"
                f"Type: {article['type']}\n"
                f"Book: {article['book']}\n"
                f"SEO Primary: {article['seo_primary']}\n"
                f"SEO Secondary: {', '.join(article.get('seo_secondary', []))}\n"
                f"CTA: {article['cta_text']} — {article['cta_url']}\n"
                f"Core Argument: {article['core_argument']}\n"
                f"Word Count Target: {'1,200-1,500' if article['type'] == 'pillar' else '800-1,000'}\n"
            )

    return "\n\n---\n\n".join(sections)


def load_book_context(book_key: str) -> str:
    """
    Load relevant book content for article writing.

    Returns key excerpts and themes from the source book.
    This is a placeholder — in practice, the operator reads the PDF
    and provides a summary. The constitution tells the writer what
    the book argues; this provides texture and quotes.
    """
    # Book context is loaded manually per article (PDF reading)
    # This function returns the path for reference
    from config import BOOK_PATHS
    path = BOOK_PATHS.get(book_key)
    if path and path.exists():
        return f"[Book source available at: {path}]"
    return f"[Book source for '{book_key}' not found at expected path]"

"""
LinkedIn Article Generator — Configuration

Article plan data, file paths, constants, and platform limits.
"""

import os
from pathlib import Path

# === Paths ===
PROJECTS_ROOT = Path(os.path.expanduser("~/Projects"))
GENERATOR_ROOT = PROJECTS_ROOT / "communication" / "linkedin" / "linkedin-article-generator"
OUTPUT_ROOT = GENERATOR_ROOT / "output"
PROMPTS_ROOT = GENERATOR_ROOT / "prompts"

# Governance docs
GOV_06_PATH = PROJECTS_ROOT / "knowledge" / "governance" / "GOV-06-brand-voice.md"
MARKETING_GOV_PATH = PROJECTS_ROOT / "marketing" / "MARKETING-GOVERNANCE.md"
CONTENT_LEARNINGS_PATH = PROJECTS_ROOT / "marketing" / "CONTENT-LEARNINGS.md"
ARTICLES_PLAN_PATH = PROJECTS_ROOT / "communication" / "linkedin" / "LINKEDIN-ARTICLES-PLAN.md"
RENOS_ARCHITECTURE_PATH = PROJECTS_ROOT / "renOS" / "ARCHITECTURE.md"

# Book source material
BOOKS_ROOT = PROJECTS_ROOT / "books" / "00-gateway-books"
BOOK_PATHS = {
    "renergence": BOOKS_ROOT / "01-renergence" / "EN" / "exports" / "renergence.pdf",
    "multiple-natures": BOOKS_ROOT / "02-multiple-natures" / "EN" / "exports",
    "heroes-not-required": BOOKS_ROOT / "03-heroes-not-required" / "EN" / "exports",
}

# === LinkedIn Platform Limits ===
HEADLINE_MAX_CHARS = 150
HEADLINE_TARGET_CHARS = 80
BODY_MIN_WORDS = 1000
BODY_TARGET_WORDS = (1200, 1500)  # pillar articles
BODY_TARGET_WORDS_TACTICAL = (800, 1000)  # tactical articles
BODY_MAX_CHARS = 125000
COVER_IMAGE_DIMS = (1280, 720)
MAX_HASHTAGS = 5
MAX_CTAS = 1  # our plan says single CTA
MAX_OUTBOUND_LINKS = 4
FIRST_SENTENCE_MAX_WORDS = 12
PARAGRAPH_MAX_SENTENCES = 4
H2_FREQUENCY_WORDS = (200, 300)  # H2 every 200-300 words

# === SEO ===
PRIMARY_KEYWORD_MIN_OCCURRENCES = 3
PRIMARY_KEYWORD_MAX_OCCURRENCES = 10
KEYWORD_IN_FIRST_N_WORDS = 100

# === Editorial ===
EDITORIAL_PASS_THRESHOLD = 85  # score out of 100 to pass
MAX_REVISION_ROUNDS = 3

# === Publishing ===
PUBLISH_DAYS = ["Tuesday", "Wednesday", "Thursday"]
PUBLISH_HOURS = (8, 10)  # AM in target timezone
GOLDEN_HOUR_MINUTES = 60  # respond to all comments within this window

# === Article Plan ===
ARTICLES = {
    1: {
        "title": "Why Some Situations Cost More Than They Return",
        "type": "pillar",
        "book": "renergence",
        "seo_primary": "career misalignment",
        "seo_secondary": ["burnout vs misalignment", "organizational misfit"],
        "cta_url": "https://xavigate.com?utm_source=linkedin&utm_medium=article&utm_campaign=art01",
        "cta_text": "Free diagnostic books at xavigate.com",
        "core_argument": (
            "The cost of a situation isn't always obvious. Some look fine — good title, "
            "good pay, good team — and still drain you. You can't tell what something will "
            "do to you over time by how it feels at the beginning. You can only tell by "
            "staying long enough for the cost to show itself. Success doesn't just delay "
            "that recognition — it interferes with it."
        ),
        "publish_target": "Week of March 10, 2026",
    },
    2: {
        "title": "Burnout vs. Misalignment: Why Rest Won't Fix a Structural Problem",
        "type": "tactical",
        "book": "renergence",
        "seo_primary": "burnout vs misalignment",
        "seo_secondary": ["burnout misdiagnosis", "misalignment burnout"],
        "cta_url": "https://xavigate.com?utm_source=linkedin&utm_medium=article&utm_campaign=art02",
        "cta_text": "Renergence book (free at xavigate.com)",
        "links_to": [1],
        "core_argument": (
            "The most commonly misdiagnosed workplace problem. Distinguishes burnout "
            "(capacity overload) from misalignment (wrong arrangement). Shows why therapy, "
            "vacation, and self-care don't fix a misaligned situation."
        ),
        "publish_target": "Week of March 24, 2026",
    },
    3: {
        "title": "Why Knowing Your Personality Type Didn't Change Anything",
        "type": "pillar",
        "book": "multiple-natures",
        "seo_primary": "MBTI doesn't work",
        "seo_secondary": [
            "personality tests are wrong",
            "why personality tests don't help",
            "career alignment assessment",
            "personality test alternative",
        ],
        "cta_url": "https://xavigate.com?utm_source=linkedin&utm_medium=article&utm_campaign=art03",
        "cta_text": "MNTEST via xavigate.com",
        "core_argument": (
            "Every personality framework in circulation treats you as a fixed thing — "
            "a type, a set of traits, a stable identity. But engagement isn't fixed. "
            "It's situational and probabilistic. After 18 years and 300,000+ people "
            "tested, that's the single most important thing revealed — not what kind "
            "of person you are, but how you engage, and that it depends entirely on "
            "where you are. The test didn't see you. It sorted you."
        ),
        "publish_target": "Week of April 7, 2026",
    },
    4: {
        "title": "What Is Diagnostic Coaching — And Why Most Coaches Skip the Diagnosis",
        "type": "tactical",
        "book": "multiple-natures",
        "seo_primary": "diagnostic coaching",
        "seo_secondary": ["diagnostic framework coaching", "career coaching methodology"],
        "cta_url": "https://xavigate.com?utm_source=linkedin&utm_medium=article&utm_campaign=art04",
        "cta_text": "Practitioner training information",
        "links_to": [3, 1],
        "core_argument": (
            "Most coaching starts with goals, values, or mindset. Diagnostic coaching "
            "starts with the arrangement — is the situation built in a way that can return "
            "what the person needs?"
        ),
        "publish_target": "Week of April 21, 2026",
    },
    5: {
        "title": "When the Wrong Person Does the Right Work",
        "type": "pillar",
        "book": "heroes-not-required",
        "seo_primary": "why good employees leave",
        "seo_secondary": ["role misalignment", "retention diagnostic", "employee engagement"],
        "cta_url": "https://xavigate.com?utm_source=linkedin&utm_medium=article&utm_campaign=art05",
        "cta_text": "Heroes Not Required book (free at xavigate.com)",
        "core_argument": (
            "In every organization, someone absorbs work that was never formally assigned. "
            "They're good at it, so nobody reassigns it. The organization calls them 'reliable.' "
            "The person calls it Tuesday. This is the hero trap — and it's a structural "
            "retention risk nobody measures."
        ),
        "publish_target": "Week of May 5, 2026",
    },
    6: {
        "title": "The Role That Fits on Paper but Fails in Practice",
        "type": "tactical",
        "book": "heroes-not-required",
        "seo_primary": "role misalignment HR",
        "seo_secondary": ["talent diagnostic"],
        "cta_url": "https://xavigate.com?utm_source=linkedin&utm_medium=article&utm_campaign=art06",
        "cta_text": "Free diagnostic tools at xavigate.com",
        "links_to": [5],
        "core_argument": (
            "Why job descriptions, competency models, and even 360 feedback miss the real "
            "problem — the arrangement around the person, not the person's skills."
        ),
        "publish_target": "Week of May 19, 2026",
    },
}

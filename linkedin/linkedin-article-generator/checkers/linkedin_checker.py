"""
LinkedIn Platform Checker

Validates article against LinkedIn-specific formatting rules,
SEO requirements, and platform constraints.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LinkedInResult:
    score: int = 100
    violations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    passed: bool = True


def _count_words(text: str) -> int:
    """Count words in text, ignoring markdown formatting."""
    clean = re.sub(r"[#*_\[\]()]", "", text)
    return len(clean.split())


def _extract_headline(text: str) -> Optional[str]:
    """Extract the H1 headline from markdown."""
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_h2s(text: str) -> list:
    """Extract all H2 headings."""
    return re.findall(r"^##\s+(.+)$", text, re.MULTILINE)


def _extract_paragraphs(text: str) -> list:
    """Extract non-heading, non-empty paragraphs."""
    paragraphs = []
    for block in text.split("\n\n"):
        block = block.strip()
        if block and not block.startswith("#") and not block.startswith("---"):
            paragraphs.append(block)
    return paragraphs


def _extract_first_paragraph(text: str) -> str:
    """Get the first non-heading paragraph."""
    paragraphs = _extract_paragraphs(text)
    return paragraphs[0] if paragraphs else ""


def _count_keyword(text: str, keyword: str) -> int:
    """Count keyword occurrences (case-insensitive)."""
    return len(re.findall(re.escape(keyword), text, re.IGNORECASE))


def _extract_links(text: str) -> list:
    """Extract all markdown links."""
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def _extract_hashtags(text: str) -> list:
    """Extract hashtags."""
    return re.findall(r"#(\w+)", text.split("\n")[-5:] if isinstance(text, str) else "")


def check_linkedin(
    text: str,
    seo_primary: str = "",
    seo_secondary: list = None,
    article_type: str = "pillar",
) -> LinkedInResult:
    """
    Run LinkedIn platform compliance check.

    Args:
        text: Full article in markdown format
        seo_primary: Primary SEO keyword
        seo_secondary: List of secondary SEO keywords
        article_type: 'pillar' or 'tactical' (affects word count targets)
    """
    result = LinkedInResult()
    seo_secondary = seo_secondary or []

    # === HEADLINE ===
    headline = _extract_headline(text)
    if headline:
        result.metrics["headline"] = headline
        result.metrics["headline_chars"] = len(headline)

        if len(headline) > 150:
            result.violations.append({
                "rule": "headline_max",
                "message": f"Headline exceeds 150 chars ({len(headline)} chars)",
                "severity": "critical",
            })
            result.score -= 15
        elif len(headline) > 80:
            result.warnings.append({
                "rule": "headline_target",
                "message": f"Headline over 80 char target ({len(headline)} chars) — may truncate in feeds/SERPs",
                "severity": "minor",
            })
            result.score -= 3

        if seo_primary and seo_primary.lower() not in headline.lower():
            result.warnings.append({
                "rule": "headline_keyword",
                "message": f"Primary keyword '{seo_primary}' not in headline (OK if voice is stronger without it — compensate with H2s and first 100 words)",
                "severity": "minor",
            })
            result.score -= 3
    else:
        result.violations.append({
            "rule": "headline_missing",
            "message": "No H1 headline found",
            "severity": "critical",
        })
        result.score -= 15

    # === WORD COUNT ===
    word_count = _count_words(text)
    result.metrics["word_count"] = word_count

    if article_type == "pillar":
        min_words, max_words = 1200, 1500
    else:
        min_words, max_words = 800, 1000

    if word_count < min_words:
        result.violations.append({
            "rule": "word_count_low",
            "message": f"Word count ({word_count}) below target ({min_words})",
            "severity": "major",
        })
        result.score -= 8
    elif word_count > max_words * 1.3:  # 30% over is a warning
        result.warnings.append({
            "rule": "word_count_high",
            "message": f"Word count ({word_count}) significantly over target ({max_words})",
            "severity": "minor",
        })
        result.score -= 3

    # === FIRST SENTENCE ===
    first_para = _extract_first_paragraph(text)
    if first_para:
        first_sentence = first_para.split(".")[0].strip()
        first_sentence_words = len(first_sentence.split())
        result.metrics["first_sentence_words"] = first_sentence_words

        if first_sentence_words > 12:
            result.warnings.append({
                "rule": "first_sentence_length",
                "message": f"First sentence is {first_sentence_words} words (target: ≤12)",
                "severity": "minor",
            })
            result.score -= 3

    # === H2 FREQUENCY ===
    h2s = _extract_h2s(text)
    result.metrics["h2_count"] = len(h2s)

    expected_h2s = max(1, word_count // 300)
    if len(h2s) < expected_h2s:
        result.violations.append({
            "rule": "h2_frequency",
            "message": f"Only {len(h2s)} H2s for {word_count} words (expected ~{expected_h2s}+)",
            "severity": "major",
        })
        result.score -= 8

    # === H2 KEYWORDS ===
    if seo_primary or seo_secondary:
        all_keywords = [seo_primary] + seo_secondary
        h2_text = " ".join(h2s).lower()
        keyword_in_h2 = any(kw.lower() in h2_text for kw in all_keywords if kw)
        if not keyword_in_h2:
            result.violations.append({
                "rule": "h2_keywords",
                "message": "No SEO keywords found in any H2 heading",
                "severity": "major",
            })
            result.score -= 8

    # === PARAGRAPH LENGTH ===
    paragraphs = _extract_paragraphs(text)
    long_paras = []
    for i, para in enumerate(paragraphs):
        sentences = re.split(r"[.!?]+", para)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 4:
            long_paras.append((i + 1, len(sentences)))

    if long_paras:
        for para_num, sent_count in long_paras:
            result.warnings.append({
                "rule": "paragraph_length",
                "message": f"Paragraph {para_num} has {sent_count} sentences (max 4)",
                "severity": "minor",
            })
            result.score -= 2

    # === SEO: KEYWORD IN FIRST 100 WORDS ===
    if seo_primary:
        first_100 = " ".join(text.split()[:100]).lower()
        if seo_primary.lower() not in first_100:
            result.violations.append({
                "rule": "keyword_first_100",
                "message": f"Primary keyword '{seo_primary}' not in first 100 words",
                "severity": "major",
            })
            result.score -= 8

    # === SEO: KEYWORD FREQUENCY ===
    if seo_primary:
        count = _count_keyword(text, seo_primary)
        result.metrics["primary_keyword_count"] = count

        if count < 3:
            result.violations.append({
                "rule": "keyword_frequency_low",
                "message": f"Primary keyword '{seo_primary}' appears only {count}x (min 3)",
                "severity": "major",
            })
            result.score -= 8
        elif count > 10:
            result.warnings.append({
                "rule": "keyword_stuffing",
                "message": f"Primary keyword appears {count}x — may be keyword stuffing",
                "severity": "minor",
            })
            result.score -= 5

    # === LINKS ===
    links = _extract_links(text)
    result.metrics["link_count"] = len(links)

    # Check for links in first paragraph
    if first_para:
        first_para_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", first_para)
        if first_para_links:
            result.violations.append({
                "rule": "link_first_paragraph",
                "message": "Link found in first paragraph (algorithm penalty)",
                "severity": "major",
            })
            result.score -= 8

    # === HASHTAGS ===
    # Look for hashtags in last few lines
    last_lines = "\n".join(text.strip().split("\n")[-5:])
    hashtags = re.findall(r"#(\w+)", last_lines)
    result.metrics["hashtag_count"] = len(hashtags)

    if len(hashtags) > 7:
        result.violations.append({
            "rule": "too_many_hashtags",
            "message": f"{len(hashtags)} hashtags (max 7, target 3-5)",
            "severity": "major",
        })
        result.score -= 8
    elif len(hashtags) == 0:
        result.warnings.append({
            "rule": "no_hashtags",
            "message": "No hashtags found — add 3-5 at article end",
            "severity": "minor",
        })
        result.score -= 3

    # === EMOJI CHECK ===
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]"
    )
    emojis = emoji_pattern.findall(text)
    if emojis:
        result.violations.append({
            "rule": "emoji",
            "message": f"Emoji detected: {' '.join(emojis)}",
            "severity": "major",
        })
        result.score -= 8

    # === CTA COUNT ===
    # Count CTA-like patterns
    cta_patterns = re.findall(
        r"\b(read it here|get it here|download|sign up|subscribe|join|register|buy now)\b",
        text,
        re.IGNORECASE,
    )
    if len(cta_patterns) > 2:
        result.warnings.append({
            "rule": "multiple_ctas",
            "message": f"Found {len(cta_patterns)} CTA-like phrases (target: 1)",
            "severity": "minor",
        })
        result.score -= 3

    # Clamp and finalize
    result.score = max(0, result.score)
    result.passed = result.score >= 85

    return result


def format_report(result: LinkedInResult) -> str:
    """Format LinkedIn check result as readable report."""
    lines = [
        "## LinkedIn Platform Check",
        f"**Score: {result.score}/100** {'PASS' if result.passed else 'FAIL'}",
        "",
        "### Metrics",
    ]

    for key, val in result.metrics.items():
        lines.append(f"- {key}: {val}")
    lines.append("")

    if result.violations:
        lines.append(f"### Violations ({len(result.violations)})")
        for v in result.violations:
            lines.append(f"- **[{v['severity'].upper()}]** {v['message']}")
        lines.append("")

    if result.warnings:
        lines.append(f"### Warnings ({len(result.warnings)})")
        for w in result.warnings:
            lines.append(f"- **[{w['severity'].upper()}]** {w['message']}")
        lines.append("")

    if not result.violations and not result.warnings:
        lines.append("All platform checks passed.")

    return "\n".join(lines)

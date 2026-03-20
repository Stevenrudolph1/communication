"""
Publish Gate — Final 4-check gate before article goes to Steven

Every article must pass ALL four checks:
1. Plain-language pass (no framework jargon)
2. ≥2 concrete examples (specific, recognizable)
3. Single clear CTA (one link, one action)
4. Companion post + DM trigger ready
"""

import re
from dataclasses import dataclass, field


@dataclass
class PublishGateResult:
    checks: dict = field(default_factory=dict)
    passed: bool = False
    summary: str = ""


# Framework jargon that should NOT appear in the article body
# (These are OK in the book title at the CTA, not in the body)
FRAMEWORK_JARGON = [
    r"\brenergence\b",
    r"\bmultiple natures\b",
    r"\bMNTEST\b",
    r"\bheroes not required\b",
    r"\bS/?A/?P\b",  # Structure/Alignment/Positioning
    r"\bmode collapse\b",
    r"\bpersonalization error\b",
    r"\bload[- ]bearing wall\b",
    r"\bstructural absence\b",
    r"\bmanufactured energy\b",
    r"\bquiet depletion\b",
    r"\bdiagnostic domain\b",
    r"\benergetic engagement\b",  # OK in MN article context, flagged for review
    r"\binteraction grammar\b",
    r"\btrait grammar\b",
    r"\btemporal deception\b",
]


def _check_plain_language(text: str, cta_section: str = "") -> dict:
    """
    Check 1: No framework jargon in article body.

    CTA section is excluded (book titles are OK there).
    Auto-detects CTA section as the last 2 paragraphs (where book titles live).
    """
    # Remove CTA section from check
    body = text
    if cta_section:
        body = text.replace(cta_section, "")
    else:
        # Auto-detect: strip everything after the last H2 or last 500 chars
        # (CTA lives at the end with book title mentions)
        paragraphs = text.strip().split("\n\n")
        if len(paragraphs) > 3:
            # Exclude last 3 paragraphs (likely CTA + hashtags + book mention)
            body = "\n\n".join(paragraphs[:-3])

    found_jargon = []
    for pattern in FRAMEWORK_JARGON:
        matches = re.findall(pattern, body, re.IGNORECASE)
        if matches:
            found_jargon.extend(matches)

    return {
        "name": "Plain Language",
        "passed": len(found_jargon) == 0,
        "details": (
            f"Framework jargon found in body: {', '.join(found_jargon)}"
            if found_jargon
            else "No framework jargon detected in article body"
        ),
    }


def _check_concrete_examples(text: str) -> dict:
    """
    Check 2: At least 2 concrete examples.

    Heuristic: Look for protagonist markers (she/he/they + past tense verb),
    specific details (numbers, timeframes, job titles), and scenario language.
    """
    # Protagonist patterns
    protagonist_patterns = [
        r"\b(she|he|they|a friend|a colleague|a client|a director|a manager|a founder|someone I)\b.*\b(took|left|started|told|said|joined|built|ran|managed|noticed|realized|discovered)\b",
    ]

    # Specific detail markers
    detail_patterns = [
        r"\b\d+\s+(years?|months?|weeks?|hours?|people|employees|clients|teams?)\b",
        r"\b(senior|junior|VP|director|manager|founder|CEO|HR|L&D)\b",
        r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|9pm|morning|quarter)\b",
    ]

    protagonists = 0
    for pattern in protagonist_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        protagonists += len(matches)

    details = 0
    for pattern in detail_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        details += len(matches)

    # Estimate: need protagonist + details for a "concrete example"
    estimated_examples = min(protagonists, max(1, details // 2))

    return {
        "name": "Concrete Examples",
        "passed": estimated_examples >= 2,
        "details": (
            f"Estimated {estimated_examples} concrete examples "
            f"({protagonists} protagonist markers, {details} specific details). "
            f"{'PASS' if estimated_examples >= 2 else 'FAIL — need ≥2'}"
        ),
    }


def _check_single_cta(text: str) -> dict:
    """
    Check 3: Single clear CTA (one link, one action).
    """
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    cta_phrases = re.findall(
        r"\b(read it here|get it here|free at|available at|download|sign up)\b",
        text,
        re.IGNORECASE,
    )

    link_count = len(links)
    cta_count = len(cta_phrases)

    return {
        "name": "Single CTA",
        "passed": link_count <= 2 and cta_count <= 2,
        "details": (
            f"{link_count} links, {cta_count} CTA phrases found. "
            f"{'PASS' if link_count <= 2 and cta_count <= 2 else 'FAIL — too many CTAs/links'}"
        ),
    }


def _check_companion_ready(companion_post: str = "", dm_triggers: str = "") -> dict:
    """
    Check 4: Companion post and DM triggers are drafted.
    """
    has_post = bool(companion_post and len(companion_post.strip()) > 50)
    has_triggers = bool(dm_triggers and len(dm_triggers.strip()) > 20)

    return {
        "name": "Companion Post + DM Triggers",
        "passed": has_post and has_triggers,
        "details": (
            f"Companion post: {'Ready ({} chars)'.format(len(companion_post)) if has_post else 'MISSING'}, "
            f"DM triggers: {'Ready' if has_triggers else 'MISSING'}"
        ),
    }


def check_publish_gate(
    article_text: str,
    cta_section: str = "",
    companion_post: str = "",
    dm_triggers: str = "",
) -> PublishGateResult:
    """
    Run the 4-check publish gate.

    Returns PublishGateResult with individual check results and overall pass/fail.
    """
    result = PublishGateResult()

    result.checks["plain_language"] = _check_plain_language(article_text, cta_section)
    result.checks["concrete_examples"] = _check_concrete_examples(article_text)
    result.checks["single_cta"] = _check_single_cta(article_text)
    result.checks["companion_ready"] = _check_companion_ready(companion_post, dm_triggers)

    all_passed = all(c["passed"] for c in result.checks.values())
    result.passed = all_passed

    passed_count = sum(1 for c in result.checks.values() if c["passed"])
    result.summary = f"{passed_count}/4 checks passed. {'READY FOR REVIEW' if all_passed else 'NOT READY'}"

    return result


def format_report(result: PublishGateResult) -> str:
    """Format publish gate result as readable report."""
    lines = [
        "## Publish Gate",
        f"**{result.summary}**",
        "",
    ]

    for key, check in result.checks.items():
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"### {check['name']}: {status}")
        lines.append(f"{check['details']}")
        lines.append("")

    return "\n".join(lines)

"""
Voice Checker — GOV-06 Brand Voice Compliance

Scans article text for prohibited language patterns, trait grammar,
and voice drift. Returns a score and list of violations.
"""

import re
from dataclasses import dataclass, field


@dataclass
class VoiceResult:
    score: int = 100
    violations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    passed: bool = True


# Prohibited patterns: (regex, category, severity)
PROHIBITED_PATTERNS = [
    # Self-help / empowerment
    (r"\byou'?ve got this\b", "self-help", "critical"),
    (r"\bbelieve in yourself\b", "self-help", "critical"),
    (r"\bunlock your potential\b", "self-help", "critical"),
    (r"\byou can do it\b", "self-help", "critical"),
    (r"\bempower(ing|ed|ment)?\b", "self-help", "major"),
    (r"\btransform(ative|ational|ing)?\b", "self-help", "major"),
    (r"\bjourney\b", "self-help", "minor"),
    (r"\bauthentic self\b", "self-help", "critical"),
    (r"\binner strength\b", "self-help", "critical"),
    (r"\bself-care\b", "self-help", "minor"),
    (r"\bmindset shift\b", "self-help", "major"),
    (r"\bgrowth mindset\b", "self-help", "major"),

    # Urgency / scarcity
    (r"\blimited time\b", "urgency", "critical"),
    (r"\bdon'?t miss out\b", "urgency", "critical"),
    (r"\bact now\b", "urgency", "critical"),
    (r"\bbefore it'?s too late\b", "urgency", "critical"),
    (r"\bonly \d+ (spots?|seats?|places?) left\b", "urgency", "critical"),

    # Promotional
    (r"\brevolutionary\b", "promotional", "critical"),
    (r"\bgame[- ]chang(er|ing)\b", "promotional", "critical"),
    (r"\bworld[- ]class\b", "promotional", "critical"),
    (r"\bgroundbreaking\b", "promotional", "critical"),
    (r"\bcutting[- ]edge\b", "promotional", "major"),
    (r"\binnovative\b", "promotional", "minor"),
    (r"\bunique(ly)?\b", "promotional", "minor"),
    (r"\bpowerful\b", "promotional", "minor"),

    # Pop-psychology
    (r"\btoxic\b", "pop-psych", "major"),
    (r"\bgaslight(ing|ed)?\b", "pop-psych", "critical"),
    (r"\bsetting intentions\b", "pop-psych", "critical"),
    (r"\btrauma response\b", "pop-psych", "major"),
    (r"\binner child\b", "pop-psych", "critical"),
    (r"\bnarcissis(t|tic|m)\b", "pop-psych", "major"),
    (r"\bboundaries\b", "pop-psych", "minor"),
    (r"\bself-worth\b", "pop-psych", "minor"),

    # Hedging
    (r"\bperhaps\b", "hedging", "minor"),
    (r"\bit could be argued\b", "hedging", "major"),
    (r"\bit seems\b", "hedging", "minor"),
    (r"\bmaybe\b", "hedging", "minor"),
    (r"\bI think\b", "hedging", "minor"),
    (r"\bin my opinion\b", "hedging", "minor"),

    # Prescriptive
    (r"\byou should\b", "prescriptive", "critical"),
    (r"\btry this\b", "prescriptive", "critical"),
    (r"\bhere'?s what to do\b", "prescriptive", "critical"),
    (r"\b\d+ steps? to\b", "prescriptive", "major"),
    (r"\b\d+ ways? to\b", "prescriptive", "major"),
    (r"\b\d+ tips?\b", "prescriptive", "major"),
    (r"\b\d+ signs? (you|that|of)\b", "prescriptive", "major"),
    (r"\bthe solution is\b", "prescriptive", "major"),
    (r"\byou need to\b", "prescriptive", "major"),
    (r"\bstart by\b", "prescriptive", "minor"),
    (r"\bask yourself\b", "prescriptive", "minor"),

    # Trait grammar
    (r"\byou are (a|an) \w+ (person|type|personality)\b", "trait-grammar", "critical"),
    (r"\byou'?re (a|an) \w+ (person|type|personality)\b", "trait-grammar", "critical"),
    (r"\byour personality (is|type)\b", "trait-grammar", "major"),
    (r"\byou'?re (naturally|inherently|fundamentally)\b", "trait-grammar", "major"),

    # Engagement bait
    (r"\blike if you agree\b", "engagement-bait", "critical"),
    (r"\bshare if\b", "engagement-bait", "critical"),
    (r"\bcomment below\b", "engagement-bait", "major"),
    (r"\btag someone\b", "engagement-bait", "critical"),
    (r"\bwho else\b", "engagement-bait", "minor"),

    # Emoji (any emoji character)
    (r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]", "emoji", "major"),
]

# Severity weights
SEVERITY_DEDUCTIONS = {
    "critical": 15,
    "major": 8,
    "minor": 3,
}


def check_voice(text: str) -> VoiceResult:
    """
    Run GOV-06 voice compliance check on article text.

    Returns VoiceResult with score, violations, and pass/fail.
    """
    result = VoiceResult()

    for pattern, category, severity in PROHIBITED_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get surrounding context (30 chars each side)
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end].replace("\n", " ").strip()

            violation = {
                "match": match.group(),
                "category": category,
                "severity": severity,
                "context": f"...{context}...",
            }

            if severity == "minor":
                result.warnings.append(violation)
            else:
                result.violations.append(violation)

            result.score -= SEVERITY_DEDUCTIONS[severity]

    # Clamp score
    result.score = max(0, result.score)
    result.passed = result.score >= 85

    return result


def format_report(result: VoiceResult) -> str:
    """Format voice check result as readable report."""
    lines = [
        "## Voice Check (GOV-06)",
        f"**Score: {result.score}/100** {'PASS' if result.passed else 'FAIL'}",
        "",
    ]

    if result.violations:
        lines.append(f"### Violations ({len(result.violations)})")
        for v in result.violations:
            lines.append(
                f"- **[{v['severity'].upper()}]** `{v['match']}` ({v['category']})"
                f"\n  Context: {v['context']}"
            )
        lines.append("")

    if result.warnings:
        lines.append(f"### Warnings ({len(result.warnings)})")
        for w in result.warnings:
            lines.append(
                f"- **[{w['severity'].upper()}]** `{w['match']}` ({w['category']})"
                f"\n  Context: {w['context']}"
            )
        lines.append("")

    if not result.violations and not result.warnings:
        lines.append("No violations or warnings detected.")

    return "\n".join(lines)

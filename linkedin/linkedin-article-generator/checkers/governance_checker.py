"""
Governance Checker — renOS Practitioner Invariants + Marketing Governance

Checks article content against:
1. Five practitioner invariants (no identity hardening, no moralized fit, etc.)
2. Marketing governance (encounter creation model, content ratio)
3. Domain non-collapse (GOV-11)
"""

import re
from dataclasses import dataclass, field


@dataclass
class GovernanceResult:
    score: int = 100
    violations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    passed: bool = True


# === Practitioner Invariant Patterns ===

# Invariant 1: You describe, you don't define (no identity hardening)
IDENTITY_HARDENING = [
    (r"\byou are (a|an|the) \w+\b", "Identity hardening: 'you are a [type]'"),
    (r"\byou'?re (a|an|the) \w+ at (heart|core)\b", "Identity hardening: 'you're a [X] at heart'"),
    (r"\byour true (self|nature|calling)\b", "Identity hardening: 'your true [X]'"),
    (r"\bwho you really are\b", "Identity hardening: 'who you really are'"),
    (r"\byour (type|profile|category) is\b", "Identity hardening: 'your type is'"),
    (r"\bborn to\b", "Identity hardening: 'born to'"),
    (r"\bmeant to be\b", "Identity hardening: 'meant to be'"),
    (r"\bdestined (to|for)\b", "Identity hardening: 'destined to/for'"),
]

# Invariant 2: Fit is not merit (no moralizing about match)
MORALIZED_FIT = [
    (r"\bthe right (job|role|career|path|place)\b", "Moralized fit: 'the right [X]'"),
    (r"\bperfect (fit|match|role)\b", "Moralized fit: 'perfect fit'"),
    (r"\bwhere you belong\b", "Moralized fit: 'where you belong'"),
    (r"\bfind your (calling|purpose|passion)\b", "Moralized fit: 'find your [X]'"),
    (r"\byou deserve (better|more)\b", "Moralized fit: 'you deserve [X]'"),
]

# Invariant 3: You can name cost, can't place person (no destination suggestion)
PLACEMENT = [
    (r"\byou (should|need to|must) (leave|quit|stay|change|find)\b", "Placement: directive to act"),
    (r"\bit'?s time to (move on|leave|quit|change)\b", "Placement: 'it's time to [X]'"),
    (r"\bthe answer is (to|clear)\b", "Placement: 'the answer is'"),
    (r"\bhere'?s what (you|to) (need|should|do)\b", "Placement: prescriptive"),
    (r"\bthe first step is\b", "Placement: prescriptive steps"),
]

# Invariant 4: Structure explains suffering, doesn't excuse or moralize it
MORALIZING = [
    (r"\bit'?s (not )?(your|their) fault\b", "Moralizing: fault assignment"),
    (r"\bthey (failed|chose|deserved)\b", "Moralizing: blame assignment"),
    (r"\byou (failed|chose wrong|made a mistake)\b", "Moralizing: self-blame"),
    (r"\bshould have (known|left|stayed|seen)\b", "Moralizing: should have"),
]

# Invariant 5: Nothing predicts what happens next (no trajectories)
TRAJECTORIES = [
    (r"\bif you (do this|follow|apply|implement), you'?ll\b", "Trajectory: promised outcome"),
    (r"\bthis will (change|transform|fix|solve|improve)\b", "Trajectory: guaranteed outcome"),
    (r"\bguarantee[ds]?\b", "Trajectory: guarantee"),
    (r"\bresults (include|are)\b", "Trajectory: promised results"),
    (r"\byou'?ll (finally|eventually|soon)\b", "Trajectory: predicted future"),
]

# === Marketing Governance Patterns ===

# Hard CTA in body (not at end)
HARD_CTA = [
    (r"\bsign up (now|today|here)\b", "Hard CTA: 'sign up [X]'"),
    (r"\bregister (now|today|here)\b", "Hard CTA: 'register [X]'"),
    (r"\bbuy (now|today)\b", "Hard CTA: 'buy [X]'"),
    (r"\bget started (now|today)\b", "Hard CTA: 'get started [X]'"),
    (r"\bdon'?t wait\b", "Hard CTA: urgency"),
    (r"\bclick (here|now|below)\b", "Hard CTA: 'click [X]'"),
]

# Domain collapse (GOV-11): "structural" used as shorthand for all three domains
DOMAIN_COLLAPSE = [
    (r"\bstructural diagnostic (report|training|method|approach|system)\b",
     "Domain collapse (GOV-11): 'structural diagnostic [X]' — use 'diagnostic [X]' when covering S/A/P"),
    (r"\bstructural clarity\b",
     "Domain collapse (GOV-11): 'structural clarity' — if meaning all-domain clarity, use 'diagnostic clarity'"),
]

ALL_PATTERNS = [
    ("invariant_1_identity", IDENTITY_HARDENING, "critical"),
    ("invariant_2_fit", MORALIZED_FIT, "major"),
    ("invariant_3_placement", PLACEMENT, "critical"),
    ("invariant_4_moralizing", MORALIZING, "major"),
    ("invariant_5_trajectory", TRAJECTORIES, "critical"),
    ("hard_cta", HARD_CTA, "critical"),
    ("domain_collapse", DOMAIN_COLLAPSE, "critical"),
]

SEVERITY_DEDUCTIONS = {
    "critical": 15,
    "major": 8,
    "minor": 3,
}


def check_governance(text: str) -> GovernanceResult:
    """
    Run governance compliance check on article text.

    Returns GovernanceResult with score, violations, and pass/fail.
    """
    result = GovernanceResult()

    for category, patterns, severity in ALL_PATTERNS:
        for pattern, description in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].replace("\n", " ").strip()

                violation = {
                    "match": match.group(),
                    "category": category,
                    "description": description,
                    "severity": severity,
                    "context": f"...{context}...",
                }

                if severity == "minor":
                    result.warnings.append(violation)
                else:
                    result.violations.append(violation)

                result.score -= SEVERITY_DEDUCTIONS[severity]

    result.score = max(0, result.score)
    result.passed = result.score >= 85

    return result


def format_report(result: GovernanceResult) -> str:
    """Format governance check result as readable report."""
    lines = [
        "## Governance Check (renOS + Marketing)",
        f"**Score: {result.score}/100** {'PASS' if result.passed else 'FAIL'}",
        "",
    ]

    if result.violations:
        lines.append(f"### Violations ({len(result.violations)})")
        for v in result.violations:
            lines.append(
                f"- **[{v['severity'].upper()}]** {v['description']}"
                f"\n  Match: `{v['match']}`"
                f"\n  Context: {v['context']}"
            )
        lines.append("")

    if result.warnings:
        lines.append(f"### Warnings ({len(result.warnings)})")
        for w in result.warnings:
            lines.append(
                f"- **[{w['severity'].upper()}]** {w['description']}"
                f"\n  Match: `{w['match']}`"
            )
        lines.append("")

    if not result.violations and not result.warnings:
        lines.append("All governance checks passed. No invariant violations detected.")

    return "\n".join(lines)

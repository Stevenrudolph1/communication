#!/usr/bin/env python3
"""
LinkedIn Article Generator — Main Pipeline

6-phase pipeline for producing governed LinkedIn Articles:

  Phase 1: CONSTITUTION    Load governance + article plan + book source
  Phase 2: DRAFT           Generate article from constitution + prompts
  Phase 3: EDITORIAL       Multi-pass editing (voice, clarity, platform, SEO, cadence)
  Phase 4: COMPLIANCE      Automated checkers (voice, linkedin, governance, publish gate)
  Phase 5: COMPANION       Generate companion post + DM triggers
  Phase 6: OUTPUT          Final article + audit trail for Steven review

Usage:
    python3 generate.py --article 1
    python3 generate.py --article 1 --check-only
    python3 generate.py --article 1 --phase editorial
    python3 generate.py --article 1 --check-file path/to/article.md

This script orchestrates the pipeline. The actual generation is done by
Claude Code (or another LLM) using the prompts and constitution. The
checkers run locally as Python validators.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import ARTICLES, OUTPUT_ROOT, PROMPTS_ROOT, EDITORIAL_PASS_THRESHOLD, MAX_REVISION_ROUNDS
from constitution import load_constitution, load_book_context
from checkers.voice_checker import check_voice, format_report as voice_report
from checkers.linkedin_checker import check_linkedin, format_report as linkedin_report
from checkers.governance_checker import check_governance, format_report as governance_report
from checkers.publish_gate import check_publish_gate, format_report as gate_report


def get_article_dir(article_num: int) -> Path:
    """Get or create output directory for an article."""
    dirname = f"article-{article_num:02d}"
    article_dir = OUTPUT_ROOT / dirname
    article_dir.mkdir(parents=True, exist_ok=True)
    return article_dir


def load_article_text(path: Path) -> str:
    """Load article text from file."""
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def run_checkers(
    article_text: str,
    article_num: int,
    companion_post: str = "",
    dm_triggers: str = "",
) -> dict:
    """
    Run all 4 checkers on article text.

    Returns dict with results and overall pass/fail.
    """
    article = ARTICLES.get(article_num, {})

    # Voice check
    voice_result = check_voice(article_text)

    # LinkedIn platform check
    linkedin_result = check_linkedin(
        article_text,
        seo_primary=article.get("seo_primary", ""),
        seo_secondary=article.get("seo_secondary", []),
        article_type=article.get("type", "pillar"),
    )

    # Governance check
    gov_result = check_governance(article_text)

    # Publish gate
    gate_result = check_publish_gate(
        article_text,
        companion_post=companion_post,
        dm_triggers=dm_triggers,
    )

    # Build report
    report = "\n\n---\n\n".join([
        f"# Compliance Report — Article {article_num}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Article:** {article.get('title', 'Unknown')}",
        "",
        voice_report(voice_result),
        linkedin_report(linkedin_result),
        governance_report(gov_result),
        gate_report(gate_result),
    ])

    # Overall
    all_passed = all([
        voice_result.passed,
        linkedin_result.passed,
        gov_result.passed,
        gate_result.passed,
    ])

    scores = {
        "voice": voice_result.score,
        "linkedin": linkedin_result.score,
        "governance": gov_result.score,
        "publish_gate": "PASS" if gate_result.passed else "FAIL",
    }

    report += f"\n\n---\n\n## Overall: {'ALL CHECKS PASSED' if all_passed else 'CHECKS FAILED'}\n\n"
    report += f"| Checker | Score |\n|---------|-------|\n"
    for name, score in scores.items():
        report += f"| {name} | {score} |\n"

    return {
        "passed": all_passed,
        "scores": scores,
        "report": report,
        "voice": voice_result,
        "linkedin": linkedin_result,
        "governance": gov_result,
        "gate": gate_result,
    }


def phase_1_constitution(article_num: int) -> str:
    """Phase 1: Load constitution."""
    print(f"\n{'='*60}")
    print(f"PHASE 1: CONSTITUTION — Article {article_num}")
    print(f"{'='*60}\n")

    constitution = load_constitution(article_num)
    article = ARTICLES.get(article_num, {})
    book_context = load_book_context(article.get("book", ""))

    print(f"Constitution loaded: {len(constitution)} chars")
    print(f"Book context: {book_context}")
    print(f"Article: {article.get('title', 'Unknown')}")
    print(f"Type: {article.get('type', 'Unknown')}")
    print(f"SEO primary: {article.get('seo_primary', 'None')}")

    # Save constitution for reference
    article_dir = get_article_dir(article_num)
    (article_dir / "constitution.md").write_text(constitution, encoding="utf-8")
    print(f"\nConstitution saved to: {article_dir / 'constitution.md'}")

    return constitution


def phase_4_compliance(article_num: int, article_path: Path = None) -> dict:
    """Phase 4: Run compliance checkers."""
    print(f"\n{'='*60}")
    print(f"PHASE 4: COMPLIANCE — Article {article_num}")
    print(f"{'='*60}\n")

    article_dir = get_article_dir(article_num)

    # Find article text
    if article_path:
        text = load_article_text(article_path)
    else:
        # Look for latest draft in article dir
        candidates = sorted(article_dir.glob("draft-v*.md"), reverse=True)
        if candidates:
            text = load_article_text(candidates[0])
            print(f"Using: {candidates[0]}")
        elif (article_dir / "final.md").exists():
            text = load_article_text(article_dir / "final.md")
            print(f"Using: {article_dir / 'final.md'}")
        else:
            print("ERROR: No article draft found. Run Phase 2 first.")
            sys.exit(1)

    # Load companion post if exists
    companion_post = ""
    companion_path = article_dir / "companion-post.md"
    if companion_path.exists():
        companion_post = companion_path.read_text(encoding="utf-8")

    # Run all checkers
    results = run_checkers(
        text,
        article_num,
        companion_post=companion_post,
        dm_triggers=companion_post,  # DM triggers are in companion post file
    )

    # Save report
    report_path = article_dir / "compliance-report.md"
    report_path.write_text(results["report"], encoding="utf-8")
    print(f"\nCompliance report saved to: {report_path}")

    # Print summary
    print(f"\n{'─'*40}")
    print(f"RESULTS:")
    for name, score in results["scores"].items():
        status = "PASS" if (isinstance(score, int) and score >= 85) or score == "PASS" else "FAIL"
        print(f"  {name:20s} {score:>6} {status}")
    print(f"{'─'*40}")
    print(f"Overall: {'ALL PASSED' if results['passed'] else 'FAILED — see report'}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Article Generator Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate.py --article 1                    # Full pipeline
  python3 generate.py --article 1 --check-only       # Run checkers only
  python3 generate.py --article 1 --constitution      # Print constitution only
  python3 generate.py --article 1 --check-file a.md  # Check a specific file
        """,
    )
    parser.add_argument("--article", "-a", type=int, required=True,
                        help="Article number (1-6)")
    parser.add_argument("--check-only", action="store_true",
                        help="Run compliance checkers only (skip generation)")
    parser.add_argument("--check-file", type=str,
                        help="Path to article file to check")
    parser.add_argument("--constitution", action="store_true",
                        help="Print constitution and exit")
    parser.add_argument("--phase", type=str,
                        choices=["constitution", "draft", "editorial", "compliance", "companion"],
                        help="Run from a specific phase")

    args = parser.parse_args()

    if args.article not in ARTICLES:
        print(f"ERROR: Article {args.article} not found. Valid: {list(ARTICLES.keys())}")
        sys.exit(1)

    # Constitution only
    if args.constitution:
        constitution = phase_1_constitution(args.article)
        print("\n" + constitution)
        return

    # Check only
    if args.check_only or args.check_file:
        check_path = Path(args.check_file) if args.check_file else None
        results = phase_4_compliance(args.article, check_path)
        sys.exit(0 if results["passed"] else 1)

    # Full pipeline (or from specific phase)
    start_phase = args.phase or "constitution"
    phases = ["constitution", "draft", "editorial", "compliance", "companion"]
    start_idx = phases.index(start_phase)

    for phase in phases[start_idx:]:
        if phase == "constitution":
            phase_1_constitution(args.article)

        elif phase == "draft":
            print(f"\n{'='*60}")
            print(f"PHASE 2: DRAFT — Article {args.article}")
            print(f"{'='*60}\n")
            article_dir = get_article_dir(args.article)
            print("Draft generation requires Claude Code or LLM.")
            print(f"System prompt: {PROMPTS_ROOT / 'system.md'}")
            print(f"Constitution: {article_dir / 'constitution.md'}")
            print(f"\nWrite draft to: {article_dir / 'draft-v1.md'}")
            print("\nThen re-run with: --phase editorial")
            return

        elif phase == "editorial":
            print(f"\n{'='*60}")
            print(f"PHASE 3: EDITORIAL — Article {args.article}")
            print(f"{'='*60}\n")
            print("Editorial passes require Claude Code or LLM.")
            print(f"Pass definitions: {PROMPTS_ROOT / 'editorial_passes.md'}")
            print(f"\n5 passes: Voice → Clarity → Platform → SEO → Cadence")
            print(f"Threshold: {EDITORIAL_PASS_THRESHOLD}/100 per pass")
            print(f"Max revisions: {MAX_REVISION_ROUNDS} rounds per pass")
            print(f"\nAfter editing, re-run with: --phase compliance")
            return

        elif phase == "compliance":
            results = phase_4_compliance(args.article)
            if not results["passed"]:
                print("\nFix violations and re-run: --phase compliance")
                sys.exit(1)

        elif phase == "companion":
            print(f"\n{'='*60}")
            print(f"PHASE 5: COMPANION — Article {args.article}")
            print(f"{'='*60}\n")
            print("Companion post generation requires Claude Code or LLM.")
            print(f"Prompt: {PROMPTS_ROOT / 'companion_post.md'}")
            article_dir = get_article_dir(args.article)
            print(f"\nWrite to: {article_dir / 'companion-post.md'}")

    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETE — Article {args.article}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

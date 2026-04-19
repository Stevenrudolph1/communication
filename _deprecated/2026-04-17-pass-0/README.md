# Deprecated — Pass 0 (2026-04-17)

Files deprecated during the system audit's Pass 0 cleanup.

## Contents (archived)

| File | Why deprecated | Replacement |
|------|---------------|-------------|
| `generate-article.sh` | Legacy bash wrapper that piped raw book excerpts to Claude. Replaced by kernel-based pipeline. | `communication/substack/produce-article.py` |

## Note

This file was lost during an initial Pass 0 delete but recovered from restic snapshot `9ae66747` (2026-04-16 backup). It was never git-tracked but IS in backup.

Confirm via: `produce-article.py:7` which says *"Replaces the old generate-article.sh which piped raw book excerpts to claude."*

## Related stale docs (to update in a later pass)

- `communication/substack/SUBSTACK-AUTOMATION-SPEC.md` — still references generate-article.sh as the active pipeline script. Spec is stale; actual pipeline is `produce-article.py`. Does not block Pass 0 but should be refreshed during Pass 2.
- `communication/substack/README.md` line 34 — lists generate-article.sh in the directory tree. Stale.

## Context

- `~/Projects/planning/system-audit/2026-04-17/03-dead-wood.md` (Tier A kill list)
- `~/Projects/planning/system-audit/2026-04-17/05-consolidation-plan.md` (Pass 0)

Can be restored if needed.

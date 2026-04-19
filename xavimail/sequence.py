"""sequence.py — XaviMail sequence engine

A sequence is an ordered series of emails sent to one or more lists.
Defined in sequences/<name>.yaml. Tracked in sequence_sends table.
"""

import sys
from pathlib import Path

import db
import send as send_mod
import render as render_mod

SEQUENCES_DIR = Path(__file__).parent / 'sequences'


def _yaml_load(path: Path) -> dict:
    """Minimal YAML parser — handles only the subset we use."""
    result = {}
    current_list_key = None
    current_steps = []
    in_lists = False
    in_steps = False
    current_step = {}

    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith('#'):
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent == 0:
            if stripped.startswith('name:'):
                result['name'] = stripped.split(':', 1)[1].strip()
                in_lists = in_steps = False
            elif stripped.startswith('description:'):
                result['description'] = stripped.split(':', 1)[1].strip()
                in_lists = in_steps = False
            elif stripped == 'lists:':
                in_lists = True
                in_steps = False
                result['lists'] = {}
            elif stripped == 'steps:':
                in_steps = True
                in_lists = False
                result['steps'] = []
        elif in_lists and indent == 2:
            key, _, val = stripped.partition(':')
            result['lists'][key.strip()] = val.strip()
        elif in_steps:
            if stripped.startswith('- num:'):
                if current_step:
                    result['steps'].append(current_step)
                current_step = {'num': int(stripped.split(':', 1)[1].strip())}
            elif stripped.startswith('en:'):
                current_step['en'] = stripped.split(':', 1)[1].strip()
            elif stripped.startswith('fr:'):
                current_step['fr'] = stripped.split(':', 1)[1].strip()

    if current_step:
        result['steps'].append(current_step)

    return result


def load_sequence(name: str) -> dict:
    path = SEQUENCES_DIR / f'{name}.yaml'
    if not path.exists():
        available = [p.stem for p in SEQUENCES_DIR.glob('*.yaml')]
        raise FileNotFoundError(
            f"Sequence '{name}' not found. Available: {', '.join(available) or '(none)'}"
        )
    seq = _yaml_load(path)
    seq['_path'] = str(path)
    return seq


def list_sequences() -> list[dict]:
    seqs = []
    for path in sorted(SEQUENCES_DIR.glob('*.yaml')):
        try:
            seq = _yaml_load(path)
            seq['_path'] = str(path)
            seqs.append(seq)
        except Exception:
            pass
    return seqs


def sequence_status(seq: dict) -> list[dict]:
    """
    Return a list of dicts describing each step's send state across all lists.
    Each dict: {num, list_alias, list_name, file, subject, sent_at or None}
    """
    history = {
        (r['step_num'], r['list_name']): r['sent_at']
        for r in db.get_sequence_history(seq['name'])
    }
    rows = []
    for step in seq['steps']:
        for alias, list_name in seq['lists'].items():
            file_key = alias  # 'en' or 'fr'
            file_path = step.get(file_key)
            subject = None
            if file_path:
                try:
                    subject = render_mod.subject_from_file(
                        str(Path(__file__).parent / file_path)
                    )
                except Exception:
                    pass
            sent_at = history.get((step['num'], list_name))
            rows.append({
                'num': step['num'],
                'alias': alias,
                'list_name': list_name,
                'file': file_path,
                'subject': subject,
                'sent_at': sent_at,
            })
    return rows


def next_step(seq: dict) -> int | None:
    """Return the step number of the first step not fully sent to all lists."""
    history = {
        (r['step_num'], r['list_name'])
        for r in db.get_sequence_history(seq['name'])
    }
    for step in seq['steps']:
        for alias, list_name in seq['lists'].items():
            if (step['num'], list_name) not in history:
                return step['num']
    return None


def send_step(seq: dict, step_num: int, list_filter: str = None,
              dry_run: bool = False, confirm: bool = False) -> dict:
    """
    Send a specific step of a sequence.

    list_filter: 'en' or 'fr' alias — send to one list only.
    dry_run: preview without sending.
    confirm: skip the y/N prompt.
    """
    step = next((s for s in seq['steps'] if s['num'] == step_num), None)
    if not step:
        raise ValueError(f"Step {step_num} not found in sequence '{seq['name']}'")

    targets = {}
    for alias, list_name in seq['lists'].items():
        if list_filter and alias != list_filter:
            continue
        file_rel = step.get(alias)
        if not file_rel:
            continue
        file_abs = str(Path(__file__).parent / file_rel)
        already = db.sequence_step_sent(seq['name'], step_num, list_name)
        targets[alias] = {
            'list_name': list_name,
            'file': file_abs,
            'already_sent': already,
        }

    if not targets:
        print('No targets for this step (check list_filter or missing file paths).')
        return {}

    results = {}
    for alias, t in targets.items():
        list_name = t['list_name']

        if t['already_sent']:
            print(f'  Step {step_num} → {list_name}: already sent on {t["already_sent"]["sent_at"]}. Skipping.')
            print(f'  (Use --force to override — not yet implemented)')
            results[alias] = 'already_sent'
            continue

        subject = render_mod.subject_from_file(t['file'])
        if not subject:
            raise ValueError(
                f"No subject in frontmatter of {t['file']}. "
                f"Add '---\\nsubject: Your subject line\\n---' at the top."
            )

        result = send_mod.run_campaign(
            list_name=list_name,
            subject=subject,
            body_file=t['file'],
            dry_run=dry_run,
            test_to=None,
        )

        if not dry_run:
            # Record the send in sequence_sends
            sends = db.get_sends(limit=1)
            send_id = sends[0]['id'] if sends else None
            db.record_sequence_send(seq['name'], step_num, list_name, send_id)
            print(f'  ✓ Recorded: sequence={seq["name"]} step={step_num} list={list_name}')

        results[alias] = result

    return results

"""render.py — Markdown email files → plain text + HTML

Email files are plain Markdown. Template variables: {first_name}, {last_name},
{email}, {unsubscribe_url}.

No external dependencies — uses stdlib only.
"""

import re
from pathlib import Path


def load_body(path: str) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f'Email body not found: {path}')
    return p.read_text(encoding='utf-8')


def apply_context(text: str, context: dict) -> str:
    for key, value in context.items():
        text = text.replace('{' + key + '}', str(value or ''))
    return text


def to_plain_text(md: str) -> str:
    """Strip markdown syntax for plain text part."""
    text = md
    # Remove HTML tags if any crept in
    text = re.sub(r'<[^>]+>', '', text)
    # Headers → plain line
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Links: [text](url) → text (url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Horizontal rule
    text = re.sub(r'^---+$', '─' * 40, text, flags=re.MULTILINE)
    # Clean up excess blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def to_html(md: str) -> str:
    """Convert Markdown to minimal HTML for the HTML part."""
    lines = md.split('\n')
    html_lines = []
    in_p = False

    for line in lines:
        stripped = line.strip()

        # Blank line — close paragraph
        if not stripped:
            if in_p:
                html_lines.append('</p>')
                in_p = False
            html_lines.append('')
            continue

        # Headers
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            if in_p:
                html_lines.append('</p>')
                in_p = False
            level = len(m.group(1))
            html_lines.append(f'<h{level}>{_inline(m.group(2))}</h{level}>')
            continue

        # Horizontal rule
        if re.match(r'^---+$', stripped):
            if in_p:
                html_lines.append('</p>')
                in_p = False
            html_lines.append('<hr>')
            continue

        # Regular paragraph line
        if not in_p:
            html_lines.append('<p>')
            in_p = True
        else:
            html_lines.append('<br>')
        html_lines.append(_inline(stripped))

    if in_p:
        html_lines.append('</p>')

    body = '\n'.join(html_lines)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: Georgia, 'Times New Roman', serif; max-width: 580px;
           margin: 0 auto; padding: 24px 16px; color: #222; font-size: 16px; line-height: 1.65; }}
    p {{ margin: 0 0 1.1em 0; }}
    h1, h2, h3 {{ font-weight: bold; margin: 1.4em 0 0.4em 0; }}
    a {{ color: #333; }}
    hr {{ border: none; border-top: 1px solid #ddd; margin: 1.5em 0; }}
    .footer {{ margin-top: 2em; padding-top: 1em; border-top: 1px solid #eee;
               font-size: 0.8em; color: #888; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def _inline(text: str) -> str:
    """Apply inline markdown (bold, italic, links) to a line."""
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


UNSUBSCRIBE_FOOTER_PLAIN = """
─────────────────────────
You're receiving this because you're a trained MN practitioner.
To unsubscribe: {unsubscribe_url}
"""

UNSUBSCRIBE_FOOTER_HTML = """
<div class="footer">
  You're receiving this because you're a trained MN practitioner.
  <a href="{unsubscribe_url}">Unsubscribe</a>
</div>
"""


def render(body_path: str, context: dict) -> tuple[str, str]:
    """
    Render an email body file into (plain_text, html) with context applied.
    Context should include: first_name, last_name, email, unsubscribe_url.
    """
    raw = load_body(body_path)
    raw = apply_context(raw, context)

    plain = to_plain_text(raw)
    plain += UNSUBSCRIBE_FOOTER_PLAIN.format(unsubscribe_url=context.get('unsubscribe_url', ''))

    html_body = to_html(raw)
    footer_html = UNSUBSCRIBE_FOOTER_HTML.format(unsubscribe_url=context.get('unsubscribe_url', ''))
    # Insert footer before closing </body>
    html_body = html_body.replace('</body>', footer_html + '\n</body>')

    return plain, html_body

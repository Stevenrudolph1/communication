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


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Extract YAML frontmatter from email file.
    Returns (meta_dict, body_without_frontmatter).
    Supported keys: subject
    """
    meta = {}
    if not text.startswith('---'):
        return meta, text
    end = text.find('\n---', 3)
    if end == -1:
        return meta, text
    block = text[3:end].strip()
    for line in block.splitlines():
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip()
    body = text[end + 4:].lstrip('\n')
    return meta, body


def subject_from_file(path: str) -> str | None:
    """Return the subject line from a file's frontmatter, or None."""
    raw = load_body(path)
    meta, _ = parse_frontmatter(raw)
    return meta.get('subject')


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
    """Convert Markdown to HTML body content (no wrapper — added by render())."""
    lines = md.split('\n')
    html_lines = []
    in_p = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_p:
                html_lines.append('</p>')
                in_p = False
            html_lines.append('')
            continue

        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            if in_p:
                html_lines.append('</p>')
                in_p = False
            level = len(m.group(1))
            html_lines.append(f'<h{level}>{_inline(m.group(2))}</h{level}>')
            continue

        if re.match(r'^---+$', stripped):
            if in_p:
                html_lines.append('</p>')
                in_p = False
            html_lines.append('<hr>')
            continue

        if not in_p:
            html_lines.append('<p>')
            in_p = True
        else:
            html_lines.append('<br>')
        html_lines.append(_inline(stripped))

    if in_p:
        html_lines.append('</p>')

    return '\n'.join(html_lines)


def _wrap_html(body_content: str, footer_html: str, pixel_html: str = '') -> str:
    """Wrap rendered body + footer in the full HTML email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title></title>
  <style>
    body {{
      margin: 0; padding: 0;
      background-color: #f4f4f4;
      font-family: Georgia, 'Times New Roman', serif;
      color: #1a1a1a;
    }}
    .wrapper {{
      max-width: 580px;
      margin: 0 auto;
      background-color: #ffffff;
      padding: 40px 40px 32px 40px;
    }}
    p {{
      margin: 0 0 1.25em 0;
      font-size: 16px;
      line-height: 1.75;
      color: #1a1a1a;
    }}
    h1 {{ font-size: 24px; font-weight: bold; margin: 1.6em 0 0.5em 0; color: #1a1a1a; }}
    h2 {{ font-size: 20px; font-weight: bold; margin: 1.5em 0 0.5em 0; color: #1a1a1a; }}
    h3 {{ font-size: 17px; font-weight: bold; margin: 1.4em 0 0.4em 0; color: #1a1a1a; }}
    a {{ color: #1a1a1a; text-decoration: underline; }}
    hr {{ border: none; border-top: 1px solid #e8e8e8; margin: 1.8em 0; }}
    .footer {{
      margin-top: 2em;
      padding-top: 1em;
      border-top: 1px solid #e8e8e8;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 12px;
      color: #999999;
      line-height: 1.5;
    }}
    .footer a {{ color: #999999; }}
    @media (max-width: 620px) {{
      .wrapper {{ padding: 24px 20px 20px 20px; }}
    }}
  </style>
</head>
<body>
<div class="wrapper">
{body_content}
{footer_html}
</div>
{pixel_html}
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


UNSUBSCRIBE_FOOTER_PLAIN = (
    '\n─────────────────────────\n'
    "You're receiving this because you're a trained MN practitioner.\n"
    'To unsubscribe: {unsubscribe_url}\n'
)

_FOOTER_HTML_TMPL = (
    '<div class="footer">'
    "You're receiving this because you're a trained MN practitioner. &nbsp;"
    '<a href="{unsubscribe_url}">Unsubscribe</a>'
    '</div>'
)


def render(body_path: str, context: dict,
           send_id: int = None, api_base: str = None,
           mailer_secret: str = None) -> tuple[str, str]:
    """
    Render an email body into (plain_text, html).

    send_id / api_base / mailer_secret — when provided, injects open-tracking
    pixel and rewrites links through click tracker.
    """
    raw = load_body(body_path)
    _, raw = parse_frontmatter(raw)
    raw = apply_context(raw, context)

    # Plain text
    plain = to_plain_text(raw)
    plain += UNSUBSCRIBE_FOOTER_PLAIN.format(
        unsubscribe_url=context.get('unsubscribe_url', '')
    )

    # HTML body content
    body_content = to_html(raw)

    # Tracking: rewrite links and add open pixel when send_id is available
    pixel_html = ''
    if send_id and api_base and mailer_secret:
        email = context.get('email', '')
        body_content = _rewrite_links(body_content, send_id, email,
                                      api_base, mailer_secret,
                                      context.get('unsubscribe_url', ''))
        pixel_html = _open_pixel(send_id, email, api_base, mailer_secret)

    footer_html = _FOOTER_HTML_TMPL.format(
        unsubscribe_url=context.get('unsubscribe_url', '')
    )

    html = _wrap_html(body_content, footer_html, pixel_html)
    return plain, html


# ── Tracking helpers ─────────────────────────────────────────────────────────

import hashlib
import hmac as _hmac
import urllib.parse as _urlparse


def _track_sig(action: str, send_id: int, email: str, secret: str,
               url: str = '') -> str:
    msg = f'{action}:{send_id}:{email.lower()}'
    if url:
        msg += f':{url}'
    return _hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


def _open_pixel(send_id: int, email: str, api_base: str, secret: str) -> str:
    sig = _track_sig('open', send_id, email, secret)
    params = _urlparse.urlencode({'sid': send_id, 'email': email.lower(), 'sig': sig})
    url = f'{api_base.rstrip("/")}/mailer/track/open?{params}'
    return f'<img src="{url}" width="1" height="1" alt="" style="display:none">'


def _rewrite_links(html: str, send_id: int, email: str,
                   api_base: str, secret: str, unsub_url: str) -> str:
    """Rewrite <a href="..."> through click tracker, skip unsubscribe + mailto."""
    base = api_base.rstrip('/')

    def rewrite(match):
        original = match.group(1)
        if (original.startswith('mailto:') or
                original.startswith('#') or
                '/mailer/unsubscribe' in original or
                '/mailer/track/' in original):
            return match.group(0)
        sig = _track_sig('click', send_id, email, secret, url=original)
        params = _urlparse.urlencode({
            'sid': send_id, 'email': email.lower(),
            'url': original, 'sig': sig,
        })
        return f'href="{base}/mailer/track/click?{params}"'

    return re.sub(r'href="([^"]+)"', rewrite, html)

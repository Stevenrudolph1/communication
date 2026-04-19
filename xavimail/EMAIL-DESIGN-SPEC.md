# XaviMail Email Design Spec

## Philosophy
Personal, editorial, text-first. Emails read like a letter from a person, not a newsletter from a brand. No logo header. No decorative elements. The writing carries it.

## Template Anatomy
```
[580px centered card on #f4f4f4 background]
  40px padding top/sides
  ── body content ──
  [hr divider]
  [footer: unsubscribe · small grey text]
  40px padding bottom
```

## Typography
| Element     | Font                            | Size  | Weight | Color   |
|-------------|----------------------------------|-------|--------|---------|
| Body        | Georgia, 'Times New Roman', serif | 16px  | normal | #1a1a1a |
| H1          | Georgia, serif                   | 24px  | bold   | #1a1a1a |
| H2          | Georgia, serif                   | 20px  | bold   | #1a1a1a |
| H3          | Georgia, serif                   | 17px  | bold   | #1a1a1a |
| Footer      | Arial, sans-serif                | 12px  | normal | #999999 |
| Line height | —                                | —     | —      | 1.75    |

## Layout
- **Max width:** 580px
- **Background:** #f4f4f4 (page) / #ffffff (card)
- **Padding:** 40px top, 40px sides, 32px bottom (mobile: 24px/20px)
- **Paragraph spacing:** 1.25em bottom margin

## Links
- Color: #1a1a1a (same as body — understated, not blue)
- Underline: yes
- Hover: no special treatment (email clients don't reliably support :hover)

## Footer
- Separated by a light `<hr>` (#e8e8e8)
- Text: "You're receiving this because you're a trained MN practitioner."
- Unsubscribe link: plain text, same grey as footer
- Font: sans-serif (contrast with body serif)

## Template Variables
| Variable          | Example                     |
|-------------------|-----------------------------|
| `{first_name}`    | Christine                   |
| `{last_name}`     | Clifton                     |
| `{email}`         | christine@...               |
| `{unsubscribe_url}` | https://api.xavigate.com/... |

## Writing the Email File
```markdown
---
subject: Your subject line here
---
Hi {first_name},

First paragraph here.

Second paragraph here.

Steven
```

Frontmatter `---` block is stripped before rendering. Subject line is extracted from it.

## Supported Markdown
- `**bold**` → `<strong>`
- `*italic*` → `<em>`
- `[text](url)` → `<a href>`
- `# H1`, `## H2`, `### H3`
- `---` → `<hr>`
- Blank line → paragraph break

## What NOT to Do
- No HTML tables for layout
- No inline styles (use the template CSS)
- No images (except the invisible tracking pixel — added automatically)
- No custom fonts (email client support is unreliable)
- No header logo or brand bar at top

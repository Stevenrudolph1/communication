# MailerLite Campaigns

Email campaigns sent to practitioner and subscriber groups via MailerLite.

## Structure

```
mailerlite/
  templates/       ← Reusable HTML email templates
  campaigns/       ← Individual campaign HTML files (ready to send)
  sent/            ← Campaigns that have been sent (moved here after send)
  README.md        ← This file
```

## How to Send

```bash
# 1. Create campaign HTML in campaigns/
# 2. Test with Steven Rudolph group (you + Shriya)
mailerlite send --group "Steven Rudolph" --subject "Test: Subject" --html campaigns/file.html

# 3. Review in inbox
# 4. Send to real group
mailerlite send --group "MN practitioners" --subject "Subject" --html campaigns/file.html

# 5. Move to sent/
mv campaigns/file.html sent/
```

## Groups (Key)

| Group | Count | Use For |
|-------|-------|---------|
| Steven Rudolph | 2 | Testing (you + Shriya) |
| MN practitioners | 148 | All MN practitioners |
| french active practitioners | 91 | French practitioners |
| Non-french practitioners | 11 | Non-French practitioners |
| mail for nyn course practitioner | 47 | NYN course participants |

## Rules

1. Always test with "Steven Rudolph" group first
2. Move sent campaigns to `sent/` with date prefix
3. Campaign files are self-contained HTML (inline styles, no external deps)
4. From: steven@xavigate.com / Steven Rudolph

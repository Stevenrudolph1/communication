#!/bin/bash
# Intercepts xavimail send commands lacking --dry-run or --test-to.
# Blocks sends that would hit the full list and warns about missing [TEST] prefix.

COMMAND=$(jq -r '.tool_input.command // ""' 2>/dev/null)

# Only care about xavimail send commands
if ! echo "$COMMAND" | grep -qE 'xavimail.*send|xavimail\.py.*send'; then
  exit 0
fi

# Allow dry runs and test sends through
if echo "$COMMAND" | grep -qE '\-\-dry-run|\-\-test-to'; then
  exit 0
fi

# Full send without --live flag — block with explanation
cat <<'EOF'
{
  "continue": false,
  "stopReason": "⛔  LIVE SEND INTERCEPTED — xavimail.py requires --live flag + interactive confirmation to send to a full list. Add --dry-run to preview, or --test-to your address to test first."
}
EOF

#!/bin/bash
# Reads newsletter/draft.md and posts it to the AI Daily Notion page.
# Run this whenever the main newsletter session ends before reaching the Notion
# posting step (e.g. context exhaustion during research).
#
# Usage:
#   ./newsletter/post.sh
#
# After a successful post the draft file is cleared so the next run starts clean.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRAFT="$SCRIPT_DIR/draft.md"
NOTION_PARENT_ID="347cee621c3d8090be7cf83f7240b374"

# Server clock is UTC; newsletter dates must reflect Singapore time (UTC+8).
SGT_TODAY="$(TZ=Asia/Singapore date '+%Y-%m-%d')"
SGT_DATE="$(TZ=Asia/Singapore date -d "$SGT_TODAY" '+%A, %-d %B %Y')"
SGT_YESTERDAY="$(TZ=Asia/Singapore date -d "$SGT_TODAY - 1 day" '+%Y-%m-%d')"
SCAN_START="${SGT_YESTERDAY} 06:00 SGT"
SCAN_END="${SGT_TODAY} 06:00 SGT"

if [[ ! -f "$DRAFT" ]]; then
  echo "Error: $DRAFT does not exist." >&2
  exit 1
fi

if [[ ! -s "$DRAFT" ]]; then
  echo "Error: $DRAFT is empty — nothing to post." >&2
  exit 1
fi

DRAFT_CONTENT="$(cat "$DRAFT")"

claude --print "$(cat <<PROMPT
Post the following newsletter draft to Notion.

Parent page ID: $NOTION_PARENT_ID  (the "AI Daily" index page)
Icon: 🧠
Singapore date (use this, not UTC): $SGT_DATE
News scan window: $SCAN_START  →  $SCAN_END
Title: extract from the first heading or date line in the content below; if the
date in the draft differs from the Singapore date above, prefer the Singapore date.

Use the notion-create-pages tool. After the page is confirmed created, output the
word DONE on a line by itself.

--- DRAFT START ---
$DRAFT_CONTENT
--- DRAFT END ---
PROMPT
)"

# Clear the draft so stale content is not re-posted on the next run.
> "$DRAFT"
echo "Draft cleared."

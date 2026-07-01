#!/bin/bash
# Reads newsletter/draft.md and posts it to the AI Daily Notion page.
# Run this whenever the main newsletter session ends before reaching the Notion
# posting step (e.g. context exhaustion during research).
#
# The draft is written incrementally, one section at a time, and a finished draft
# ends with the marker line "<!-- AI-DAILY-COMPLETE -->". By default this script
# refuses to post a draft that lacks the marker (a partial briefing). Finish it in
# a resuming session first, or pass --partial to post as-is.
#
# Usage:
#   ./newsletter/post.sh              # post a complete draft
#   ./newsletter/post.sh --partial    # post whatever is in the draft, incomplete
#
# After a successful post the draft file is cleared so the next run starts clean.

set -euo pipefail

ALLOW_PARTIAL=0
if [[ "${1:-}" == "--partial" ]]; then
  ALLOW_PARTIAL=1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRAFT="$SCRIPT_DIR/draft.md"
COMPLETE_MARKER="<!-- AI-DAILY-COMPLETE -->"
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

# A finished draft ends with the completion marker. Refuse partial drafts unless
# --partial was passed.
if ! grep -qF "$COMPLETE_MARKER" "$DRAFT"; then
  if [[ "$ALLOW_PARTIAL" -eq 0 ]]; then
    echo "Error: $DRAFT has no completion marker — it looks partial." >&2
    echo "Finish the remaining sections in a resuming session, or re-run with" >&2
    echo "  ./newsletter/post.sh --partial" >&2
    echo "to post the incomplete draft as-is." >&2
    exit 1
  fi
  echo "Warning: posting a partial draft (--partial)." >&2
fi

# Strip the completion marker so it does not appear in the posted page.
DRAFT_CONTENT="$(grep -vF "$COMPLETE_MARKER" "$DRAFT")"

claude --print "$(cat <<PROMPT
Post the following newsletter draft to Notion.

Parent page ID: $NOTION_PARENT_ID  (the "AI Daily" index page)
Icon: 🧠
Singapore date (use this, not UTC): $SGT_DATE
News scan window: $SCAN_START  →  $SCAN_END
Title: extract from the first heading or date line in the content below; if the
date in the draft differs from the Singapore date above, prefer the Singapore date.

The draft is a full 10-section briefing (see newsletter/FORMAT.md). Post it
faithfully and in full — preserve every section, heading, list, and citation.
Do NOT summarise, truncate, or drop any section.

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

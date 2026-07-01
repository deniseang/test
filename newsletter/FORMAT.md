# AI Daily — Newsletter Format Specification

This is the canonical structure for the AI Daily briefing posted to Notion.
It is modelled on the full 10-section email briefing. The routine must produce
**all 10 sections** in this order. Reference example: "AI Daily — Full Briefing:
Wednesday, 1 Jul 2026 SGT".

## Page-level

- **Parent:** `347cee621c3d8090be7cf83f7240b374` (the "AI Daily" index page)
- **Icon:** 🧠
- **Title:** `AI Daily — {Weekday}, {D} {Month} {Year}` (SGT date — see CLAUDE.md)
- **Header line (first block):**
  `AI DAILY — {Weekday}, {D} {Month} {Year} SGT | Prepared for Denise Ang, CSO & Director, AI Central, HTX`

## Scan windows (per section)

| Section | Window |
|---------|--------|
| 1 Executive Summary | derived from all sections below |
| 2 Tier A | **strictly last 24h** — published after ~06:00 SGT previous day |
| 3 Tier B | past 7 days |
| 4 Tier C | past 7 days |
| 5 Model Landscape | current state as of posting day |
| 6 AI Agents & Tools | current state / past 7 days |
| 7 Blogs & Articles (official) | last 24h (previous day 06:00 → posting day 06:00 SGT) |
| 8 Substack posts | last 24h |
| 9 Tweets & X posts | last 24h |
| 10 New AI Products | past 7 days |

## The 10 sections

### 1. Executive Summary — "Top 10 things you should pay attention to this morning"
Numbered list 1–10. Each item: an emoji + bold headline, then a 2–4 sentence
paragraph ending with an HTX-relevant "so what". Lead with the single most
important story of the day (often Singapore/HTX-specific).

### 2. 🔥 TIER A — TOP 5 STORIES
State the rule line: *"Tier A = strictly last 24 hours (published after ~06:00
SGT {prev date}). Tier C = past 7 days."*
Then 5 stories, each formatted:
```
--- STORY {n}: {emoji} {headline}
[Date: {D Mon YYYY} | Source: {source} | Link]
{2–3 paragraph body}
HTX Tie-in: {actionable HTX-specific implication}
```

### 3. 📊 TIER B — STRATEGIC INTELLIGENCE (Past 7 Days)
Three audience subsections, each with a **Key Theme** and a **Talking Point**
(HTX AI Central also gets numbered **Technical Actions** for the week):
- `━━━ For MHA Leadership ━━━`
- `━━━ For Peer Agency Directors (SPF / ICA / SCDF / SPS) ━━━`
- `━━━ For HTX AI Central Staff ━━━`

### 4. 📋 TIER C — ADDITIONAL HEADLINES (Past 7 Days)
Numbered headlines grouped under themed subheads (include those that apply):
Security & Vulnerabilities · AI Policy & Regulation · Environment &
Sustainability · AI Industry · Market & Economy · China AI Strategy ·
Singapore & Regional AI Ecosystem.
Each item: `{emoji} {headline}` + `[Date | Source | Link]` + 1–2 sentences.

### 5. 🧭 MODEL LANDSCAPE
Grouped lists with a one-line status per model:
- **Frontier / Top Tier**
- **Mid-Tier / Specialist**
- **Open Source**
- **⚠️ Deprecation Notices** (model — date — migration path)
- **Notable talent moves** ({month})

### 6. 🤖 AI AGENTS & TOOLS LANDSCAPE
- **Major Commercial Agents** (numbered, with `[Date | Source | Link]`)
- **Agent Security — New Category**
- **Open-Source Agents**
- **Key Agent Platforms to Track** (inline pipe-separated list)

### 7. 📝 BLOGS & ARTICLES — AI Company Official Posts (Last 24h)
State the scan set: *"Scanned: Anthropic, OpenAI, Google DeepMind, Mistral AI,
xAI, Cursor, Meta AI, DeepSeek."* Group by company; each entry: title + date +
full URL + 1–2 sentence summary.

### 8. 📬 TOP AI SUBSTACK POSTS (Last 24h)
State the scan set (The Rundown AI, Import AI, Interconnects, Last Week in AI,
Superhuman AI, Ben's Bites, The Batch, Ahead of AI, EU AI Act Newsletter, etc.).
Group by theme (Policy & Regulation · Business & Strategy · Philosophy &
Society); each: title + author + date + URL + 1–2 sentence summary.

### 9. 🐦 TOP AI TWEETS & X POSTS (Last 24h)
State the scanned handles. Group by theme (Major Announcements · Policy &
Regulation · Research & Technical · Community & Narrative · AI Agents & Tools);
each: handle + date + URL + quoted post + 1-line significance.

### 10. 🛍️ NEW AI PRODUCTS LAUNCHED (Past 7 Days)
State the scan set (Product Hunt, TechCrunch, VentureBeat, Reuters, etc.).
Group (AI-for-Science & Enterprise · AI Agents · Major Deals); each: product +
date + URL + 1–2 sentence description.

**Then close with:**
- **📡 Source Coverage** — bulleted list of source groups scanned.
- Footer: `— AI Daily | HTX AI Strategic Intelligence | Generated: {D Mon YYYY} (SGT)`

## Notes

- Every story/headline carries an inline `[Date | Source | Link]` citation.
- HTX relevance ("HTX Tie-in" / "so what") is required on Tier A stories and the
  Executive Summary; strongly encouraged elsewhere.
- If a section genuinely has no qualifying items in-window, keep the section
  heading and state the null result explicitly (e.g. "No official posts in the
  last 24h.") — do not silently drop a section.

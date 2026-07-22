---
type: how_to_use
updated: 2026-07-22
---

# How to Use My Wine Vault

One box of note-cards (the GitHub repo). Everything reads from that one box —
no second copy anywhere. Three things you ever do: **read**, **ask**, **change**.

---

## The big idea (read this once)

- **One source of truth:** the GitHub repo `evanakarp-oss/wine_vault`.
- You **read** it in Obsidian, you **ask** it questions with Claude, and you
  **change** it by asking Claude Code. That's the whole system.
- There is **no Google Drive** and no second copy. (The old Drive mirror was
  retired 2026-07-22 — it was the thing that kept breaking.)

---

## 📖 READ — Obsidian (your clean reader)

**Set up once (Windows):**
1. Install **GitHub Desktop** (free) → sign in → clone **wine_vault**.
2. Install **Obsidian** (free) → **Open folder as vault** → pick the
   wine_vault folder.

**Every day:**
- Left panel = every card. Start at **index** (the table of contents).
- Colored/underlined words are **doors** — click to jump to that producer.
- 🔍 (left side) searches every card.
- Book/pencil icon (top-right) → leave on **read** for the cleanest look.

**To get my latest changes:** open GitHub Desktop → click **Pull origin**.
One click = newest cards. (Think "Pull = refresh.")

---

## 💬 ASK — Claude, reading the repo directly

- **Deep questions** (compare producers, gap analysis, drink-window lists):
  **Claude Code on the web** (claude.ai/code) — it reads the whole live vault
  and has the **`/ask-cellar`** command.
- **Quick questions / on your phone:** **claude.ai in a web browser** with the
  **GitHub connector**. Set up once: claude.ai → Settings → Connectors →
  GitHub → connect. Then in a chat: **＋ → Add from GitHub → wine_vault**.
  (The Claude phone *app* has no GitHub option yet — use the browser, and
  "Add to Home Screen" so it feels like an app.)

---

## ✏️ CHANGE — ask Claude Code

- New wine list, new producer, fix a page, run an analysis and save it →
  just ask **Claude Code** (claude.ai/code). It edits the files and saves
  them to GitHub for you.
- After it does, click **Pull origin** in GitHub Desktop to see the changes
  in Obsidian.

---

## ✅ The golden rules

1. **The GitHub repo is the only real copy.** Never keep the vault on Google
   Drive or as uploaded files somewhere — those go stale and cause drift.
2. **Edit through git** (ask Claude Code, or edit in Obsidian and let it save).
3. **"Pull" = refresh** your reader. Do it whenever you want the latest.

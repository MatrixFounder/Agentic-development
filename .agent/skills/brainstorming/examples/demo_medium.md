# Example: Medium Task (Standard Flow)

**User Request**: "Add a 'Dark Mode' toggle to the settings page."

---

**Agent Thinking** (Internal):
- **Complexity**: MEDIUM. Goal is clear, but implementation details are open (persistence, detection, styling approach).
- **Action**: Standard Cycle. Gather context → generate 2-3 options → compare → confirm.

---

## Phase 1: Assess & Understand

**Agent**:
"I'll help add Dark Mode. I see you're using Tailwind + React.

**How should we persist the user's preference?**
A) `localStorage` — preserves across sessions, no backend needed
B) System preference only (`prefers-color-scheme`) — zero storage, respects OS setting
C) Database — syncs across devices, needs API endpoint"

**User**:
"Let's go with localStorage."

---

## Phase 2: Diverge — Generate Options

**Agent**:
"Good choice. Now for the implementation approach, here are 3 options:

1. **React Context + Hook** — Create `useTheme()` hook, wrap app in `ThemeProvider`. Clean separation, easy to test.
2. **CSS-only with Tailwind `dark:` classes** — Toggle `dark` class on `<html>`, let Tailwind handle everything. Minimal JS, but harder to extend later.
3. **Zustand store** — If you already use Zustand, add theme as a slice. Consistent with existing state management.

I see you already use Zustand in `src/store/` for other features."

---

## Phase 3: Converge — Evaluate

**Agent**:
"Quick comparison:

| Criteria | Context+Hook | CSS-only | Zustand |
|---|---|---|---|
| Consistency with codebase | Medium | Low | **High** |
| Implementation effort | Medium | **Low** | Medium |
| Extensibility | High | Low | **High** |

**I recommend Option 3 (Zustand)** — it matches your existing patterns and scales if you add theme customization later. The main trade-off is slightly more code than CSS-only.

Proposed plan:
1. **State**: Add `theme` slice to existing Zustand store, read/write `localStorage`
2. **UI**: Toggle switch in `Settings.tsx`
3. **Styling**: Toggle `dark` class on `<html>` root, use Tailwind `dark:` variants
4. **Init**: On app load, check `localStorage` → fall back to `prefers-color-scheme`

Does this match your expectations?"

**User**:
"Yes, sounds good."

---

## Phase 4: Confirm

**Agent**:
"Confirmed. I'll create the Technical Spec in `docs/design/dark-mode.md` and then implement. Starting with the Zustand store slice."

---

**Why this works**:
- Generated 3 real alternatives (not one idea in different words)
- Used existing codebase context (Zustand already in use) to inform recommendation
- Comparison table makes trade-offs visible
- Clear recommendation with reasoning, not just a list of options
- 4-step plan is concrete and actionable

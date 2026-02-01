# Example: Medium Task (Standard Flow)

**User Request**: "Add a 'Dark Mode' toggle to the settings page."

**Agent Thinking** (Internal):
*   **Complexity**: MEDIUM. Goal is clear, but implementation details (Storage? System preference? Tailwind?) are open.
*   **Action**: Standard Cycle. Check stack, ask preference, propose design.

**Agent**:
"I'd be happy to add the Dark Mode toggle.
I see you are using Tailwind. **How would you like to persist the user's preference?**
A) `localStorage` (Preserves across sessions)
B) System Preference only (`prefers-color-scheme`)
C) Database (Server-side)"

**User**:
"Let's go with LocalStorage."

**Agent**:
"Understood. **Proposed Design**:
1.  **State**: React Context or Hook (`useTheme`) to read/write `localStorage`.
2.  **UI**: A simple toggle switch in `Settings.tsx`.
3.  **Class**: Toggle the `dark` class on the `<html>` root element.

Does this match your expectations?"

**User**:
"Yes, sounds good."

**Agent**:
"Perfect. I'll create the `Feature Plan` in `docs/design/dark-mode.md` and then implement."

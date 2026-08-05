# Chapter 7: Keyboard Shortcut Registry

Herdr uses **Prefix Mode** (default prefix `ctrl+b`) for most bindings, plus a separate **Copy Mode** for scrollback/selection. Ctrl+alt-based prefix-free shortcuts are *not* on by default — they're an optional binding example from the keyboard docs, not the out-of-box behavior.

## Essential Default Bindings

| Category | Action | Shortcut |
| :--- | :--- | :--- |
| **System** | Help / Settings | `Prefix + ?` / `Prefix + s` |
| | Detach Session | `Prefix + q` |
| **Workspaces**| New / Rename | `Prefix + Shift + n/w` |
| **Tabs** | Create New Tab | `Prefix + c` |
| | Next / Prev Tab | `Prefix + n` / `Prefix + p` |
| **Panes** | Split Right / Down | `Prefix + v` / `Prefix + minus` |
| | Move Focus | `Prefix + h/j/k/l` |
| | Zoom | `Prefix + z` |
| | Enter Copy Mode (scroll/select) | `Prefix + [` |

Herdr also supports mouse-driven interaction out of the box: clicking to focus a pane, drag-resizing splits, right-click context menus, click-drag text selection with copy, and Ctrl-click to open links — often the faster path for a new user than memorizing the prefix table above. See `herdr.dev/docs/keyboard/` for the full, version-current binding list and how to customize it via `herdr config`.

---

Previous: [Chapter 6 — Operational Constraints & Known Issues](chapter06-operational-constraints.md) · Next: [Appendix — Verification Notes](appendix-verification-notes.md)

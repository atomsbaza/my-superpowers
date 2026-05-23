# Kiro Model Identifiers

Agent files in `kiro/agents/` use these model identifiers:

| Value used | Status |
|---|---|
| `claude-sonnet-4-6` | Confirmed — [GitHub issue kirodotdev/Kiro#6637](https://github.com/kirodotdev/Kiro/issues/6637) |
| `claude-opus-4-7` | Inferred from same hyphen pattern; CLI docs show `claude-opus-4.7` (dot) — both may work |
| `claude-haiku-4-5` | Confirmed by same source (not currently used here) |

**To verify available models in your Kiro version:** run `/model` in an active Kiro chat session. The canonical list comes from Kiro's model service and may change with updates.

If a model fails to load, try replacing hyphens with dots in the version part: `claude-opus-4-7` → `claude-opus-4.7`.

# Chapter 5: Advanced Configuration & UI Control

## Configuration Resolution

- **Unix:** `~/.config/herdr/config.toml`
- **Windows:** `%APPDATA%\herdr\config.toml`

## Validation and Environment

`herdr config check` validates `config.toml` and prints diagnostics. Run it after editing the config, since some settings are only applied on the next `herdr server reload-config` and others require a full server restart.

- **`HERDR_PROCESS_DETECTION`**: Set to `child-groups` for restricted environments. This variable is read by the server and requires a server restart to take effect.
- **`HERDR_AGENT`**: Overrides process detection; useful for VM/sandbox wrappers (e.g., `HERDR_AGENT=claude`).

## UI Customization

Run `herdr --default-config` to print the full annotated default config, including the `[theme]` section (e.g. `theme.auto_switch` for following system light/dark appearance) and other UI options. Use that output as the source of truth for available keys rather than a hardcoded list — it reflects your installed version exactly.

---

Previous: [Chapter 4 — Agent Integrations & Support Matrix](chapter04-agent-integrations.md) · Next: [Chapter 6 — Operational Constraints & Known Issues](chapter06-operational-constraints.md)

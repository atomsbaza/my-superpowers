# Research: XcodeBuildMCP

## Summary

XcodeBuildMCP is an open-source Model Context Protocol (MCP) server and CLI that bridges AI coding agents with Xcode's build toolchain, enabling autonomous iOS and macOS development workflows. Originally authored by Cameron Cooke, it was transferred to Sentry in 2025 and is now maintained at `github.com/getsentry/XcodeBuildMCP`. It exposes up to 82 tools across build, test, debug, simulator, and UI automation categories, and integrates natively with Claude Code as a first-class client. The project fills a significant gap: before it existed, AI agents had to parse thousands of lines of unstructured `xcodebuild` output and could not close the feedback loop by verifying their own builds on device or simulator.

---

## Key Findings

### What It Is

- XcodeBuildMCP is a **dual-mode tool**: an MCP server (for AI agents) and a standalone CLI (for scripting and CI/CD), both backed by the same underlying tool set.
- It wraps `xcodebuild` and related Apple developer tools and returns **structured JSON output** — categorized errors with file paths and line numbers — rather than raw compiler logs, which is what makes it tractable for AI agents.
- Ownership transferred from Cameron Cooke to **Sentry** in 2025; the canonical repository is now `github.com/getsentry/XcodeBuildMCP`.
- It is MIT-licensed and supports Xcode 16.x and later, with support for macOS 14.5+, Node.js 18+, and Xcode 26 (beta) bridge integration.
- Version 2.0 introduced a "first-class CLI" that makes all MCP tools available directly from the terminal.

---

### Installation and Configuration

**System requirements:** macOS 14.5+, Xcode 16.x+, Node.js 18+ (only if using npm; not required for Homebrew).

**Two installation paths:**

Via Homebrew (no Node.js dependency):
```bash
brew tap getsentry/xcodebuildmcp
brew install xcodebuildmcp
```

Via npm (globally or on demand):
```bash
npm install -g xcodebuildmcp@latest
# or run ad-hoc without install:
npx -y xcodebuildmcp@latest mcp
```

**Adding to Claude Code:**

```bash
claude mcp add XcodeBuildMCP -s user -e XCODEBUILDMCP_SENTRY_DISABLED=true -- npx -y xcodebuildmcp@latest mcp
```

Verify with:
```bash
claude mcp list
claude mcp get XcodeBuildMCP
```

**Per-project configuration:**

Run the setup wizard from your project root:
```bash
xcodebuildmcp setup
```

This creates or updates `.xcodebuildmcp/config.yaml` with settings covering target platforms, enabled workflows, workspace/scheme defaults, and simulator preferences. An optional `xcodebuildmcp init` step installs client-specific "agent skills" that prime the AI model with usage instructions.

**Workflow enabling:** Only the `simulator` workflow is enabled by default. Others (device, debugging, UI automation, macOS, Xcode IDE bridge) must be explicitly enabled either in the config YAML or via the `XCODEBUILDMCP_ENABLED_WORKFLOWS` environment variable.

---

### Tools and Capabilities

XcodeBuildMCP exposes **82 tools** (v2.3.2) organized into 16 workflow groups.

| Workflow Group | Representative Tools |
|---|---|
| Simulator Build | `simulator/build`, `simulator/build-and-run`, `simulator/test` |
| Simulator Lifecycle | boot, open, list, stop, erase, set location/network/statusbar/appearance |
| Device Build | build and deploy to physical devices over USB or Wi-Fi |
| LLDB Debugging | attach debugger, set breakpoints, inspect variables and call stacks |
| UI Automation | tap, swipe, type, snapshot UI, capture screenshots, video capture |
| Project Inspection | discover schemes, build settings, bundle IDs |
| Session Defaults | set/get/persist workspace, scheme, simulator across tool calls |
| Xcode IDE Bridge | `xcode_ide_list_tools`, `xcode_ide_call_tool` (Xcode 26+ only) |

Key design details:
- A **per-workspace daemon** handles stateful operations and launches automatically on demand.
- **Session defaults** persist workspace/scheme/simulator choices across tool calls, reducing token overhead.
- **Macro validation skipping** is automatically enabled during builds to avoid common blockers.
- UI automation and simulator video capture rely on a **bundled helper binary** (`axePath`).

---

### Integration with Claude Code

- Claude Code is listed as a **first-class client** with full support for tools, resources, tool-list-changed notifications, and environment variable configuration.
- The server runs over **stdio**, which is the standard Claude Code MCP transport.
- Getsentry ships an **agent skill** (`xcodebuildmcp init`) that installs a `SKILL.md` into the Claude Code project context.
- Real-world use: an agent detected a missing Metal Toolchain from structured output and downloaded it autonomously, auto-adapted when a requested simulator wasn't available, and ran a five-step health check (build, install, launch, test, log capture) in ~90 seconds.
- The telemetry flag `XCODEBUILDMCP_SENTRY_DISABLED=true` is commonly set during Claude Code installation to opt out of Sentry error reporting.

---

### Known Limitations and Issues

**Functional gaps:**
- **Visual debugging is not supported.** The agent cannot interpret layout bugs, rendering artifacts, or visual correctness.
- **Code signing is opaque.** Provisioning profile and certificate errors are not structured diagnostically. Workaround: open in Xcode, enable automatic signing, pick a development team first.
- **Incremental builds are not leveraged.** Rebuilds entire projects rather than using Xcode's incremental compilation cache across sessions.
- **Xcode IDE Bridge requires Xcode 26+** (currently in beta).

**Configuration friction:**
- Only the simulator workflow is enabled by default; device, debugging, and UI automation must be explicitly enabled.
- Missing `bundleId` in session defaults causes `launch_app_logs_sim()` to fail.
- UI automation helper binary must be reinstalled if the package is reinstalled.

**Reliability issues (community-reported):**
- Timeout errors in some clients; mitigated by `XCODEBUILDMCP_STARTUP_TIMEOUT_MS`.
- Stale daemon sockets require manual intervention via `xcodebuildmcp daemon list`.
- Some users report the server "forever waiting" under certain agent loop conditions.
- Running inside Xcode's agent requires wrapping the startup command with `zsh -lc` and setting PATH explicitly.

**vs. Apple's native Xcode MCP:** Apple's Xcode MCP compiles faster (2.1s vs 42–79s initial) but stops at build — no simulator install, launch, screenshot, or log capture. XcodeBuildMCP is slower but closes the full feedback loop.

---

## Trade-offs / Caveats

- **Tool count discrepancy:** Different sources cite 59, 81, or 82 tools depending on which workflows are enabled and version installed.
- **Telemetry:** Now owned by Sentry, it includes Sentry error telemetry by default. Opt-out: `XCODEBUILDMCP_SENTRY_DISABLED=true`.
- **Sentry ownership:** The original Cameron Cooke repository still exists; `getsentry/XcodeBuildMCP` is the active one.
- **Build speed:** First-run builds are slow (40–80 seconds for the full install-and-run cycle) due to `xcodebuild` cold starts and simulator boot time.

---

## Sources

- [XcodeBuildMCP Official Site](https://www.xcodebuildmcp.com/)
- [GitHub - getsentry/XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP)
- [Setup · XcodeBuildMCP Docs](https://www.xcodebuildmcp.com/docs/setup)
- [MCP Server Mode · XcodeBuildMCP Docs](https://www.xcodebuildmcp.com/docs/mcp-mode)
- [XcodeBuildMCP Troubleshooting](https://www.xcodebuildmcp.com/docs/troubleshooting)
- [Two MCP Servers Made Claude Code an iOS Build System](https://blakecrosley.com/blog/xcode-mcp-claude-code)
- [Apple Xcode MCP vs XcodeBuild MCP - @samwize](https://samwize.com/2026/03/11/i-tried-apple-xcode-mcp-and-xcodebuild-mcp-only-one-feels-complete/)
- [iOS Project Claude Code Setup Prompt - GitHub Gist](https://gist.github.com/joelklabo/6df9fa603bec3478dec7efc17ea44596)
- [Issues · getsentry/XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP/issues)

# Research: Tools for iOS Simulator Screen Visibility + UI Interaction from Claude Code CLI

**Date:** 2026-05-24

## Summary

As of mid-2026, the dominant approach for letting Claude Code "see" an iOS Simulator and drive its UI is an MCP server that wraps either Facebook's `idb` or a newer Swift CLI called **AXe**, exposing tools like `screenshot`, `describe_ui`, `tap`, `swipe`, and `type_text`. Three actively maintained options exist: **`ios-simulator-mcp`** (idb-based, focused), **`XcodeBuildMCP`** (AXe-based, broadest Xcode coverage), and **`mobile-mcp`** (cross-platform iOS/Android via Appium/WebDriverAgent). Apple's own `xcrun simctl` can only capture screenshots and video — it has no native tap or swipe command — so every solution layers a private-framework or out-of-process helper on top. Anthropic's computer-use capability can technically drive the Simulator by clicking macOS window pixels, but it is a last resort because it has no accessibility-tree awareness.

---

## Key Findings

### 1. Native Baseline: `xcrun simctl`

- `xcrun simctl io <device> screenshot output.png` captures a PNG of the booted simulator; `recordVideo` captures MP4.
- **`simctl` has no tap, swipe, or type primitive** — UI interaction must come from another layer.
- Claude Code can invoke simctl directly via Bash: `xcrun simctl io booted screenshot /tmp/screen.png`

### 2. XcodeBuildMCP (cameroncooke) — AXe-Backed — INSTALLED ✅

- The broadest Xcode-focused MCP: handles build, run, test, device management, and simulator UI automation.
- UI interaction tools: `screenshot`, `describe_ui`, `tap`, `long_press`, `swipe`, `type_text`, `key_press`, `button`, `gesture`
- Backed by **AXe** — a standalone Swift CLI using Apple's accessibility APIs to synthesize HID events and enumerate the element tree.
- Recommended when you need a single MCP covering the full Xcode loop (build → boot simulator → install → screenshot → tap → assert).
- GitHub: https://github.com/cameroncooke/XcodeBuildMCP
- AXe CLI: https://github.com/cameroncooke/AXe

### 3. `ios-simulator-mcp` (joshuayoes) — idb-Backed

- Requires: `brew install facebook/fb/idb-companion`
- Tools: `screenshot`, `ui_describe_all`, `ui_tap`, `ui_swipe`, `ui_type`, `record_video`
- Caveat: Facebook `idb` was archived in 2024 — community-maintained.
- GitHub: https://github.com/joshuayoes/ios-simulator-mcp

### 4. `mobile-mcp` (mobile-next) — Cross-Platform iOS + Android

- Backed by Appium / WebDriverAgent — heavier setup.
- Best when the same workflow must target both iOS and Android.
- GitHub: https://github.com/mobile-next/mobile-mcp

### 5. Computer-Use (Last Resort)

- Can screenshot any macOS window (including Simulator) and click at pixel coordinates.
- No accessibility-tree awareness — coordinates are brittle.
- Peekaboo MCP: https://github.com/steipete/peekaboo

---

## Trade-offs

| Option | Pros | Cons |
|---|---|---|
| XcodeBuildMCP | Full Xcode loop, AXe-backed, actively maintained | Heavier install (npx) |
| ios-simulator-mcp | Lightweight, simple | idb archived 2024 |
| mobile-mcp | iOS + Android parity | WDA setup overhead |
| xcrun simctl | Zero setup, first-party | Screenshot/video only, no interaction |
| Computer-use | Works on anything | Pixel-level only, brittle |

## Recommendation Matrix

| Need | Best Tool |
|---|---|
| Build + run + screenshot + tap in one MCP | XcodeBuildMCP + AXe |
| Lightweight, focused simulator interaction | `ios-simulator-mcp` + `idb_companion` |
| iOS and Android from same workflow | `mobile-mcp` |
| Run full XCUITest suites, feed results to Claude | `xcodebuild test` via XcodeBuildMCP + `xcresulttool` |
| Screenshot only, no interaction | `xcrun simctl io booted screenshot` |

---

## Sources

- https://github.com/cameroncooke/XcodeBuildMCP
- https://github.com/cameroncooke/AXe
- https://github.com/joshuayoes/ios-simulator-mcp
- https://github.com/mobile-next/mobile-mcp
- https://github.com/facebook/idb
- https://github.com/appium/appium
- https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device
- https://github.com/steipete/peekaboo

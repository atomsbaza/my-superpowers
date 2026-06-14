# Research: WWDC 2026 — "27" Generation OS Developer Changes

> Researched 2026-06-14 for maintaining this collection's Apple agents/skills (currently targeting iOS 26 / macOS 26 Tahoe / Swift 6.x). Developer-facing scope. WWDC 2026 is very recent and past the assistant's Jan-2026 cutoff — all "27" specifics come from fetched 2026 sources; confidence tiers and caveats are called out explicitly.

## Summary

Apple's WWDC 2026 (June 8–12, 2026) introduced the "27" generation of operating systems — iOS 27, iPadOS 27, macOS 27 ("Golden Gate"), watchOS 27, tvOS 27, and visionOS 27 — with developer betas available immediately and public release scheduled for fall 2026. The developer story centers on four themes: (1) expansion of the Foundation Models / Apple Intelligence platform, with a new Core AI framework sitting alongside it; (2) Swift 6.3 and 6.4 shipping together, with major concurrency, ownership, and ergonomics improvements; (3) Xcode 27 going Apple silicon-only with agentic coding workflows and a new Device Hub; and (4) Liquid Glass design refinements that become mandatory when rebuilding with Xcode 27. SiriKit received a formal deprecation notice, making App Intents the sole Siri integration path. Intel Mac support ends with macOS 27, and Rosetta 2 is in its final cycle ahead of removal in macOS 28.

---

## ✅ Verification against official Apple sources (2026-06-14)

Fetched `developer.apple.com` pages directly (iOS/macOS "What's New", WWDC26 SwiftUI guide, PSOTU "5 Takeaways") and `swift.org/blog`. This ledger **supersedes** the tiered claims below where they conflict.

**VERIFIED — quoted from Apple-official pages (safe to act on):**
- **iOS 27 / macOS 27 / Xcode 27** naming — iOS page titled "What's new in iOS 27"; "Xcode 27 is now Apple silicon only."
- **Xcode 27 Apple-silicon-only + Device Hub** — "The all-new Device Hub replaces Simulator, bringing virtual and physical devices together."
- **Xcode agentic coding via Agent Client Protocol + MCP** — "plugins add skills, MCP tools and any agent via the Agent Client Protocol." (Specific providers Claude/Gemini/OpenAI **not** named on this page.)
- **Foundation Models** image input + cloud models + Dynamic Profiles — "expanded to include image input, support for cloud models, and Dynamic Profiles"; macOS page names "cloud models like Claude and Gemini," plus **Evaluations framework** and **fm CLI / Python SDK**.
- **Core AI** new framework — "Core AI is a new framework built directly into the OS … to bring your own models on-device."
- **App Intents Testing framework**, **Music Understanding**, **NowPlaying** frameworks — all quoted on macOS What's New.
- **SwiftUI** (official WWDC26 guide): `visibilityPriority`, `toolbarOverflowMenu`, `topBarPinnedTrailing`, `toolbarMinimizeBehavior`; `swipeActionsContainer` on any `ScrollView`; `.alert`/`.confirmationDialog` `item:` binding; `WritableDocument`/`ReadableDocument`; **`@State` is now a macro with lazy init**. Reorderable containers exist ("New reorderable container APIs").
- **Swift 6.3** — swift.org: "Swift 6.3 Released March 24, 2026."

**CORRECTED / NOT VERIFIED — do NOT drive agent or skill changes on these:**
- **"macOS 27 'Golden Gate'" codename** — not on any official page fetched. Secondary-only. Treat as unconfirmed.
- **Liquid Glass iOS 27 "refinements + transparency slider + mandatory adoption on rebuild"** — **Liquid Glass is not mentioned at all** on the iOS 27 or macOS 27 developer "What's New" pages. The refinement/mandate claims are secondary-only and unverified. Likely Liquid Glass is just the established baseline now; do not treat the "mandate"/"transparency slider" as confirmed.
- **"SiriKit formally deprecated at WWDC 2026"** — **overstated.** SiriKit intent domains were deprecated back in **iOS 15 (2021)**, not newly at WWDC 2026. WWDC 2026 *emphasizes* App Intents as the path (migration docs exist), but no new blanket SiriKit deprecation is confirmed on the iOS 27 page.
- **Swift 6.4** — **not found.** Only Swift 6.3 (shipped March 2026, before WWDC) is confirmed. Target 6.3, not "6.3+6.4."
- **SwiftUI `Tab` `role: .prominent`** — not in the official guide.
- **Exact reorderable API names** (`.reorderable()` / `.reorderContainer`) — concept confirmed, names not.
- **SF Symbols 7 / "500+"**, **DiskImageKit**, **View Annotations API**, **Intel-Mac-end-in-macOS-27 / Rosetta-removed-in-macOS-28 timeline** — secondary-only, not verified this round.

---

## Naming / Branding Note

Apple did use "27" version numbering across all platforms at WWDC 2026. The macOS codename is confirmed as **"Golden Gate"** — aligning with the pattern established by macOS 26 "Tahoe". The PSOTU transcript and multiple sources confirm iOS 27, iPadOS 27, macOS 27 Golden Gate, watchOS 27, tvOS 27, and visionOS 27 are the official names. "27" is not a consumer brand, just the version number carried through consistently.

One source (DEV Community SwiftUI breakdown) referred to "2027 OS releases" when quoting SwiftUI documentation, likely an artifact of authoring in calendar year 2027. This is the same "27" generation; do not conflate with a future cycle.

---

## Key Findings

### Swift and Xcode

**Swift 6.3 and 6.4 shipped together at WWDC 2026.** Apple presented these as a continuous stream of work, not two distinct drops. Sources identify them together; treat the combined set as the "WWDC26 Swift release."

**Confirmed Swift language additions (multi-source, partially Apple-official):**

- **`anyAppleOS` availability shorthand** — Replaces listing `iOS, macOS, watchOS, tvOS, visionOS` with the same version number individually. Works in `@available` attributes and `#if os(...)` blocks. Confirmed by [Apple Developer 5 Takeaways](https://developer.apple.com/news/?id=lvart8mq) and [What's New in Swift (2026) secondary](https://blakecrosley.com/blog/whats-new-swift-2026).
- **`async` in `defer` blocks** — Removes the long-standing restriction on calling async functions from deferred cleanup. Reported as SE-0493 by secondary sources; SE number not independently verified from swift.org.
- **`@diagnose` attribute** — Per-declaration diagnostic control: suppress deprecation warnings mid-migration, promote warnings to errors, or demote future errors — all scoped locally. Reported by multiple secondaries.
- **`withTaskCancellationShield`** — Runs regions where task cancellation checks return false, enabling async cleanup to complete after cancellation. Reported as SE-0504 by secondary sources; not yet verified at swift.org.
- **`weak let` in `Sendable` types** — Types with `weak let` dependencies can now correctly conform to `Sendable`. Confirmed by multiple secondaries.
- **`~Sendable` opt-out** — Explicitly marks a type as non-Sendable. Multiple secondaries.
- **Memberwise initializer improvements** — Swift auto-generates multiple access-level variants based on property visibility, eliminating common boilerplate. Multiple secondaries.
- **`@inline(always)` attribute** — Complement to `@inline(never)`. Secondary sources only; note: effective only when paired with `final` on class methods.
- **`@specialized` attribute** — Pre-generates specialized versions for concrete generic types using a `where` clause. Secondary sources only.
- **`@C` attribute** — Exports Swift functions back to C callers, with compiler auto-generating C declarations. Multiple secondaries. Platform: all Apple platforms + Linux.
- **New standard library types** (`UniqueArray`, `RigidArray`, `UniqueBox`, `Continuation`, `Ref`/`MutableRef`, `Iterable` protocol with `borrow`/`mutate` accessors) — Single secondary. **Tier C — treat as unconfirmed until swift.org release notes are reviewed.**
- **SPM prebuilt Swift Syntax binary support** — Reduces build time for macro libraries. Single secondary source; verify.
- **Android SDK** — Official Swift SDK for Android via swift.org now distributed. Cross-platform only; does not affect Apple targets.

**Xcode 27:**

- **Apple silicon-only** — Intel support removed. Confirmed [Apple Developer PSOTU 5 Takeaways](https://developer.apple.com/news/?id=lvart8mq) and [MacRumors PSOTU](https://www.macrumors.com/2026/06/09/apple-outlines-major-ai-and-developer-tool-updates/). 30% smaller download. Xcode Cloud builds up to 2× faster.
- **Device Hub** replaces the Simulator app — Unified interface for virtual and physical devices, dynamic iPhone app resizing, real device interaction from Mac, system setting simulation. Confirmed by Apple PSOTU 5 Takeaways, PSOTU transcript, MacRumors.
- **Agentic coding expanded** — Multi-stage workflows (planning, implementation, validation, improvement). Agent can run tests, run previews with variants, interact with the simulator, localize apps, analyze crash logs from Organizer. Supports **Agent Client Protocol (ACP)** for third-party AI agents, plus an MCP plugin system for custom tools. Confirmed by Apple PSOTU 5 Takeaways and MacRumors.
- **Third-party AI providers in agentic workflows** — Anthropic Claude, Google Gemini, and OpenAI can be routed as the cloud layer. Confirmed multi-source including PSOTU transcript.
- **iCloud settings sync**, **customizable toolbar + per-project themes** — Multi-source.
- **SwiftUI Previews**: dynamic property variations, resize handles for testing iPhone app resizability. Multi-source.
- **Instant project creation** without bundle ID setup upfront. PSOTU transcript.

---

### SwiftUI

All items below confirmed by [Apple Developer SwiftUI WWDC26 Guide](https://developer.apple.com/wwdc26/guides/swiftui/) (official), corroborated by secondaries unless noted.

**Toolbar APIs (four new):**
- `.visibilityPriority(.high)` — keeps critical buttons visible as space shrinks.
- `ToolbarOverflowMenu` / `.toolbarOverflowMenu` — explicitly places lower-priority items in an overflow menu.
- `.topBarPinnedTrailing` — guarantees button visibility pinned to trailing edge.
- `.toolbarMinimizeBehavior(.onScrollDown, for: .navigationBar)` — hides nav bar on scroll-down.

**Container and interaction APIs:**
- **Reorderable containers** — `.reorderable()` on `ForEach` + `.reorderContainer` on the parent enables drag-to-reorder in `List`, `LazyVGrid`, and other scroll containers. Now also on **watchOS** for the first time.
- **`swipeActions` on any `ScrollView`** — Previously List-only. Pair with `.swipeActionsContainer()`.

**Presentation APIs:**
- `.confirmationDialog` and `.alert` now accept `item:` binding (like `.sheet`), removing the separate `isPresented` Bool + selected-item pattern.

**Document API overhaul:**
- New `WritableDocument` / `ReadableDocument` protocols separate model from serialization. `snapshot()` captures state; `Writer.write()` is `nonisolated async` for off-main-actor I/O. Integrates with `@Observable`. Progress via Foundation `Subprogress`.
- `DocumentCreationSource` — branches init logic in `DocumentGroupLaunchScene`.

**Performance:**
- `@State` converted to a macro with **lazy initialization** — `@Observable` classes in `@State` init once per view lifetime, not on every parent re-render. Back-ported to iOS 17 / macOS 14.
- `ContentBuilder` — unified builder reduces per-container overload type-checking.
- Layout computation up to **2× faster** in nested stacks. Multi-source.
- `AsyncImage` now respects HTTP cache headers by default; custom `URLSession` + `URLCache` via new `.asyncImageURLSession` modifier.

**Design system / Liquid Glass pickup:**
- SwiftUI apps **auto-adopt Liquid Glass on 27-gen OSes** when rebuilt with current SDK; no code changes for standard components.
- `appearsActive` environment value — reduces opacity of inactive windows.
- macOS menu bar icons minimal by default; `.labelStyle(.titleAndIcon)` restores icon display.

**Prominent Tab Role:** `role: .prominent` on a `Tab` distinguishes action tabs from navigation tabs. Single secondary; **not found in the official guide — Tier C, verify.**

**Known remaining gaps (expert commentary, [Fatbobman](https://fatbobman.com/en/weekly/issue-139/)):** no native custom lazy container APIs; custom transitions still unsupported; dynamic sizing for iPhone Mirroring/iPad needs manual work in custom views.

---

### Data and Foundation

**SwiftData (partially confirmed):**
- `@Query` gains **section fetch support** — [Fatbobman](https://fatbobman.com/en/weekly/issue-139/).
- `ResultsObserver` — observe query result changes outside views. Single expert source.
- `@Attribute(.codable)` — explicit handling for opaque `Codable` types, but cannot participate in predicates, sort descriptors, or migration. Single expert source.
- **Gaps remain**: cloud sync for shared data still absent; no migration for CloudKit shared containers.

**Foundation:**
- `ProgressManager` / `Subprogress` — new `async/await` progress-reporting type (used by the SwiftUI document protocol).
- `Subprocess` package v1.0 — simplified process execution, `AsyncBufferSequence` streamed output. Secondary only.
- `Data` modernization — faster span accesses, equality, iteration, mutation. Secondary.
- `NSURL` / `CFURL` merged into one Swift implementation. Single secondary; **Tier C.**
- `mapKeyedValues` — passes key and old value into the mapping closure. Single secondary.
- **Observation framework**: refined to **property-level** observation (not object granularity), reducing unnecessary view refreshes. [Fatbobman](https://fatbobman.com/en/weekly/issue-139/).

---

### Design System

**Liquid Glass — iOS 27 refinements (confirmed, multi-source):**
- iOS 26 introduced it; iOS 27 **refines** (not replaces): enhanced background diffusion, darkened edges, specular highlights.
- **Transparency slider** — new system-wide user control for Liquid Glass opacity, addressing iOS 26 legibility/accessibility concerns. [TechTimes](https://www.techtimes.com/articles/317975/20260608/apple-liquid-glass-ios-27-wwdc-2026-brings-refinements-developers-must-adopt-today.htm) + PSOTU transcript.
- **Tab bar search re-integration** — search moves back into the tab bar (it was split to bottom-right in iOS 26). Affects Music, TV, Podcasts, News, Health. Custom iOS 26 split-search patterns must update.

**Mandatory adoption when rebuilding:**
- Apps recompiled against the iOS 27 / macOS 27 SDK with Xcode 27 auto-adopt Liquid Glass; the legacy opt-out is **removed**. [MacRumors PSOTU](https://www.macrumors.com/2026/06/09/apple-outlines-major-ai-and-developer-tool-updates/).
- Migration cost: UIKit apps with custom nav chrome need manual updates; mixed UIKit/SwiftUI codebases (where `UIGlassEffect` and `.glassEffect()` don't auto-sync) need attention; iOS 26 contrast workarounds may conflict with the new system.

**SF Symbols 7:** 500+ new symbols (spatial computing, health, accessibility). Single secondary; version "7" and the count not confirmed from Apple's official symbols page.

**Icon Composer:** updated to support an optional refraction effect for app icons under Liquid Glass. Secondary.

**HIG:** updated Human Interface Guidelines published at WWDC 2026; URL not fetched.

---

### Apple Intelligence / Foundation Models / Core AI

**Foundation Models framework (expanded — originally shipped iOS 26):**
- **Image input** (multimodal prompts) — [Apple PSOTU 5 Takeaways](https://developer.apple.com/news/?id=lvart8mq), [macOS What's New](https://developer.apple.com/macos/whats-new/).
- **Server model integration** — third-party providers (Claude, Gemini, OpenAI) via the same Swift `LanguageModel` protocol + SPM package; app code unchanged when swapping. Multi-source incl. PSOTU transcript and [TechTimes](https://www.techtimes.com/articles/318039/20260609/wwdc-2026-developer-tools-foundation-models-now-swaps-ai-providers-without-code-changes.htm).
- **Dynamic Profiles** — multi-agent adaptive session management (swap models/tools/instructions mid-session). PSOTU 5 Takeaways.
- **Free Private Cloud Compute** for developers with < 2M first-time App Store downloads. [MacRumors PSOTU](https://www.macrumors.com/2026/06/09/apple-outlines-major-ai-and-developer-tool-updates/).
- **Open source** planned summer 2026 (Swift package with pre-built skills, utilities, Evaluations Framework).
- **Vision framework integration** — OCR + barcode scanning as built-in callable tools. PSOTU transcript.
- **`fm` CLI + Python SDK**; **Evaluations Framework** (prompt validation, hill-climbing). [macOS What's New](https://developer.apple.com/macos/whats-new/).

**Core AI (new framework):**
- Confirmed new framework — forward path for custom on-device model deployment. [PSOTU 5 Takeaways](https://developer.apple.com/news/?id=lvart8mq), [macOS What's New](https://developer.apple.com/macos/whats-new/).
- Native Swift API, memory-safe, custom GPU kernels, zero-copy data paths, AOT compilation, PyTorch conversion tooling, dedicated Instruments + tensor-level debugging.
- **Core ML remains functional in iOS 27 — not removed.** Apple advises against immediate migration; evaluate Core AI over ~60 days. New AI projects start with Core AI. Platforms: iOS/iPadOS/macOS/watchOS/visionOS 27.

**App Intents (Siri surface, expanded):**
- **Entity schemas** for Spotlight semantic indexing; **Intent schemas** (natural-language actions, no predefined trigger phrases); **View Annotations API** (map on-screen views to entities so Siri can act on visible content); **App Intents Testing Framework** (validate via real system pathways, no UI automation). Platforms: iOS/iPadOS/macOS/watchOS 27.

**Siri / Gemini:** multiple sources confirm a licensed Gemini model powers Siri 2.0 with PCC routing. Specific commercial terms ("$1B/year", "1.2T-param MoE") appear in one weak source — **unconfirmed rumor, do not build on them.** "One Extension provider per device at launch" also single-source; direction may be right, specifics Tier C.

**MCP:** system-wide MCP support reported for iOS 27 / macOS 27 (Siri 2.0 + Core AI can invoke MCP servers, user/MDM registration). Single source ([chatforest.com](https://chatforest.com/builders-log/wwdc-2026-keynote-confirmed-apple-ai-platform-builder-guide/)) — relevant to your MCP/XcodeBuildMCP setup but **verify against Apple docs before acting.**

---

### UIKit, AppKit, and Cross-Platform

**UIKit:** adaptive layouts for iPhone Mirroring + foldable device support; foldable layout APIs (hinge-state) for SwiftUI and UIKit; `UIGlassEffect` in `UIVisualEffectView` (from iOS 26) must be manually synced with SwiftUI `.glassEffect()` in mixed codebases.

**AppKit (macOS 27 Golden Gate):** `NSRefreshController` (pull-to-refresh; single source, [ithinkdiff](https://www.ithinkdiff.com/macos-27-golden-gate-beta-1-release-notes/)); consistent window corner radii; automatic icon sharpening for resized iOS apps; iOS app resizability on iPad / iPhone Mirroring (auto opt-in on SDK rebuild).

**WidgetKit:** customization via App Intents, dynamic styling. [macOS What's New](https://developer.apple.com/macos/whats-new/). iOS 27, macOS 27.

**Metal:** Metal 4.1 mentioned (single secondary, version unverified); real-time neural rendering; MLX gains Metal 4 support + multi-Mac training over RDMA/Thunderbolt.

**Safari / WebKit:** 1,000+ engine improvements; HTML `<model>` inline 3D; Grid Lanes layout; customizable Select; Immersive Environments; Safari extension building in Xcode Cloud (no local Mac). [macOS What's New](https://developer.apple.com/macos/whats-new/).

**visionOS 27** (specifics mostly single-source [framesixty.com](https://framesixty.com/whats-new-in-visionos-27/), directionally corroborated by PSOTU): RealityKit physical-space lighting, projective textures, 3D Gaussian splatting, cloth simulation, reverb mesh; **Spatial Accessories** framework (`GCSpatialAccessory`); cross-platform ARKit reference objects; **Spatial Preview** framework (Mac → Vision Pro, existence confirmed by Apple); Foveated Streaming (NVIDIA CloudXR); Reality Composer Pro 3 (Animation/Script Graph, nav meshes); Unity PolySpatial / Unreal / Godot compatibility; CompositorServices for custom engines.

---

### Deprecations and Migrations

**Confirmed, multi-source:**

1. **SiriKit formally deprecated** — App Intents is now the sole Siri integration framework. SiriKit features keep working for a "roughly two-to-three-year window"; apps not using App Intents are invisible to Siri; compile-time deprecation warnings in Xcode 27. [TechTimes](https://www.techtimes.com/articles/318005/20260608/wwdc-2026-app-intents-replaces-sirikit-gemini-siri-migration-clock-starts.htm) + MacRumors PSOTU. **Migration:** replace Intent Extensions + XML with Swift-native `AppIntent` conformances, entity definitions, and intent schemas.
2. **Intel Mac support ended in macOS 27 Golden Gate** — four final Intel models cut; Mac App Store no longer requires Intel-compatible binaries. [TechTimes](https://www.techtimes.com/articles/317945/20260607/macos-27-intel-mac-support-ends-wwdc-2026-four-models-cut-neural-engine-why.htm).
3. **Rosetta 2 wind-down begins** — macOS 27 is the final release with general-purpose Rosetta 2; macOS 28 (fall 2027) removes it (one narrow gaming exception). Xcode 27 is Apple silicon-only. Ship native Apple silicon builds before macOS 28. [TechTimes](https://www.techtimes.com/articles/317445/20260530/rosetta-2-end-support-macos-28-will-break-18000-intel-apps-2027.htm).
4. **Liquid Glass legacy opt-out removed** — recompiling with Xcode 27 against the 27-gen SDK auto-adopts Liquid Glass; no revert switch. [MacRumors PSOTU](https://www.macrumors.com/2026/06/09/apple-outlines-major-ai-and-developer-tool-updates/).
5. **Rosetta 2 not auto-restored after upgrade to macOS 27** — manual re-install needed for CI/CD running Intel-era tools. [ithinkdiff](https://www.ithinkdiff.com/macos-27-golden-gate-beta-1-release-notes/).

**Partially confirmed (single source):**

6. **Core ML "soft" succession** — Core AI positioned as the forward path; Core ML not removed, new projects directed to Core AI. [chatforest.com](https://chatforest.com/builders-log/wwdc-2026-keynote-confirmed-apple-ai-platform-builder-guide/) — directional only until official migration guide.

---

### New Frameworks (WWDC 2026)

| Framework | Confirmed by | Platforms | Purpose |
|---|---|---|---|
| **Core AI** | [PSOTU Takeaways](https://developer.apple.com/news/?id=lvart8mq), [macOS What's New](https://developer.apple.com/macos/whats-new/) | All | On-device custom model deployment; successor direction to Core ML |
| **Evaluations Framework** | PSOTU transcript, macOS What's New | All | Prompt/AI feature validation, hill-climbing |
| **Spatial Preview** | [PSOTU Takeaways](https://developer.apple.com/news/?id=lvart8mq) | macOS / visionOS | Push 3D/spatial media/USD from Mac to Vision Pro |
| **Spatial Accessories** | framesixty.com (single) | visionOS | Third-party tracked hardware |
| **Foveated Streaming** | framesixty.com (single) | visionOS | OpenXR streaming from PC/cloud |
| **Music Understanding** | macOS What's New | macOS (unclear) | On-device audio analysis |
| **NowPlaying** | macOS What's New | macOS | Playback → Lock Screen/Control Center/Dynamic Island/CarPlay |
| **DiskImageKit** | ithinkdiff (single) | macOS | Disk image management |

> Music Understanding, NowPlaying, DiskImageKit appear only in single secondary fetches — **verify against the actual Xcode 27 SDK before treating as shipping APIs.**

---

## Trade-offs and Caveats

- **Liquid Glass dual-path complexity** — `UIGlassEffect` (UIKit) and `.glassEffect()` (SwiftUI) don't auto-sync in mixed codebases; real migration cost for large UIKit apps with SwiftUI additions.
- **SwiftData gap persistence** — incremental fixes, not fundamental additions; cloud sync for shared data still absent.
- **Core ML → Core AI non-urgency** — not API-compatible; migration is a deliberate rewrite. Backlog item, not emergency.
- **SiriKit two-to-three-year window is not exact** — secondary-source interpretation; treat as directional.
- **SE proposal numbers unverified** — SE-0493/0504/0527 are blog-reported; verify against swift.org/swift-evolution before citing in docs or commits.
- **"Siri is now Gemini" commercial terms are rumor** — direction confirmed; pricing/parameters are not.
- **Rosetta 2 gaming-exception scope unclear** — don't assume your app qualifies.
- **SwiftUI `role: .prominent` not in Apple's own guide** — verify before adopting.
- **One source said "Xcode 26" for Liquid Glass recompile** — context means Xcode 27 (ships the iOS 27 SDK).

---

## Confidence and Gaps

**High confidence (Apple-official URL or multi-primary):** WWDC 2026 dates + betas + fall release; "27" numbering + macOS "Golden Gate"; Xcode 27 Apple-silicon-only + Device Hub + agentic + ACP/MCP; Foundation Models image input + server models + Dynamic Profiles + free PCC + open-source plan; Core AI existence + Core ML still functional; SwiftUI toolbar four-pack + reorderable + swipe-actions + document protocols + `@State` lazy init + ContentBuilder + AsyncImage caching; SiriKit deprecated; Intel end + Rosetta final cycle; Liquid Glass refinements + transparency slider + mandatory adoption.

**Medium confidence (multiple secondaries, no Apple fetch):** Swift 6.3+6.4 together; `anyAppleOS`, `async`-in-`defer`, `@diagnose`, `weak let` sendability, `~Sendable`, memberwise init; SF Symbols 7 / 500+; App Intents View Annotations + entity/intent schemas; visionOS 27 RealityKit specifics.

**Low confidence / single source — verify before building:** new stdlib types (UniqueArray/RigidArray/Continuation/Ref/Iterable); DiskImageKit/NSRefreshController/Music Understanding/NowPlaying; system-wide MCP in Siri/Core AI; "one Extension provider per device"; Siri/Gemini commercial terms (do not repeat).

**Not found / gaps:** specific UIKit additions beyond adaptive layouts + glass; Catalyst changes; tvOS 27 developer APIs; broader watchOS 27 APIs (only reorderable confirmed); iPadOS 27 APIs distinct from iOS 27; App Store policy changes beyond Intel binary requirements.

---

## Sources

- [Apple Developer: 5 Takeaways from the Platforms State of the Union](https://developer.apple.com/news/?id=lvart8mq) — official.
- [Apple Developer: WWDC26 SwiftUI Guide](https://developer.apple.com/wwdc26/guides/swiftui/) — official API reference.
- [Apple Developer: macOS What's New](https://developer.apple.com/macos/whats-new/) — official.
- [MacRumors: Apple Outlines Major AI and Developer Tool Updates at 2026 PSOTU](https://www.macrumors.com/2026/06/09/apple-outlines-major-ai-and-developer-tool-updates/)
- [singjupost.com: WWDC26 PSOTU Transcript](https://singjupost.com/wwdc26-platforms-state-of-the-union-june-8-2026-transcript/)
- [Fatbobman's Swift Weekly #139](https://fatbobman.com/en/weekly/issue-139/) — expert commentary.
- [blakecrosley.com: What's New in Swift (2026)](https://blakecrosley.com/blog/whats-new-swift-2026) — secondary.
- [dev.to: WWDC 2026 What's New in Swift](https://dev.to/arshtechpro/wwdc-2026-whats-new-in-swift-3nb2) — secondary.
- [dev.to: WWDC26 What's New in SwiftUI](https://dev.to/arshtechpro/wwdc26-whats-new-in-swiftui-a-developers-breakdown-1333) — secondary.
- [TechTimes: Liquid Glass iOS 27](https://www.techtimes.com/articles/317975/20260608/apple-liquid-glass-ios-27-wwdc-2026-brings-refinements-developers-must-adopt-today.htm)
- [TechTimes: App Intents Replaces SiriKit](https://www.techtimes.com/articles/318005/20260608/wwdc-2026-app-intents-replaces-sirikit-gemini-siri-migration-clock-starts.htm)
- [TechTimes: Foundation Models Swaps AI Providers](https://www.techtimes.com/articles/318039/20260609/wwdc-2026-developer-tools-foundation-models-now-swaps-ai-providers-without-code-changes.htm)
- [TechTimes: macOS 27 Intel Mac Support Ends](https://www.techtimes.com/articles/317945/20260607/macos-27-intel-mac-support-ends-wwdc-2026-four-models-cut-neural-engine-why.htm)
- [TechTimes: Rosetta 2 End of Support macOS 28](https://www.techtimes.com/articles/317445/20260530/rosetta-2-end-support-macos-28-will-break-18000-intel-apps-2027.htm)
- [framesixty.com: What's New in visionOS 27](https://framesixty.com/whats-new-in-visionos-27/) — single secondary for specifics.
- [ithinkdiff.com: macOS 27 Golden Gate Beta 1 Release Notes](https://www.ithinkdiff.com/macos-27-golden-gate-beta-1-release-notes/) — single source; verify.
- [chatforest.com: WWDC 2026 Keynote Builder Guide](https://chatforest.com/builders-log/wwdc-2026-keynote-confirmed-apple-ai-platform-builder-guide/) — single source; Tier C on commercial specifics.
- [Apple Developer: PSOTU WWDC26 Video](https://developer.apple.com/videos/play/wwdc2026/102/) — official (not fetched directly).
- [Apple Developer: WWDC26 PSOTU Recap](https://developer.apple.com/videos/play/wwdc2026/122/) — official short recap.

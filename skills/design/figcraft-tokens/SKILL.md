---
name: figcraft-tokens
description: Set up a project's design tokens (colours, type, radius, Liquid Glass) in FigCraft from its code before drawing screens, and write the shared brief that drawing agents read. Use when starting a new screen set in FigCraft, when tokens in code change, or before briefing a model to draw.
---

# FigCraft: tokens first, then screens

Screens drawn from memory drift from the app. For an existing app the code's token file (SwiftUI example: `Tokens.swift` with
`Color.slIndigo` and friends) plus its design doc decide the look; they override the "distinctive aesthetic" push of
`frontend-design`. Read them, then freeze the values for the drawing session.

## Steps

1. Read the code tokens: every colour with light and dark hex, radius and spacing constants, type sizes. Read the project's
   visual-design doc for rules the code does not show (dark mode rules, what may use shadows).
2. Write the table into a shared brief file outside the repo (for example `~/.claude/plans/<project>/COMMON.md`): tokens in light and
   dark, the reusable pieces (tab bar, header, list group, chip, button, switch), the frame grid, naming rules, the quality bar and
   the handoff the agent must return. Drawing agents read this file; it is the single place to change a value.
3. Check the table against the code: each hex in the brief appears in the token file (grep it). Colours the code does not define
   are marked "design only".
4. Optional, *untested*: bind values inside FigCraft so a later change is one edit. `style.create` (paint, text, effect) and
   `variable.bind` appeared in `list_commands` output but were never run; try them on one frame and check with `inspect.properties`
   before asking an agent to use them. Plain hex fills are the fallback.
5. Draw one reference screen first (home), check it by screenshot (skill `figcraft-screen-check`), and write what the agent got
   wrong back into the brief before commissioning more screens.

Done means: every value in the brief traces to the code, one reference screen matches the app's look, and corrections from that
screen are in the brief.

## Liquid Glass in FigCraft

Observed: FigCraft has a native glass effect, `effect.add {ids, type: "glass"}`, and the settings `depth 6, refraction 0.3,
frost 12, dispersion 0.15, lightIntensity 0.7` (via `effect.set`, with `type: "glass"` repeated inside `effect`) gave a frosted
look over a coloured shape in one test. The defaults (depth 20, refraction 0.8, frost 4) visibly smeared the backdrop in that test.

Design guidance, from Apple's description of the material and not verified in FigCraft:

- Use glass for the floating layer only: tab bar pill, round nav buttons, a bottom action strip, toasts. Cards and rows stay flat.
- A glass layer needs a translucent fill (a starting point: about `#FFFFFF66` light, `#FFFFFF1A` dark) and real content behind it,
  or it reads as a plain pill. Let scrolling content run under it.
- Do not stack glass on glass.
- In the real app a native SwiftUI `TabView` and navigation bar are expected to render the system glass on iOS 26+ without
  extra code. That is *unverified*: confirm against the SDK or Apple docs before a brief says "do not rebuild by hand"
  (see `figcraft-handoff`).

## Dark variants

Variable modes exist (`variable.createCollection` with modes, `variable.bind`, `variable.setMode` on a frame), which would make Dark a
mode switch, but binding every layer was not tried. What worked: duplicate each Light frame (`edit.duplicate`, `dx` 3600, same y) and
recolour the twin layer by layer with a fixed Light-to-Dark colour table in the shared brief (paper, card, line, ink, muted,
indigo, status colours and their text variants, tints, glass fill, category colours). Rules that mattered: the label on a filled
indigo button flips to the dark paper colour; switch knobs stay white; scrims keep their translucent black; every id passed
explicitly; screenshot each twin beside its Light frame. 34 frames took about 25 minutes with up to 4 agents in parallel.

## Brief pattern for a drawing agent

Shared file (above) plus one short file per batch (3 to 4 screens): which source files to read for real labels, the frame names
and grid positions, the state each frame shows, captions. Point at the files instead of pasting them. End with the handoff the
agent must return (frames made with ids, deviations, things it is unsure about, tool errors). A Haiku agent drew a Home screen
correctly from a brief of this shape, and moved one section to avoid an overlap and said so.

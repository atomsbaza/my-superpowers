---
name: figcraft-handoff
description: Turn approved FigCraft screens into a spec and an implementation brief for Codex or Claude (SwiftUI). Use when the user approves a FigCraft design and wants it built, or when exporting FigCraft frames for review.
---

# FigCraft: from approved design to a build brief

A drawing is a reference, not code. This skill packages it so the implementer reproduces the design without guessing and a
reviewer can compare the result with the screenshot. It is the last stage after `frontend-design-workflow` approval (the approved
frame is the visual spec) and after `figcraft-screen-check`.

## Steps

1. Confirm the user approved the screens and that the file is saved (`save_file`). Note the file path and frame ids.
2. Export one PNG per frame: one `export` call per frame with `ids: [<frame id>]`, `path: <absolute path>/<frame>.png`,
   `format: png`, `scale: 2` (create the folder first; a Haiku agent can run the whole list mechanically from an id-to-name list). Several ids in one call are composited into a single image, and without `path` the image comes back
   inline and no file is written. Put the files in `docs/design/figcraft/<screen>/` next to the `.figcraft` file. The PNG is the
   source of truth. (`figcraft-cli export` exists for scripts; its flags were not tried.)
3. Write `docs/design/figcraft/<screen>/spec.md`: per frame the layers that matter (hierarchy, text, sizes, tokens used, states),
   what is native system chrome (tab bar, navigation bar, sheets, alerts) and what is custom, and the data each field shows. Mark
   deviations from the existing app. Take exact sizes from `get_node` / `inspect_document`, not by eye.
4. Map to SwiftUI in the brief, using the project's own tokens and components (never a hardcoded hex):
   - the project's token file; fonts by Dynamic Type style, not fixed sizes;
   - SF Symbols by name (the drawing uses letter glyphs as stand-ins);
   - `TabView`, `NavigationStack`, `List`, `.sheet`, `.alert` for system chrome. Plausible on iOS 26+ but unverified: these render
     Liquid Glass by themselves, and custom floating surfaces use `.glassEffect()` in a `GlassEffectContainer`. Before the brief
     says "do not rebuild by hand", confirm both against the SDK headers or Apple docs for the project's deployment target, and
     state the confirmed API and availability guard in the brief;
   - accessibility: labels, identifiers the UI tests need, Dynamic Type, both colour schemes, Thai text through the string catalog.
5. Write the build brief: goal, files in scope, the PNGs to match, acceptance criteria, tests to add, commands to run, "do not push
   or merge", the handoff required. Send the code work to Codex through the `herdr-workflow` skill, or to a small-task model when it
   is a tiny, precisely specified change, per the project's routing rules. Claude plans and reviews; it does not write the code.
6. Review the result: build, run in the simulator, screenshot the screen, compare side by side with the exported PNG, list the
   differences, and accept only deviations that are the system's own rendering.

Done means: spec and PNGs are in the repo, the brief names every token and native component, the SwiftUI API claims were checked,
and the built screen was compared with the PNG in the simulator.

## Cautions

- Design data is made up. Do not export or paste real slips, account numbers or real totals into specs or briefs.
- Do not push design files or builds unless the user asked.
- If the design contradicts the app's rules (a shadow in dark mode, a hardcoded colour), say so in the spec instead of silently choosing.

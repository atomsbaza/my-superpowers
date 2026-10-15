---
name: figcraft-screen-check
description: Drive FigCraft through its MCP tools to draw app screens and check each one by screenshot before moving on. Use when creating or changing frames in FigCraft (figcraft or figcraft-live MCP), when delegating drawing to a cheaper model, or when a FigCraft tool call fails.
---

# FigCraft: draw a screen, then look at it

FigCraft is a Figma-class design app with an MCP server (`figcraft-cli mcp`). Written from use with FigCraft 0.6.0 and
`figcraft-cli` 0.5.1. Items marked *untested* were not tried; everything else was seen to work or fail as described.

FigCraft frames are the mockup stage of `frontend-design-workflow`: show 2 to 3 options as frames when the design is open, the
approved frame is the visual spec, and that skill's new-user review still applies. For an existing app, its tokens decide the look
(see `figcraft-tokens`).

## Pick the right server first

- `figcraft` is headless: an in-memory document nobody can see. Use it for scripted work and exports; call `save_file` to keep anything.
- `figcraft-live` attaches to the running app and edits the document open in its window. The app has to be started with a
  control port, for example `open -n -a FigCraft --args --control 47800` when it is not running (this works; with the app already
  running, `-n` starts a second instance, so quit it first). Then the user reconnects the server with `/mcp` (*untested* whether
  Claude can do that itself; it could not in practice).
- The two servers hold different documents. Tell a drawing agent which one to use and not to touch the other.
- The control port is loopback only and the docs show no token, so any local process could drive the app while it is open this way.
  Quit and relaunch normally when the live session is over.

## Loop for every screen

1. Decide the frame size, grid position and name first (iPhone 393 x 852). Child x/y are relative to the parent frame.
2. Build the frame, then one section at a time. Prefer `create_node` with `props` (fill, cornerRadius, fontSize) over later edits.
3. After each section: `screenshot` the frame alone (`ids: [<frame id>]`, `scale: 2`, `maxSize: 2400`; the image is scaled down to
   fit `maxSize`, default 1600, so a tall frame at scale 2 is silently shrunk without it). Look for text clipped or overlapping,
   content crossing the frame edge, weak contrast, anything hidden behind a floating bar, Thai glyphs.
4. Use `inspect_document` or `get_node` when a screenshot is ambiguous (sizes, fills, effects).
5. Fix or `undo`, then draw the next section.
6. At the end: one screenshot of the whole page (in live mode also `window: true`), then `save_file` and note the saved path for
   `figcraft-handoff`.

Done means: every frame was screenshotted after its last change, nothing overlaps or clips, layers are named by role, every
frame exists in light and dark when the brief lists both, and the file is saved.

## Things that fail, and what works

- `run_command` takes `command`, not `id`: `{"command":"effect.add","params":{...}}`. Find ids with `list_commands` and a `filter`.
- Delete layers with `edit.delete {ids}`; `node.delete` does not exist. A call that runs in the background reports its failure only
  in a later notification, so read the result of every destructive call before telling anyone it worked.
- `effect.add` accepts `type: glass`. `effect.set` errors with "missing field type" unless `type` is repeated inside `effect`.
- `save_file` fails if the target folder does not exist. Create the folder first.
- `open -a FigCraft file.figcraft` opened an empty document. `open_file` exists in live mode (*untested* beyond one successful
  call: it loaded the saved file and the window showed both frames).
- Never run `FigCraft --help`: the app binary starts a GUI instance instead of printing help. `figcraft-cli` is safe: running
  `figcraft-cli mcp --help` printed "unknown option" followed by the full usage text.
- Glass only reads as glass with content behind it; see `figcraft-tokens`.

## Delegating the drawing

Drawing agents have worked from a precise brief; vague prompts produced layouts that needed rework.

- Launch with the Agent tool: `subagent_type: general-purpose`, `model: haiku` pinned. `haiku-engineer` has no MCP tools, so it
  cannot draw. Subagents did get the FigCraft tools (a Haiku agent drew a screen this way), but load their schemas with ToolSearch
  first, as the brief should say.
- Keep one drawing agent per live document: new layers become the selection and commands act on it, so two agents would likely
  collide (an inference, not tried).
- The brief tells it to read the real source for labels and row order, use made-up data only, and report deviations.
- Treat its handoff as a claim: take your own screenshot of every frame before reporting it done. Agents re-laid out sections that
  did not fit; accept or send back, but look.
- Safe in parallel with drawing: web research, reading code, writing docs.

## Data boundary

Design files go in the repo (`docs/design/figcraft/`). Never draw real slips, account numbers, QR codes, bank logos or real
totals. Use the made-up sample data from the project's brief.

---
name: tessera-panes
description: Drive and observe a neighboring Tessera pane from an agent session -- discover panes, send keystrokes, poll or stream their output. Use when running inside a Tessera terminal pane and asked to control, read, or coordinate with another pane (e.g. a Codex or Claude session next to you), or when the user mentions tessera-ctl, subscribe_output, read_output, or "the pane next to me."
---

# Tessera Panes

Tessera (`~/Work/tessera`) is a terminal app where each split/tab is a pane with its own PTY
session, automatable over a local control socket via the `tessera-ctl` CLI. This skill covers
the read side (CONTRACT.md v5, `read_output`/`subscribe_output`) added to complement the write
side that already existed (`send_text`, v2) -- together they let one agent in one pane drive
and observe another agent (or shell) in a neighboring pane.

## Finding `tessera-ctl`

Prefer the release bundle path; fall back to a debug/release cargo build if the app hasn't
been packaged yet:

```bash
for candidate in \
  "/Applications/Tessera.app/Contents/MacOS/tessera-ctl" \
  "$HOME/Work/tessera/src-tauri/target/release/tessera-ctl" \
  "$HOME/Work/tessera/src-tauri/target/debug/tessera-ctl"; do
  if [ -x "$candidate" ]; then
    TESSERA_CTL="$candidate"
    break
  fi
done
```

Every example below assumes `$TESSERA_CTL` resolves. If none of the candidates exist, the app
needs building (`cargo build [--release]` from `tessera/src-tauri/`) before any of this works.

## Discovering panes

```bash
"$TESSERA_CTL" list_sessions
```

Returns every live session across every tab: `sessionId`, `title`, `tabIndex`, `command`, plus
`remote`/`shared`/`viewer` flags. Find the pane you were asked to work with by its title or
command -- session ids are assigned at spawn time and not stable across a restart, so don't
hardcode one across a conversation; re-run `list_sessions` if in doubt.

## Sending input: `\r` vs `\n`

`send_text {sessionId, text}` writes bytes into that pane's PTY, exactly as if typed. The
submit character matters and the two are NOT interchangeable:

- A plain shell (bash/zsh/sh) accepts `\n` to submit a line.
- A TUI agent (Claude Code, Codex, or any full-screen prompt-box program) usually has its own
  input widget that only submits on a real carriage return, `\r`. Sending `\n` into one of
  these can just insert a newline into the input box instead of submitting it.

When unsure which kind of pane you're driving, check `command` from `list_sessions` (e.g.
`claude`, `codex`, vs `bash`/`zsh`/`sh`) and pick the submit character accordingly. If a
submitted-looking command visibly doesn't run (confirmed via `read_output`), retry with the
other terminator before assuming something else is wrong.

## The marker-poll pattern

There's no acknowledgement for a PTY write -- `send_text` returning `ok:true` only means the
bytes were queued, not that the target program has processed them yet. To know a command has
actually landed and produced output, send a unique marker and poll for it:

```bash
marker="agent-bridge-$$-$RANDOM"
"$TESSERA_CTL" send_text "{\"sessionId\":$SESSION_ID,\"text\":\"echo $marker\r\"}"

for i in 1 2 3 4 5 6 7 8; do
  resp="$("$TESSERA_CTL" read_output "{\"sessionId\":$SESSION_ID}")"
  if echo "$resp" | grep -q "$marker"; then
    break
  fi
  sleep "0.$((i * 2))" # simple backoff: 0.2s, 0.4s, 0.6s, ...
done
```

This is the reliable building block underneath anything more elaborate ("wait for this
command to finish", "confirm the other agent saw my message") -- always prefer it over a fixed
sleep.

## Signal vs text: `subscribe_output` + `read_output` together

`subscribe_output {sessionId}` opens a long-lived connection that streams raw PTY bytes
(ANSI escapes included) the moment they're written -- it's a good *signal* ("something just
happened in that pane") but a poor source of clean text, since it's not rendered and can split
multi-byte characters or ANSI sequences across chunks. The reliable pattern is:

1. Use `subscribe_output` as a wake-up: something changed.
2. Then call `read_output {sessionId, lines?}` to get the CURRENT rendered screen as plain
   text (default 100 lines, capped at 1000) -- this is what the pane actually looks like right
   now, ANSI-free, because it reads xterm's rendered buffer rather than the raw byte stream.

Don't try to parse the `subscribe_output` stream directly as if it were clean text; it isn't.

## Etiquette

Only drive panes the user has explicitly designated for this workflow (e.g. "the Codex pane
on the right", "the pane you just split off"). Never `send_text` into a pane you weren't
invited to control just because `list_sessions` happens to show it -- reading via
`read_output`/`subscribe_output` is comparatively low-risk (it's observation), but writing
changes what another agent or the user is doing.

## Limitations

- `read_output` shows the pane's full rendered screen exactly as it looks -- prompts, borders,
  status lines, and any other TUI chrome are all included; there's no way to ask for "just the
  agent's reply" if the pane is running something with its own UI frame.
- `subscribe_output`'s stream is raw: ANSI escape sequences included, no server-side stripping.
  It is a signal channel, not a clean-text feed -- see the pattern above.
- Local sessions only: `subscribe_output` on a remote (`tessera-remoted`) or collab-viewer pane
  returns `"not a local session"`. `read_output` has no such restriction (it reads the local
  render regardless of what's behind the pane).
- A session allows at most 5 simultaneous `subscribe_output`/share taps; a 6th attempt errors
  with `"subscriber limit reached for session {id}"`.

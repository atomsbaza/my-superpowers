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
TESSERA_CTL=""
for candidate in \
  "/Applications/Tessera.app/Contents/MacOS/tessera-ctl" \
  "$HOME/Work/tessera/src-tauri/target/release/tessera-ctl" \
  "$HOME/Work/tessera/src-tauri/target/debug/tessera-ctl"; do
  if [ -x "$candidate" ]; then
    TESSERA_CTL="$candidate"
    break
  fi
done
echo "$TESSERA_CTL"
[ -n "$TESSERA_CTL" ] || { echo "tessera-ctl not found - build src-tauri first" >&2; exit 1; }
```

On Windows, `tessera-ctl` talks to a named pipe (`tessera-control`) instead of a Unix socket --
see the `cfg(windows)` branch in `tessera_ctl.rs` -- but the request/response JSON and every
command in this skill are otherwise identical.

`$TESSERA_CTL` only lives in the shell that ran the loop above. Each Bash tool call in an agent
session is a fresh shell with no env carry-over, so run the loop once, note the resolved
absolute path it prints/assigns, and substitute that literal path into every subsequent command
below instead of relying on `$TESSERA_CTL` still being set (or re-run the loop at the top of
every command block that needs it). If none of the candidates exist, the app needs building
(`cargo build [--release]` from `tessera/src-tauri/`) before any of this works.

## Discovering panes

```bash
"$TESSERA_CTL" list_sessions
```

Returns every live session across every tab: `sessionId`, `title`, `tabIndex`, `command`, plus
`remote`/`shared`/`viewer` flags, and (CONTRACT.md v6) `agentLabel: string | null` and
`selectedTarget: boolean`. Find the pane you were asked to work with by its title, command, or
`agentLabel` -- session ids are assigned at spawn time and not stable across a restart, so don't
hardcode one across a conversation; re-run `list_sessions` if in doubt. A viewer session
(`viewer: true`) always has `agentLabel: null` and `selectedTarget: false` -- it is never a
labelable or selectable routing recipient.

## Natural-language recipient routing

When asked to “send this to Codex”, “send to the other agent”, or “send to the selected pane”,
run a **fresh** `list_sessions` first. Never reuse an id or a recipient choice from an earlier
turn.

- An explicit name resolves to exactly one case-insensitive exact `agentLabel` match among
  non-viewer sessions. Zero or multiple matches (labels are not server-enforced-unique) means
  ask the user rather than falling back to a `command`/title guess.
- “Selected pane” resolves only through `selectedTarget: true`. There is at most one across the
  whole app by construction; if none is set, ask the user which visible pane to use.
- “Other agent” requires this pane's own `TESSERA_SESSION_ID` environment variable. If it's
  missing, empty, or non-numeric, you are not a local pane (remote/viewer panes never receive
  it) -- ask the user to name a recipient explicitly. Otherwise resolve `selectedTarget` (rule
  above) and additionally require its `sessionId` differ from your own `TESSERA_SESSION_ID`. If
  they're equal (the user selected your own pane) or no target is selected, ask rather than
  guessing or sending to yourself.
- Do not infer a recipient from tab order, physical proximity, process names, or a partial
  label. Never route to a viewer pane under any of these rules.

Once exactly one live, authorized recipient is resolved, call
`send_text {sessionId, text, fromSessionId?}` immediately. For the "other agent" rule, always
pass your own `TESSERA_SESSION_ID` as `fromSessionId` -- the app rejects the request
server-side if `fromSessionId` equals the target `sessionId`, so this is a real safety net even
if the resolution logic above is buggy or bypassed, not just a courtesy; omit `fromSessionId`
for the label/selected-pane rules. For an agent/TUI use `\r` to submit; use `\n` only when the
recipient is known to be a plain shell and the user needs a literal newline behavior. Report the
visible label (or command, if unlabelled) and location after the write, e.g. `Sent to Codex
(tab 2, right pane).` `ok:true` means queued to the PTY, not that the recipient understood or
completed the request; report a delivery error (including the `fromSessionId` self-rejection)
rather than claiming success.

To label your own pane, or another pane the user asks you to label, call
`set_agent_label {sessionId, label}` -- `label` must be non-blank after trimming and at most 40
Unicode code points, or the call fails with `ok:false`. Viewer sessions cannot be labeled.

For a response or completion claim, observe rather than sleep: baseline with `read_output`,
then poll for a meaningful change and 2–3 stable consecutive renders. Prefer a bounded direct
socket `subscribe_output` wake-up for local panes, followed by `read_output`; subscriptions are
raw byte signals, can fail, and do not prove the agent is finished. If output remains unstable or
the deadline expires, say it is still working/unknown instead of claiming delivery or completion.

For the common "send this and have it auto-submit" case, `tessera-ctl send <target> <text>`
(see `docs/AGENT_BRIDGE.md`) wraps the list/resolve/send sequence below into one command --
reach for the manual form only when you need to omit the trailing terminator or otherwise
deviate from straight auto-submit.

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

If genuinely unsure, `\r` is the safer default for either kind of pane -- the PTY line
discipline maps a carriage return to a newline for plain shells too, so the marker-poll
example below uses `\r` throughout rather than contradicting the `\n` guidance above.

## The marker-poll pattern

There's no acknowledgement for a PTY write -- `send_text` returning `ok:true` only means the
bytes were queued, not that the target program has processed them yet. To know a command has
actually landed and produced output, send a unique marker and poll for it.

**Shell panes (bash/zsh/sh):** `read_output` returns the RENDERED screen, which already
contains the echoed input line -- if you poll for the same marker text you just sent, the
first poll matches on the echo before the command has done anything. Search for a token that
only appears in the command's *output*, not in the typed text:

```bash
marker="agent-bridge-$$-$RANDOM"
resp="$("$TESSERA_CTL" send_text "{\"sessionId\":$SESSION_ID,\"text\":\"m=$marker; echo \\\"done-\$m\\\"\r\"}")" || { echo "send_text failed: $resp" >&2; exit 1; }

found=0
deltas="0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6"
last="1.6"
for d in $deltas; do
  resp="$("$TESSERA_CTL" read_output "{\"sessionId\":$SESSION_ID}")" || { echo "read_output failed: $resp" >&2; exit 1; }
  if echo "$resp" | grep -q "done-$marker"; then
    found=1
    break
  fi
  # backoff between reads: 0.2s, 0.4s, 0.6s, ... skip sleeping after the last read
  # (nothing would read the result), so the honest total wait is ~5.6s, not 7.2s
  [ "$d" = "$last" ] || sleep "$d"
done
[ "$found" = 1 ] || { echo "marker $marker not seen after ~5.6s" >&2; exit 1; }
```

**TUI agent panes (Claude Code, Codex, or any other full-screen prompt-box program):** the
marker-poll above does NOT transfer -- you cannot send a shell variable assignment to a chat
input box, and there's no echo/output distinction to exploit. Instead this splits into two
separate questions, each needing its own check:

- **Did my input land?** Capture the rendered screen from `read_output` before sending -- check
  that this baseline call actually succeeded (exit status, or the response's `ok` field) and
  abort if it didn't; an errored baseline must not silently be treated as "empty," or the first
  successful poll afterward will look like a change and be misread as "input landed." Then poll
  `read_output` again and compare: wait for the screen to CHANGE from that baseline (new
  text appended, a spinner replaced by a reply, etc.), using the same backoff. A screen
  identical to the baseline means nothing has happened yet, not that the input landed.
- **Is the target agent done responding?** First-change detection does NOT answer this --
  sending into a TUI prompt box changes the screen immediately (the input box clears, a
  spinner/thinking indicator appears), so the very first poll already differs from the
  baseline while the target agent is still working. Instead poll for STABILITY: keep calling
  `read_output` on the same backoff and compare each response to the previous one (e.g. hash
  the last N lines); only declare the pane idle once the screen is identical across 2-3
  consecutive polls in a row. A single differing poll just means something is still changing.

This is the reliable building block underneath anything more elaborate ("wait for this
command to finish", "confirm the other agent saw my message") -- always prefer it over a fixed
sleep.

## Signal vs text: `subscribe_output` + `read_output` together

`tessera-ctl` cannot be used for `subscribe_output`: it reads exactly one response line and
exits (that's fine for `send_text`/`read_output`/`list_sessions`, which are one-shot
request/response, but `subscribe_output` needs the connection held open to receive the stream
that follows the initial ack). Running `"$TESSERA_CTL" subscribe_output '{"sessionId":N}'`
gets you `{"ok":true,"result":{"subscribed":N}}` and then nothing -- the process has already
exited, which looks exactly like "the pane produced no output" but isn't.

To actually consume `subscribe_output`, connect to the Unix socket directly (default
`~/.tessera/control.sock`) and keep reading. The ack is not automatically a success: on any
error (`"not a local session"`, `"subscriber limit reached for session {id}"`, `"no such
session: {id}"`) the server writes that one line as the ack and then closes the socket
immediately -- if the ack is discarded unread, the next read just returns EOF, which looks
exactly like "the pane produced no output" but isn't. Always check `ok` on the ack before
looping. On the success path, a idle pane may never send another frame, so also set a socket
timeout and an overall deadline rather than blocking forever -- and since this reads in a
loop, run it as a bounded background process writing to a file rather than as a blocking
foreground call, or it wedges the calling agent's own Bash tool:

```python
import base64, json, socket, sys, time

sock_path, session_id, deadline_s = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    s.connect(sock_path)
except OSError as e:
    print("subscribe_output: connect to %s failed: %s" % (sock_path, e), file=sys.stderr)
    sys.exit(1)
s.sendall(('{"id":1,"method":"subscribe_output","params":{"sessionId":%d}}\n' % session_id).encode())

deadline = time.monotonic() + deadline_s
s.settimeout(deadline_s)  # bound the ack read too, not just the streaming loop below
f = s.makefile("rb")
ack_line = f.readline()
if not ack_line:
    print("subscribe_output: connection closed before ack", file=sys.stderr)
    sys.exit(1)
ack = json.loads(ack_line)
if not ack.get("ok"):
    print("subscribe_output failed: %s" % ack.get("error"), file=sys.stderr)
    sys.exit(1)

buf = bytearray()
while True:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        print("subscribe_output: deadline reached, no closed event", file=sys.stderr)
        break
    s.settimeout(remaining)
    try:
        line = f.readline()
    except socket.timeout:
        print("subscribe_output: read timed out", file=sys.stderr)
        break
    if not line:
        break
    obj = json.loads(line)
    if obj.get("event") == "closed":
        break
    if obj.get("event") == "output":
        chunk = base64.b64decode(obj["data"])  # data is base64 -- decode before writing
        sys.stdout.buffer.write(chunk)
        sys.stdout.flush()
```

Run it in the background against a fixed output file (e.g. `python3 -u subscribe.py "$SOCK"
"$SESSION_ID" 30 > /tmp/sub-out.log 2>&1 &`) and poll that file, rather than calling it as a
blocking foreground command that ties up the Bash tool for the whole subscription window.
Redirect stderr into the same log (or a separate `2> /tmp/sub-out.err` path) too -- the
connect/ack/timeout diagnostics above are only useful if they survive being backgrounded.
Both the explicit `flush()` in the loop and `-u` matter: redirecting stdout to a file makes it
block-buffered (~8 KiB), so without them the file stays empty until that buffer fills or the
process exits, even though bytes are being written.

Each streamed frame looks like:

```
{"event":"output","sessionId":<id>,"data":"<base64 of the raw PTY chunk bytes>"}
```

and on session exit the server sends one final frame and closes the connection:

```
{"event":"closed","sessionId":<id>}
```

`data` is base64-encoded raw PTY bytes (ANSI escapes included, not rendered) -- grepping the
raw JSONL lines for a marker will never match, because the marker text only exists after
base64-decoding. Decode and concatenate `data` across events before searching for anything.
Because chunks are forwarded as soon as they're read (no cross-read buffering), a multi-byte
character or ANSI sequence can also land split across two chunks, so treat the stream as a
signal that bytes arrived and reassemble fully before treating it as text.

Given that, the reliable pattern is:

1. Use the socket reader above as a wake-up: something changed.
2. Then call `"$TESSERA_CTL" read_output '{"sessionId":N,"lines":?}'` to get the CURRENT
   rendered screen as plain text (default 100 lines, capped at 1000) -- this is what the pane
   actually looks like right now, ANSI-free, because it reads xterm's rendered buffer rather
   than the raw byte stream.

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
- `subscribe_output`'s stream is raw and base64-encoded (ANSI escape sequences included, no
  server-side stripping), and `tessera-ctl` cannot hold the connection open to receive it. It
  is a signal channel, not a clean-text feed, and needs the direct-socket reader -- see the
  pattern above.
- Local sessions only: `subscribe_output` on a remote (`tessera-remoted`) or collab-viewer pane
  returns `"not a local session"`. `read_output` has no such restriction (it reads the local
  render regardless of what's behind the pane).
- A session allows at most 5 simultaneous `subscribe_output`/share taps; a 6th attempt errors
  with `"subscriber limit reached for session {id}"`.

The hardcoded numbers and error strings throughout this skill (100/1000-line `read_output`
defaults, the 5-tap subscriber cap, the exact error text) mirror CONTRACT.md v5 as of this
writing -- if the two disagree, CONTRACT.md is the source of truth and wins.

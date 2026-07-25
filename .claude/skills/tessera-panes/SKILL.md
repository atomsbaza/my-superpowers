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
actually landed and produced output, send a unique marker and poll for it.

**Shell panes (bash/zsh/sh):** `read_output` returns the RENDERED screen, which already
contains the echoed input line -- if you poll for the same marker text you just sent, the
first poll matches on the echo before the command has done anything. Search for a token that
only appears in the command's *output*, not in the typed text:

```bash
marker="agent-bridge-$$-$RANDOM"
"$TESSERA_CTL" send_text "{\"sessionId\":$SESSION_ID,\"text\":\"m=$marker; echo \\\"done-\$m\\\"\r\"}"

found=0
for d in 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6; do
  resp="$("$TESSERA_CTL" read_output "{\"sessionId\":$SESSION_ID}")"
  if echo "$resp" | grep -q "done-$marker"; then
    found=1
    break
  fi
  sleep "$d" # backoff: 0.2s, 0.4s, 0.6s, ... up to ~7.2s total
done
[ "$found" = 1 ] || { echo "marker $marker not seen after ~7.2s" >&2; exit 1; }
```

**TUI agent panes (Claude Code, Codex, or any other full-screen prompt-box program):** the
marker-poll above does NOT transfer -- you cannot send a shell variable assignment to a chat
input box, and there's no echo/output distinction to exploit. Instead this splits into two
separate questions, each needing its own check:

- **Did my input land?** Capture the rendered screen from `read_output` before sending, then
  poll `read_output` again and compare: wait for the screen to CHANGE from that baseline (new
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
s.connect(sock_path)
s.sendall(('{"id":1,"method":"subscribe_output","params":{"sessionId":%d}}\n' % session_id).encode())

f = s.makefile("rb")
ack = json.loads(f.readline())
if not ack.get("ok"):
    print("subscribe_output failed: %s" % ack.get("error"), file=sys.stderr)
    sys.exit(1)

buf = bytearray()
deadline = time.monotonic() + deadline_s
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
        buf += base64.b64decode(obj["data"])  # data is base64 -- decode before searching
```

Run it in the background against a fixed output file (e.g. `python3 subscribe.py "$SOCK"
"$SESSION_ID" 30 > /tmp/sub-out.log &`) and poll that file, rather than calling it as a
blocking foreground command that ties up the Bash tool for the whole subscription window.

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

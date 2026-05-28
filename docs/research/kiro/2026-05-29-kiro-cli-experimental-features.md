# Research: Kiro CLI Experimental Features

## Summary

Kiro CLI ships six experimental features (excluding Delegate) that can be toggled individually via the `/experiment` interactive menu or direct `kiro-cli settings` commands. The features span persistent knowledge storage, conversation branching, AI-managed task lists, visible reasoning traces, session-scoped file snapshotting, and a context-window usage indicator. All experiments default to disabled, several are marked "classic only" (meaning they apply to the classic chat interface, not the terminal UI variant), and all should be treated as subject to change or removal.

---

## Managing Experiments

### The `/experiment` Command

The `/experiment` command opens an interactive menu listing all available experiments with their current on/off status. It is the canonical way to toggle features without memorising individual setting names.

All experiments are also accessible via `kiro-cli settings <setting-name> true|false` for scripted or persistent configuration. Setting names follow the pattern `chat.enable<FeatureName>`.

All experimental commands (`/experiment`, `/knowledge`, `/todo`, `/tangent`, `/checkpoint`) support fuzzy search via **Ctrl+S**.

**General adoption advice from the docs:** test on non-critical projects first, maintain backups before using any file-modifying features, and restart Kiro CLI after toggling settings if commands become unavailable. File feedback via `kiro issue`.

Source: [Kiro CLI Experimental Features Overview](https://kiro.dev/docs/cli/experimental/)

---

## Feature 1 — Knowledge Management

### What It Does

Provides a persistent, queryable knowledge base that survives across chat sessions. You index files, directories, or text content once; Kiro can then search that indexed content in any future session. Each agent maintains its own isolated knowledge base.

### How to Enable

```
kiro-cli settings chat.enableKnowledge true
```

Or select "Knowledge Management" via `/experiment`.

**Classic-only:** No — the settings reference does not mark this feature as classic-only.

### Commands and Flags

| Command | Description |
|---|---|
| `/knowledge show` | List all entries with creation dates, file counts, and active operations |
| `/knowledge add --name <n> --path <p>` | Index a file or directory |
| `/knowledge add ... --include <glob>` | Only index matching files |
| `/knowledge add ... --exclude <glob>` | Skip matching files |
| `/knowledge add ... --index-type Fast\|Best` | Choose index strategy (see below) |
| `/knowledge remove` | Delete an entry by name or path |
| `/knowledge update` | Refresh an entry (preserves existing patterns) |
| `/knowledge clear` | Remove all entries — prompts for confirmation; irreversible |
| `/knowledge cancel [id]` | Cancel a background indexing operation (or all with no ID) |

**Index types:**

- `Fast` — BM25 lexical (keyword) search. Rapid, low resource usage. Best for logs, structured code, known terms.
- `Best` — Semantic search (all-minilm-l6-v2 model). Understands meaning and related concepts via natural language. Slower, higher resource cost.

### Supported File Types

Text (`.txt`, `.log`), Markdown (`.md`, `.mdx`), JSON, config files (`.ini`, `.yaml`, `.toml`), code files (Rust, Python, JavaScript, Java, C++, and others), and special files (Dockerfile, Makefile, README).

Binary files are silently ignored.

### Storage Location

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/kiro-cli/knowledge_bases/` |
| Linux | `~/.local/share/kiro-cli/knowledge_bases/` |
| Windows | `%LOCALAPPDATA%\kiro-cli\knowledge_bases\` |

### Practical Use Cases

- Index a large codebase once; query it in later sessions by symbol, concept, or behaviour rather than re-pasting files.
- Maintain a project's documentation corpus so Kiro can answer questions against it persistently.
- Store log archives for long-running debugging investigations that span multiple sessions.
- Index configuration files so Kiro can resolve parameter values without manual lookups.

### Limitations and Caveats

- Binary files are skipped entirely.
- Very large files are chunked, which can split logically related content across chunk boundaries.
- Large directories require significant wall-clock time to index (background, but consumes disk and CPU).
- There is no automatic cleanup of stale or unused entries — you must run `/knowledge remove` or `/knowledge clear` manually.
- `/knowledge clear` cannot be undone.

Source: [Knowledge Management](https://kiro.dev/docs/cli/experimental/knowledge-management)

---

## Feature 2 — Tangent Mode

### What It Does

Creates a checkpoint of the current conversation state, letting you branch off to explore a side question, alternative approach, or clarifying topic without polluting the main thread. When you exit tangent mode, the conversation returns to the checkpoint. Tangent content is discarded unless you explicitly use `tail` to carry the final exchange back.

### How to Enable

```
kiro-cli settings chat.enableTangentMode true
```

Or select "Tangent Mode" via `/experiment`.

**Classic-only:** Yes — the settings reference marks this as "classic only". It does not apply to the terminal UI variant.

### Commands and Invocation

| Action | Method |
|---|---|
| Enter tangent mode | `/tangent` or **Ctrl+T** |
| Exit (discard tangent) | `/tangent` or **Ctrl+T** again |
| Exit (keep last Q&A) | `/tangent tail` |

**Keyboard shortcut customisation:**

```
kiro-cli settings chat.tangentModeKey [key]    # default: t
```

**Auto-tangent for help queries:**

```
kiro-cli settings introspect.tangentMode true
```

### Visual Indicators

| Mode | Prompt |
|---|---|
| Normal | `>` (magenta) |
| Tangent | `↯ >` (yellow + magenta) |
| Tangent + agent | `[dev] ↯ >` (cyan + yellow + magenta) |

### Practical Use Cases

- Ask a clarifying question about the current topic without it becoming part of the conversation history.
- Evaluate an alternative design approach before committing to it.
- Get quick Kiro CLI command help mid-task.
- Test a conceptual assumption without derailing the main discussion.

### Limitations and Caveats

- Tangent conversations that are exited without `tail` are **permanently lost** — they cannot be recovered.
- Only **one level of tangent** is supported. Nesting tangents inside tangents is not possible.
- The feature is experimental and may be removed or redesigned.
- Classic-only: not available in the terminal UI.

Source: [Tangent Mode](https://kiro.dev/docs/cli/experimental/tangent-mode)

---

## Feature 3 — TODO Lists

### What It Does

Kiro automatically generates structured, persistent task lists when it determines a problem has multiple discrete steps. Lists survive across sessions, allowing work to be paused and resumed. The system distinguishes between the `todo` tool (which Kiro calls internally to create and update lists) and the `/todo` command (which you invoke to manage existing lists).

### How to Enable

```
kiro-cli settings chat.enableTodoList true
```

Or select "TODO Lists" via `/experiment`.

**Classic-only:** Yes — marked as "classic only" in the settings reference.

### Commands and Flags

| Command | Description |
|---|---|
| `/todo view` | Display existing TODO lists with completion status (✓ done, ✗ in-progress) |
| `/todo resume` | Load a list back into the current chat so Kiro can continue it |
| `/todo clear-finished` | Delete all completed lists |
| `/todo delete` | Delete a specific list |
| `/todo delete --all` | Delete all lists |

**Note:** You cannot directly edit list content. Kiro manages item creation, marking, addition, and removal. Direct JSON file editing is unsupported and may break list state.

### Storage

Lists persist as timestamped JSON files at:

```
<project-directory>/.kiro/cli-todo-lists/
```

Each file stores task descriptions, completion statuses, and contextual metadata.

### Practical Use Cases

- Multi-stage database migrations: Kiro breaks the work into discrete, trackable steps with visible progress.
- Feature implementation (e.g. an authentication system): each component becomes a task.
- CI/CD pipeline setup: separate pipeline stages become individually trackable items.
- Any work spanning multiple sessions where continuity and progress visibility matter.

### Limitations and Caveats

- Tasks **cannot be reordered** after list creation.
- Lists **cannot be merged or split**.
- You cannot directly edit tasks — you must resume an active list and ask Kiro to modify it.
- Classic-only: not available in the terminal UI.

Source: [TODO Lists](https://kiro.dev/docs/cli/experimental/todo-lists)

---

## Feature 4 — Thinking Tool

### What It Does

Reveals Kiro's internal reasoning process for complex problems. When enabled, responses to difficult queries include a visible step-by-step breakdown of how Kiro reached its conclusions. Activation is automatic when Kiro judges a task warrants it — you do not manually trigger a "think" step.

### How to Enable

```
kiro-cli settings chat.enableThinking true
```

To disable:

```
kiro-cli settings chat.enableThinking false
```

To check current status:

```
kiro-cli settings chat.enableThinking
```

Or select "Thinking" via `/experiment`.

**Classic-only:** No — not marked as classic-only in the settings reference.

### Automatic Triggers

Kiro activates the thinking trace when it encounters:

- Complex multi-step problem-solving
- Trade-off analysis between competing approaches
- Multi-step implementation planning with dependencies
- Systematic debugging of intricate issues
- Architectural decisions involving multiple factors

### Practical Use Cases

- **Learning:** Observe how Kiro decomposes a problem — useful for onboarding team members to AI-assisted reasoning patterns.
- **Architecture reviews:** Evaluate why Kiro recommended a microservices split or a monolith.
- **Debugging complex bugs:** Understand the diagnostic path, not just the fix.
- **Algorithm selection:** See the performance trade-off analysis before accepting a recommendation.
- **Validation:** Sanity-check that Kiro's reasoning chain is sound before acting on it.

### Limitations and Caveats

- Adds **latency** to responses — visible thinking consumes additional tokens and processing time.
- Produces **longer responses**, which can be noisy for simple tasks.
- Recommended practice: enable for complex or high-stakes problems, disable during fast implementation iterations.

Source: [Thinking Tool](https://kiro.dev/docs/cli/experimental/thinking)

---

## Feature 5 — Checkpointing

### What It Does

Creates session-scoped, Git-like snapshots of file state after each conversation turn (and each tool call within a turn). Kiro maintains a shadow git repository to track changes. At any point in a session, you can diff between states or restore an earlier snapshot. When the session ends, the shadow repository is cleaned up automatically — checkpoints do not persist.

In git repositories, checkpointing auto-enables. In non-git directories, you must initialise manually.

### How to Enable

```
kiro-cli settings chat.enableCheckpoint true
```

Or select "Checkpointing" via `/experiment`.

**Classic-only:** Yes — marked as "classic only" in the settings reference.

### Commands and Flags

| Command | Description |
|---|---|
| `/checkpoint init` | Manually initialise checkpoints in a non-git directory |
| `/checkpoint list` | Show all turn-level checkpoints with file stats and timestamps |
| `/checkpoint list --limit N` | Limit display to N most recent checkpoints |
| `/checkpoint expand <tag>` | Show tool-level checkpoints nested inside a given turn |
| `/checkpoint diff <tag1> [tag2\|HEAD]` | Compare two checkpoint states; `tag2` defaults to `HEAD` if omitted |
| `/checkpoint restore [<tag>]` | Revert modifications and deletions; newly created files are preserved |
| `/checkpoint restore [<tag>] --hard` | Make workspace exactly match checkpoint; deletes files created after it |
| `/checkpoint clean` | Delete the session's shadow repository |

### Practical Use Cases

- **Safe experimentation:** Try a refactoring approach, inspect the diff, and revert if it degrades the code.
- **Side-by-side comparison:** Generate two implementations in separate turns, then diff them.
- **Progress tracking:** Review what Kiro changed across all turns in a long session.
- **Error recovery:** Return to the last known-working state without manually undoing changes.

### Limitations and Caveats

- **Session-scoped only**: all checkpoints are discarded when the session ends.
- Only tracks files **modified during the session** — pre-existing untouched files are invisible.
- **Restoring a checkpoint also unwinds the conversation** — all messages after the checkpoint are removed.
- `--hard` restore **permanently deletes** files created after the checkpoint.
- Classic-only: not available in the terminal UI.

Source: [Checkpointing](https://kiro.dev/docs/cli/experimental/checkpointing)

---

## Feature 6 — Context Usage Percentage

### What It Does

Displays the current context window consumption as a colour-coded percentage directly in the chat prompt.

| Usage | Colour |
|---|---|
| Under 50% | Green |
| 50–89% | Yellow |
| 90–100% | Red |

### How to Enable

```
kiro-cli settings chat.enableContextUsageIndicator true
```

Or select "Context Usage Percentage" via `/experiment`.

**Classic-only:** Yes — marked as "classic only" in the settings reference.

### Practical Use Cases

- Warn yourself before a conversation gets long enough to cause context truncation or quality degradation.
- Know when to start a new session to stay in the green zone.

### Limitations and Caveats

- Passive display only — does not warn, block, or summarise automatically.
- Classic-only: not available in the terminal UI.
- Setting name `chat.enableContextUsageIndicator` differs from the generic pattern implied by the main page. Use the settings-reference name.

Source: [Kiro CLI Experimental Features Overview](https://kiro.dev/docs/cli/experimental/), [Settings Reference](https://kiro.dev/docs/cli/reference/settings)

---

## Trade-offs / Caveats

- **"Classic only" scope**: Tangent Mode, TODO Lists, Checkpointing, and Context Usage Percentage are all tagged "classic only". They do not apply to the terminal UI variant. Teams using the terminal UI should verify which features are actually accessible before planning adoption.
- **Setting name discrepancy for Context Usage Percentage**: Use `chat.enableContextUsageIndicator` (from the settings reference), not the generic name implied by the main experimental page.
- **No cross-session persistence for Checkpointing**: Checkpoints evaporate with the session. Use actual version control before starting destructive Kiro sessions.
- **Knowledge base maintenance burden**: No automatic staleness detection. Establish a discipline of running `/knowledge update` when code changes significantly.
- **Thinking Tool latency**: Leave it disabled during rapid implementation cycles; enable contextually for complex or high-stakes problems.
- **Tangent Mode data loss**: Tangent conversations are unrecoverable. Use `tail` mode whenever the tangent produces anything worth keeping.
- **All features are experimental**: May change or be removed. Do not build hard dependencies on current behaviour or command signatures.

---

## Sources

- [Kiro CLI Experimental Features Overview](https://kiro.dev/docs/cli/experimental/)
- [Knowledge Management](https://kiro.dev/docs/cli/experimental/knowledge-management)
- [Tangent Mode](https://kiro.dev/docs/cli/experimental/tangent-mode)
- [TODO Lists](https://kiro.dev/docs/cli/experimental/todo-lists)
- [Thinking Tool](https://kiro.dev/docs/cli/experimental/thinking)
- [Checkpointing](https://kiro.dev/docs/cli/experimental/checkpointing)
- [Settings Reference](https://kiro.dev/docs/cli/reference/settings)

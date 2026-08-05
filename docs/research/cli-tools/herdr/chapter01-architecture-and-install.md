# Chapter 1: Architecture & Installation

Herdr is an agent-native terminal multiplexer engineered for the high-throughput orchestration of autonomous AI coding assistants. Unlike human-centric multiplexers like tmux or Zellij, Herdr operates as a persistent execution runtime with structural awareness of the processes running within its pseudo-terminals (PTYs).

## Client-Server Architecture

Herdr utilizes a bifurcated architecture to ensure operational reliability:

- **Background Server:** Managed by the `herdr server` process, it maintains the state of workspaces, tabs, panes, and agent classifications. It survives client disconnections and SSH drops, so long-running tasks keep running while you're detached. A server/machine restart is a different case: Herdr restores layout and cwd and can resume supported agents' native conversations (if integrations are installed), but ordinary running processes are not preserved across a restart.
- **Lightweight Client:** Acts as a rendering viewport and command-line interface. It translates input gestures and displays output streams without hosting the underlying logic.

## Multi-Platform Installation

Herdr is built in Rust to provide local user-space execution, minimizing permission-based friction.

### Unix-Based Systems (Linux/macOS)

- **Shell installer:** `curl -fsSL https://herdr.dev/install.sh | sh`
- **Homebrew:** `brew install herdr`
- **mise:** `mise use -g herdr`
- **Nix:** Available via Nix derivations.

### Windows Systems (Beta)

Herdr runs natively in PowerShell via an app-local ConPTY runtime:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
```

## Shell Integration

To enable dynamic shell completions for Zsh, ensure your `fpath` is configured correctly:

```zsh
mkdir -p ~/.zfunc
herdr completion zsh > ~/.zfunc/_herdr
```

Add the following to your `.zshrc`:

```zsh
fpath=(~/.zfunc $fpath)
autoload -Uz compinit
compinit
```

---

Next: [Chapter 2 — Core CLI Command Hierarchy](chapter02-cli-command-hierarchy.md)

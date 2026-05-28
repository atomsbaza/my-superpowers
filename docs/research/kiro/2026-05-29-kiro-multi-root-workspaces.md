# Research: Multi-Root Workspaces in Kiro

## Summary

Kiro's multi-root workspace feature, shipped in IDE release 0.6, allows a single Kiro window to contain multiple independent top-level folders simultaneously. Each root maintains its own `.kiro` configuration directory for steering files, specs, hooks, and MCP server definitions, while Kiro presents a unified view across all roots for search, indexing, and navigation. The feature is designed for teams managing interconnected but separate codebases — such as a frontend, backend, and shared library — without requiring multiple IDE windows or symlink workarounds. One explicit limitation: the experimental Repo Indexing context provider does not work with multi-folder workspaces.

---

## Key Findings

### What Multi-Root Workspaces Are

A multi-root workspace is a single Kiro workspace session that holds more than one top-level ("root") folder. For example, one workspace could simultaneously open `/users/bob/my-project` and `/shared/utils/crypto`. Each folder retains its own identity, its own `.kiro` configuration subtree, and its own git context. This is distinct from a single-root workspace, where all configuration and indexing is anchored to one directory.

### How to Set It Up

Two methods, both available from any existing single-root workspace:

1. **Menu:** File > Add Folder to Workspace... — select the folder you want to add.
2. **Drag and drop:** Drag a folder from macOS Finder or Windows File Explorer directly into Kiro's Explorer panel.

Kiro automatically recognizes each folder as a root and loads its `.kiro` configuration files. No manual workspace file editing is required to get started.

### Steering Files Across Roots

Steering files from every root's `.kiro/steering/` directory are aggregated and displayed as a unified list in the Agent Steering panel, with each file labelled by its containing root folder. Inclusion behavior differs by mode:

- **Always Included** — load for every agent interaction, regardless of which root is active. Use for workspace-wide coding standards.
- **Conditional Inclusion** — triggered by file-path patterns (e.g., `components/**/*.tsx`); activate only when the agent is working on files within the root that owns the steering file.
- **Manual Inclusion** — must be explicitly referenced with `#steering-file-name` syntax; available on-demand.
- **Global steering** — files in `~/.kiro/steering/` apply across all workspaces. Workspace-level steering takes priority over global steering when conflicts arise.

When creating a new steering file inside a multi-root workspace, Kiro asks whether the file should be root-specific, workspace-wide, or at the foundation level.

### Agent Hooks

Hooks (`File Create`, `File Save`, `File Delete`) are scoped to the root where they are defined. A hook living in `shared-ui/.kiro/hooks/` fires only when the agent modifies files inside `shared-ui/`. This prevents hooks from one project accidentally triggering in another root.

### MCP Server Configuration

All MCP server definitions found across all roots are loaded at startup. Two important behaviors:

1. **Name collision resolution:** If two roots define an MCP server with the same name, the definition in the last-listed root wins. Recommended mitigation: use descriptive prefixes — e.g., `frontend-github` and `backend-github` — to avoid collisions entirely.
2. **Working directory:** All MCP servers launch using the **first root's directory** as their working directory, regardless of which root's `.kiro` folder defined them. Any MCP config that relies on relative file paths will resolve those paths from the first root, not the defining root.

### Search, Indexing, and Navigation

The `#codebase` reference searches across all roots simultaneously. Repository maps and codebase indexing integrate code from all roots. When identical filenames exist in multiple roots (e.g., `utils/logger.ts` in both frontend and backend), Kiro displays full paths to disambiguate.

### Specifications

Spec files from each root's `.kiro` folder appear in a unified Specs list, labelled by root. Kiro automatically determines the appropriate root when you create a new spec.

### Practical Use Cases

- **Monorepo-adjacent workflows:** Working simultaneously on an app feature and the shared library it depends on.
- **Microservices development:** Keeping frontend, backend, and authentication services open together without context-switching between windows.
- **Package manager workspaces:** Projects using npm, yarn, or pnpm workspaces where packages live in sibling directories.
- **Git submodule projects:** Repositories that include submodules pointing to external code you also need to edit.
- **Cross-project refactors:** Searches and navigation that need to span project boundaries in a single operation.

---

## Trade-offs / Caveats

- **Hard limitation — Repo Indexing:** The experimental Repo Indexing context provider does not work with multi-folder workspaces. Teams relying on this feature must choose between it and multi-root setup.

- **MCP working directory trap:** All MCP servers use the first root's directory as their working directory. Any MCP config that uses relative paths will break silently if the defining root is not the first root. Audit MCP configs to use absolute paths or be deliberate about root ordering.

- **MCP name collision is last-wins, not merge:** No merging behavior for conflicting MCP definitions — one silently overwrites the other. Use prefixed server names proactively.

- **Source control behavior across roots is not documented:** How Git operations behave when roots span different repositories is unverified. Test before relying on it in critical workflows.

- **Feature availability:** Introduced in IDE release 0.6. Teams on older versions will not have this feature.

---

## Sources

- [Kiro Blog — Multi-root Workspaces](https://kiro.dev/blog/multi-root-workspaces/) — Primary blog post; use cases, setup methods, steering/hooks/MCP behavior overview
- [Kiro Docs — Multi-root Workspaces](https://kiro.dev/docs/editor/multi-root-workspaces/) — Official reference; detailed behavior for indexing, specs, steering aggregation, MCP working directory, hooks scoping
- [Kiro Changelog — IDE 0.6](https://kiro.dev/changelog/ide/0-6/) — Release notes confirming when the feature shipped and the Repo Indexing incompatibility
- [Kiro Docs — Steering](https://kiro.dev/docs/steering/) — Steering inclusion modes and global vs. workspace priority

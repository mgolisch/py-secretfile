# PRD: Discover Secretfile in Parent Directories

## Overview
The CLI currently loads `Secretfile` only from the current working directory unless `--file` is provided. In monorepos and nested project layouts, users often run commands from subdirectories and expect configuration discovery to work similarly to other developer tools.

This PRD specifies upward directory discovery for a bare filename (default `Secretfile`), with a safe stopping rule.

## Problem Statement
- Running `secretfile env` or `secretfile run -- ...` from a nested directory fails unless the user passes `--file` explicitly.
- This makes the CLI awkward in real projects where the working directory changes frequently.

## Goals
- Allow the CLI to locate `Secretfile` in parent directories automatically.
- Keep discovery deterministic (nearest match wins).
- Avoid surprising cross-project lookups by stopping at git repo root when in a checkout.

## Non-Goals
- Changing Secretfile syntax or Vault resolution behavior.
- Implementing project-root heuristics beyond git root (e.g., `pyproject.toml`, `package.json`).
- Adding interactive prompts.

## User Stories
- As a user, when I run `secretfile env` from `repo/service/a/`, it finds `repo/Secretfile` automatically.
- As a user, if there is a closer `Secretfile` in `repo/service/`, that one is used instead.
- As a user, if I pass `--file path/to/Secretfile`, the CLI uses that exact path and does not search.

## Requirements
### Functional
- If `--file` value includes a directory component (relative or absolute), the CLI MUST use it as-is and MUST NOT perform upward search.
- If `--file` is a bare filename (default `Secretfile`), the CLI MUST:
  - Start from the current working directory.
  - Search the current directory, then parent directories.
  - Select the nearest matching file (first match when walking upward).
  - Stop searching at the git repo root when inside a git worktree.
  - If not in a git worktree, stop at the filesystem root.
  - Apply a reasonable max-depth safety cap (e.g., 25).
- If discovery fails, the CLI MUST exit non-zero with a clear error message indicating the file was not found.

### Compatibility
- Existing behavior when run from the directory containing `Secretfile` MUST remain unchanged.
- Existing behavior when an explicit `--file` path is provided MUST remain unchanged.

## UX / CLI Behavior
- Nearest `Secretfile` wins (predictable in nested setups).
- Error messaging should be argparse-style (consistent with current CLI behavior).

## Acceptance Criteria
- From a nested directory, the CLI finds a parent `Secretfile` when `--file` is a bare filename.
- If two parent directories contain a `Secretfile`, the CLI picks the closer one.
- When `--file` includes a directory component, no upward search occurs.
- When inside a git worktree, discovery stops at the git root and does not search above it.
- Tests cover the above behaviors.

## Implementation Plan (No Code Yet)
- Add a helper to resolve the Secretfile path by walking upward.
- Determine git root (e.g., by invoking `git rev-parse --show-toplevel` or by locating `.git` appropriately).
- Integrate resolution into `secretfile/cli.py` before calling `load_secretfile`.
- Add tests in `tests/test_cli.py` using temp directories to simulate nested layouts and a git root boundary.

## Risks / Considerations
- Git detection must behave sensibly when git is unavailable or when run outside a worktree.
- Ensure the chosen error message does not reveal secret values (only filesystem paths).

# PRD: Support Mixed-Case Environment Variable Keys

## Overview
The Secretfile parser currently rejects environment variable keys that are not all-caps. This blocks common real-world keys such as Terraform's `TF_TOKEN_app_terraform_io`.

This PRD specifies a change to accept mixed-case keys while keeping validation aligned with portable shell identifier rules.

## Problem Statement
- Today, Secretfile lines are validated with an all-caps regex, rejecting mixed-case identifiers.
- Users cannot load secrets into environment variables whose names include lowercase letters.

## Goals
- Accept environment variable keys that are valid POSIX-style shell identifiers.
- Preserve existing safety/clarity by continuing to reject invalid names (spaces, hyphens, leading digits, etc.).
- Keep error messages clear and actionable.

## Non-Goals
- Supporting arbitrary OS environment keys (e.g., names containing `.`, `-`, spaces, or `=`).
- Changing the CLI commands, output formats, or Vault resolution behavior.
- Adding Terraform-specific documentation callouts.

## User Stories
- As a user, I can declare a mixed-case env var key in `Secretfile` and have it resolve successfully.
- As a user, I still get a clear parse error if I use an invalid env var key.

## Requirements
### Functional
- Secretfile env key validation MUST accept keys matching:
  - `^[A-Za-z_][A-Za-z0-9_]*$`
- Secretfile env key validation MUST reject keys that do not match the rule above.
- Parse errors MUST include `source:line_no` location context (as today).

### Compatibility
- Existing Secretfiles that use all-caps keys MUST continue to work unchanged.
- Existing invalid-name failures (e.g., `bad-key`) MUST remain failures.

## UX / API Behavior
- No new CLI flags.
- No changes to stdout/stderr conventions beyond the existing parser error messaging.

## Acceptance Criteria
- A Secretfile line with a mixed-case key (e.g., `TF_TOKEN_app_terraform_io <path>:<field>`) parses without error.
- A Secretfile line with `bad-key <path>:<field>` fails with `SecretfileParseError`.
- A Secretfile line with a leading digit key (e.g., `1BAD <path>:<field>`) fails with `SecretfileParseError`.
- Test suite includes coverage for the new allowed pattern and the key rejection cases.

## Implementation Plan (No Code Yet)
- Update `_ENV_KEY_RE` in `secretfile/parser.py` to the shell-identifier regex.
- Add tests in `tests/test_parser.py` for:
  - mixed-case key accepted
  - hyphenated key rejected
  - leading-digit key rejected

## Risks / Considerations
- Some platforms/shells may allow broader env key sets; this project intentionally limits keys to portable shell identifiers.
- Ensure parse errors do not leak secret values (only key names and file locations).

## Status
- Implemented (2026-05-13)

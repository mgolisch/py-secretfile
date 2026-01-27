# AGENTS.md
# Guidance for coding agents working in this repository.

Project summary
- Package name: py-secretfile
- Description: python library for Secretfile
- Python: >=3.12
- Build backend: poetry-core (PEP 517)
- Dependencies: hvac

Repository layout
- Root only; no src/ or tests/ directories detected
- No .cursor/rules, .cursorrules, or Copilot instructions found

Commands
Note: No lint/test tooling is configured in this repo.
Use the commands below only if the required tools are installed.

Build
- `python -m build` (requires `build` package)
- `poetry build` (requires `poetry`)

Install for development
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -U pip`
- `pip install -e .`

Lint
- None configured. If you add tooling, document it here.
- Common choices: `ruff`, `flake8`, `black`, `mypy`.

Test
- `pytest` (install with `pip install -e .[dev]` or `pip install pytest`)

Run a single test (if pytest is added)
- `pytest -k "pattern"`
- `pytest path/to/test_file.py::TestClass::test_name`
- `pytest path/to/test_file.py -k "pattern"`

Formatting
- None configured. If you add formatting, document here.
- Common choices: `black` or `ruff format`.

Code style guidelines
Default to existing patterns once code is added.
If creating new files, use these conventions unless the repo evolves.

Imports
- Use absolute imports from the package namespace.
- Standard library imports first, then third-party, then local.
- One import per line for clarity in public modules.
- Avoid wildcard imports.

Formatting
- Keep lines readable; prefer <= 88 characters if using Black.
- Use trailing commas in multi-line literals.
- Prefer explicit parentheses over backslashes.

Types
- Use type hints for public APIs and complex internals.
- Favor builtin generics: `list[str]`, `dict[str, str]`.
- Use `typing.Protocol` for structural interfaces.
- Keep return types explicit when the function is non-trivial.

Naming conventions
- Modules and packages: `snake_case`.
- Classes: `PascalCase`.
- Functions and methods: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Private helpers: leading underscore.

Docstrings
- Use short, clear docstrings for public functions and classes.
- Prefer imperative style: "Return secret value".
- Keep examples concise and correct.

Error handling
- Raise specific exceptions; avoid bare `Exception`.
- Preserve context using `raise ... from err`.
- Validate inputs early; fail fast with clear messages.
- Do not swallow exceptions silently.

Logging
- If logging is added, use module-level loggers.
- Avoid logging secrets or sensitive data.

Security
- Treat secret values as sensitive; avoid printing them.
- Do not write secrets to disk by default.
- Ensure exceptions do not include secret values.

API design
- Keep public API surface small and documented.
- Use simple, explicit parameters over ambiguous dicts.
- Keep side effects obvious in function names.

Dependencies
- Keep dependencies minimal.
- If adding a dependency, update `pyproject.toml`.
- Prefer well-maintained libraries.

Packaging
- Update `pyproject.toml` when adding packages/modules.
- Keep versioning consistent with semver conventions.
- Update README when public usage changes.

Tests (when added)
- Use pytest.
- Mirror package structure under `tests/`.
- Keep tests deterministic and isolated.
- Use fixtures for shared setup.

Examples (when added)
- Prefer minimal, runnable examples.
- Avoid embedding real secrets in examples.

Release checklist (if you add releases)
- Bump version in `pyproject.toml`.
- Update changelog/README as needed.
- Build with `python -m build` or `poetry build`.
- Verify artifacts before publishing.

Agent behavior
- If you add lint/test tooling, update this file.
- Follow existing conventions once code is present.
- Keep changes small and focused.

Notes on missing rules
- No Cursor rules detected in `.cursor/rules/` or `.cursorrules`.
- No Copilot rules detected in `.github/copilot-instructions.md`.

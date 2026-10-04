# Project Dependencies Inventory

This document tracks all libraries and packages used by GitPR-Analyzer, the rationale for inclusion, and the evaluated alternatives.

Per project guidelines, no third-party library is installed without explicit prior authorization.

---

## 1. Built-in Dependencies (Python Standard Library)

No external installation required. These ship with Python 3.10+.

| Module | Purpose in Pipeline | Why Standard Library? |
| :--- | :--- | :--- |
| `ast` | Parses Python files into syntax trees; traverses `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Call`. | Zero external dependencies; compiler-accurate parsing for Python code; no compilation steps required. |
| `dataclasses` | Strongly-typed data containers (`FileDiff`, `Hunk`, `ChangedSymbol`, `CallSite`). | Clean object representations with zero runtime dependency overhead. |
| `re` | Regex extraction of unified diff hunk coordinates (`@@ -l,s +l,s @@`). | High performance string pattern matching. |
| `pathlib` | Cross-platform filesystem path manipulation (Windows/Linux/macOS). | Standard object-oriented path handling. |
| `typing` | Static type annotations (`List`, `Dict`, `Set`, `Optional`, `Tuple`). | Improves code clarity, safety, and IDE autocompletion. |
| `unittest` | Unit testing of core parsers and AST visitors. | Built-in test runner; no setup required to verify logic. |

---

## 2. Third-Party Dependencies (Planned / Pending Approval)

The following libraries are planned for later stages and will require explicit approval before installation:

| Package | Intended Stage | Rationale | Built-in / Lighter Alternative |
| :--- | :--- | :--- | :--- |
| `pydantic` | Stage 5 (LLM Evaluation) | Enforces strict JSON schema validation on LLM output (contract breaking risks, line numbers, severities). | Built-in `json` module + custom validation functions (more error-prone, less rigid schema generation). |
| `google-genai` / `openai` | Stage 5 (LLM Evaluation) | Client SDK for neural evaluation. | Raw `urllib.request` / `requests` calling REST API directly (requires manual payload and retry handling). |
| `rich` | Stage 6 (CLI & Reporting) | Terminal formatting: color-coded severity badges, syntax-highlighted diffs, clean tables. | Built-in ANSI escape sequences (`\033[31m` etc.) or plain text formatting. |

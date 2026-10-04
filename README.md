# GitPR-Analyzer (DiffRadius)

> **Context-Aware Impact Analysis & Blast-Radius Detection in Git Pull Requests**  
> *Combining Abstract Syntax Tree (AST) analysis and Large Language Models to detect silent cross-file breaking changes.*

---

## The Problem

Standard automated code review bots and raw LLM queries evaluate Git Pull Requests (PRs) in isolation: they only inspect the lines touched by the unified diff. 

Because of this isolated view, they fail to detect **cross-file breaking changes**—scenarios where modifying a function signature, changing return types, or introducing new default assumptions in one file silently breaks unedited caller files elsewhere across the repository.

Conversely, passing an entire repository into an LLM context window is computationally expensive, introduces high latency, and suffers from **"lost in the middle"** retrieval degradation.

## The Solution

GitPR-Analyzer implements a **hybrid static-semantic pipeline**:

1. **Deterministic Static Analysis (AST):**
   - Parses unified git diffs into exact hunk boundaries and modified line numbers.
   - Maps modified lines to syntax nodes (`FunctionDef`, `AsyncFunctionDef`, `ClassDef`) using compiler AST traversal.
   - Scans the repository to build a call graph and locate every downstream caller in unedited files.
2. **Targeted Neural Evaluation (LLM):**
   - Assembles a compact context payload containing only the modified functions and the specific downstream call-sites.
   - Evaluates the contract boundary using structured JSON schemas to flag breaking changes, type mismatches, and behavioral regressions.

---

## Architecture Overview

```
[ Git Diff / Patch ]
         │
         ▼
[ Stage 1: Diff Parser (src/diff_parser.py) ]
         │ Extracts modified files & changed line numbers
         ▼
[ Stage 2: AST Function Mapper (src/ast_mapper.py) ]
         │ Maps changed lines to AST function/class nodes
         ▼
[ Stage 3: Static Call-Graph Resolver (src/call_graph.py) ]
         │ Finds all downstream callers across the workspace
         ▼
[ Stage 4: Context Packager (src/context_packager.py) ]
         │ Combines changed functions + remote caller snippets
         ▼
[ Stage 5: Structured Neural Evaluator (src/llm_evaluator.py) ]
         │ Evaluates breaking contract risks with Pydantic schemas
         ▼
[ Stage 6: CLI & Reporter (src/reporter.py) ]
         │ Generates blast-radius reports and remediation steps
```

---

## Project Structure

```text
GitPR-Analyzer/
├── docs/
│   ├── ARCHITECTURE.md       # Full architecture specification and data flow
│   ├── DEPENDENCIES.md       # Dependency inventory and alternatives analysis
│   └── SPRINT_LOG.md         # Sprint notes, algorithms, and complexity analysis
├── src/
│   ├── __init__.py
│   └── diff_parser.py        # Zero-dependency unified git diff parser
├── tests/
│   └── test_diff_parser.py   # Unit tests for diff parsing logic
├── .editorconfig             # Whitespace and formatting rules across platforms
├── .gitignore                # Production ignore patterns for Python projects
├── LICENSE                   # MIT License
├── pyproject.toml            # PEP 518/621 packaging and project metadata
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Git

### Running Tests

The core parsing engine uses only Python standard library modules with zero external package installations:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## Documentation

- [Architecture Specification](docs/ARCHITECTURE.md)
- [Dependency Inventory](docs/DEPENDENCIES.md)
- [Sprint & Implementation Log](docs/SPRINT_LOG.md)

---

## License

MIT License. See [LICENSE](LICENSE) for details.

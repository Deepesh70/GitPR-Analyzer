# Architecture Specification: Context-Aware Impact Analysis in Git Pull Requests

**Project Name:** DiffRadius / GitPR-Analyzer  
**Domain:** Code Intelligence, Static Program Analysis, Applied NLP/LLM Evaluation  

---

## 1. Executive Summary

Standard automated code review platforms and raw Large Language Model (LLM) prompts review Git Pull Requests (PRs) in isolation, examining solely the lines included within a unified diff. Consequently, they fail to detect cross-file breaking changes—scenarios where modifying a function signature, changing return semantics, or introducing unexpected side effects in one file silently breaks dependent call-sites across unedited files in the repository.

Conversely, dumping an entire codebase into an LLM context window causes high token costs, high inference latency, and retrieval degradation ("lost in the middle").

This project implements a hybrid static-analysis and neural evaluation pipeline:
1. **Deterministic Layer (Static Analysis):** Analyzes unified git diffs, maps changed line numbers to Abstract Syntax Tree (AST) nodes, and statically traces downstream references across the workspace to compute the change's structural blast radius.
2. **Neural Layer (Targeted LLM Evaluation):** Assembles a high-density, minimal context payload containing only the modified code blocks paired with their exact remote caller snippets. Queries an LLM using strict JSON schema validation to detect contract breaking changes, type mismatches, and behavioral regressions.

---

## 2. Pipeline Architecture & Data Flow

```
[ Raw Git Diff / Patch ]
          │
          ▼
[ Stage 1: Diff Parser (src/diff_parser.py) ]
          │ Extracts modified files and changed line numbers from hunks (@@ -a,b +c,d @@)
          ▼
[ Stage 2: AST Function Mapper (src/ast_mapper.py) ]
          │ Parses modified source files with Python AST.
          │ Maps modified lines to exact AST nodes (FunctionDef, AsyncFunctionDef, ClassDef).
          │ Extracts symbol names, parameter signatures, and docstrings.
          ▼
[ Stage 3: Call-Graph & Reference Resolver (src/call_graph.py) ]
          │ Scans repository Python files.
          │ Builds an inverted caller index (ast.Call nodes referencing modified symbols).
          │ Extracts exact caller functions/blocks from unedited files.
          ▼
[ Stage 4: Context Packager (src/context_packager.py) ]
          │ Bundles changed function (before/after) + downstream caller snippets.
          │ Eliminates irrelevant repository tokens (90%+ prompt token savings).
          ▼
[ Stage 5: Structured Neural Evaluator (src/llm_evaluator.py) ]
          │ Enforces Pydantic schema validation.
          │ Prompts LLM to evaluate breaking contract risks.
          ▼
[ Stage 6: CLI & Reporter (src/reporter.py) ]
          │ Formats diagnostic tables, risk severity badges, and remediation advice.
```

---

## 3. Core Design Principles

1. **Deterministic Where Possible, Neural Where Necessary:**
   Do not use an LLM to guess which files call a function. Use compiler AST parsing to locate callers with 100% determinism. Use the LLM solely to reason over semantic and contract compatibility between caller and callee.
2. **Zero Syntax Truncation:**
   Standard text-splitting RAG cuts code by arbitrary character lengths, breaking loops, decorators, and function signatures. AST-based chunking preserves complete semantic syntax blocks.
3. **Token Minimization:**
   Instead of uploading dozens of full files, transmit only the altered function signature and the specific 5-15 lines of code at downstream call-sites.
4. **Standard Library First:**
   Core parsing and AST traversal use Python's built-in `ast`, `re`, and `dataclasses` modules to keep installation lightweight and eliminate dependency drift.

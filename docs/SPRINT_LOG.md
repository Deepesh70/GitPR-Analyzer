# Sprint & Implementation Log

This document records the incremental progress of GitPR-Analyzer, detailing what was built, how the implementation works, key algorithms, complexity analysis, and technical explanations for interview preparation.

---

## Sprint 1: Stage 1 - Unified Diff Parser & AST Change Extraction

### Step 1.1: Unified Diff Parser (`src/diff_parser.py`)

- **Objective:** Ingest raw unified git diff text and parse it into structured data classes containing modified file paths and precise changed line numbers in the target version.
- **Dependencies Used:** Python standard library (`dataclasses`, `re`, `typing`). Zero external packages.
- **Status:** Completed and verified with unit tests (`tests/test_diff_parser.py`).

#### How It Works (Code Walkthrough)
1. **File Header Detection:** The parser scans line-by-line for `--- a/path` (old version) and `+++ b/path` (new version), stripping git prefixes and identifying if a file was created (`/dev/null` on old) or deleted (`/dev/null` on new).
2. **Hunk Header Parsing:** Regex matches `@@ -old_start,old_len +new_start,new_len @@`. We extract start coordinates and length ranges for both sides of the diff.
3. **Line Tracking:** Within each hunk:
   - Lines prefixed with `+` are recorded into `added_lines` using the new file line counter, which then increments.
   - Lines prefixed with `-` are recorded into `deleted_lines` using the old file line counter, which then increments.
   - Context lines starting with a space increment both counters simultaneously.
4. **Output Interface:** Returns a list of `FileDiff` objects with a helper property `all_modified_new_lines` producing a `Set[int]`. This set gives the AST mapper the exact line coordinates to query.

#### Complexity & Trade-offs
- **Time Complexity:** $O(N)$ where $N$ is the number of lines in the diff. Each line is checked sequentially with regex and string prefix checks.
- **Space Complexity:** $O(L)$ where $L$ is the number of changed lines stored in memory.
- **Trade-off:** We wrote a custom pure-Python parser instead of pulling in `unidiff` or `gitpython`. This keeps the package self-contained, eliminates version drift, and directly exposes the hunk line tracking mechanism for clear explanation.


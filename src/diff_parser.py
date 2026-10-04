"""
Diff Parser Module for GitPR-Analyzer.

Parses unified git diff output into structured file and line modification models.
Uses strictly the Python standard library (re, dataclasses).
"""

import re
from dataclasses import dataclass, field
from typing import List, Set, Optional


@dataclass
class HunkChange:
    """Represents modified line numbers within a single diff hunk."""
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    # Line numbers in the new file that were added or modified
    added_lines: List[int] = field(default_factory=list)
    # Line numbers in the old file that were deleted or modified
    deleted_lines: List[int] = field(default_factory=list)


@dataclass
class FileDiff:
    """Represents all changes associated with a single modified file."""
    old_path: Optional[str]
    new_path: Optional[str]
    is_new_file: bool = False
    is_deleted_file: bool = False
    hunks: List[HunkChange] = field(default_factory=list)

    @property
    def target_path(self) -> Optional[str]:
        """Returns the active file path for downstream AST parsing."""
        return self.new_path if not self.is_deleted_file else self.old_path

    @property
    def all_modified_new_lines(self) -> Set[int]:
        """
        Returns a flat set of all line numbers modified in the new version of the file.
        Used by the AST mapper to locate enclosing functions and classes.
        """
        lines: Set[int] = set()
        for hunk in self.hunks:
            lines.update(hunk.added_lines)
        return lines


class DiffParser:
    """
    Parses unified diff text into a structured collection of FileDiff objects.
    
    Handles standard unified diff hunk syntax:
        @@ -old_start,old_len +new_start,new_len @@
    """

    HUNK_HEADER_PATTERN = re.compile(
        r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@"
    )

    def parse(self, diff_text: str) -> List[FileDiff]:
        """
        Parses raw unified diff string into a list of FileDiff instances.
        
        Args:
            diff_text: Raw diff content (e.g. from `git diff` or patch file).
            
        Returns:
            List of FileDiff structures.
        """
        files: List[FileDiff] = []
        current_file: Optional[FileDiff] = None
        current_hunk: Optional[HunkChange] = None

        # Tracks current line cursors within the active hunk
        current_old_line = 0
        current_new_line = 0

        lines = diff_text.splitlines()

        for line in lines:
            # Detect file header: old file
            if line.startswith("--- "):
                raw_path = line[4:].strip()
                old_path = None if raw_path == "/dev/null" else self._normalize_path(raw_path)
                current_file = FileDiff(old_path=old_path, new_path=None)
                files.append(current_file)
                current_hunk = None
                continue

            # Detect file header: new file
            if line.startswith("+++ "):
                if current_file is None:
                    # In case of patch anomalies where +++ appears without ---
                    current_file = FileDiff(old_path=None, new_path=None)
                    files.append(current_file)

                raw_path = line[4:].strip()
                if raw_path == "/dev/null":
                    current_file.new_path = None
                    current_file.is_deleted_file = True
                else:
                    current_file.new_path = self._normalize_path(raw_path)
                    if current_file.old_path is None:
                        current_file.is_new_file = True

                current_hunk = None
                continue

            # Detect hunk header: @@ -a,b +c,d @@
            hunk_match = self.HUNK_HEADER_PATTERN.match(line)
            if hunk_match and current_file is not None:
                old_start = int(hunk_match.group(1))
                old_len = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                new_start = int(hunk_match.group(3))
                new_len = int(hunk_match.group(4)) if hunk_match.group(4) else 1

                current_hunk = HunkChange(
                    old_start=old_start,
                    old_length=old_len,
                    new_start=new_start,
                    new_length=new_len,
                )
                current_file.hunks.append(current_hunk)

                # Initialize cursor line numbers
                current_old_line = old_start
                current_new_line = new_start
                continue

            # Process line changes inside an active hunk
            if current_hunk is not None:
                if line.startswith("+") and not line.startswith("+++"):
                    current_hunk.added_lines.append(current_new_line)
                    current_new_line += 1
                elif line.startswith("-") and not line.startswith("---"):
                    current_hunk.deleted_lines.append(current_old_line)
                    current_old_line += 1
                elif line.startswith(" "):
                    # Context line: present in both versions
                    current_old_line += 1
                    current_new_line += 1
                elif line.startswith(r"\ No newline at end of file"):
                    # Git diff metadata marker
                    pass

        return files

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Strips standard git prefixes (a/, b/) and quotes if present."""
        cleaned = path.strip("\"'")
        if cleaned.startswith("a/") or cleaned.startswith("b/"):
            return cleaned[2:]
        return cleaned

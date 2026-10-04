"""Unit tests for Unified Diff Parser."""

import unittest
from src.diff_parser import DiffParser


class TestDiffParser(unittest.TestCase):

    def setUp(self):
        self.parser = DiffParser()

    def test_single_file_modification(self):
        sample_diff = """--- a/billing/calculator.py
+++ b/billing/calculator.py
@@ -10,4 +10,5 @@
 def calculate_tax(amount, rate):
-    return amount * rate
+    discount = 0.05
+    return (amount - discount) * rate
"""
        files = self.parser.parse(sample_diff)
        self.assertEqual(len(files), 1)

        f = files[0]
        self.assertEqual(f.old_path, "billing/calculator.py")
        self.assertEqual(f.new_path, "billing/calculator.py")
        self.assertEqual(f.target_path, "billing/calculator.py")
        self.assertFalse(f.is_new_file)
        self.assertFalse(f.is_deleted_file)

        self.assertEqual(len(f.hunks), 1)
        hunk = f.hunks[0]
        self.assertEqual(hunk.old_start, 10)
        self.assertEqual(hunk.new_start, 10)
        self.assertEqual(hunk.deleted_lines, [11])
        self.assertEqual(hunk.added_lines, [11, 12])
        self.assertEqual(f.all_modified_new_lines, {11, 12})

    def test_multiple_hunks_and_files(self):
        sample_diff = """--- a/math_ops.py
+++ b/math_ops.py
@@ -1,3 +1,4 @@
 def add(a, b):
+    # logging
     return a + b
@@ -20,2 +21,3 @@
 def multiply(a, b):
+    validate(a, b)
     return a * b
--- a/config.py
+++ b/config.py
@@ -5,1 +5,1 @@
-DEBUG = False
+DEBUG = True
"""
        files = self.parser.parse(sample_diff)
        self.assertEqual(len(files), 2)

        # File 1
        f1 = files[0]
        self.assertEqual(f1.target_path, "math_ops.py")
        self.assertEqual(len(f1.hunks), 2)
        self.assertEqual(f1.all_modified_new_lines, {2, 22})

        # File 2
        f2 = files[1]
        self.assertEqual(f2.target_path, "config.py")
        self.assertEqual(len(f2.hunks), 1)
        self.assertEqual(f2.hunks[0].deleted_lines, [5])
        self.assertEqual(f2.hunks[0].added_lines, [5])

    def test_newly_created_file(self):
        sample_diff = """--- /dev/null
+++ b/new_module.py
@@ -0,0 +1,3 @@
+def greet(name):
+    return f"Hello, {name}"
+
"""
        files = self.parser.parse(sample_diff)
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertTrue(f.is_new_file)
        self.assertIsNone(f.old_path)
        self.assertEqual(f.new_path, "new_module.py")
        self.assertEqual(f.all_modified_new_lines, {1, 2, 3})

    def test_deleted_file(self):
        sample_diff = """--- a/deprecated.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def old():
-    pass
"""
        files = self.parser.parse(sample_diff)
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertTrue(f.is_deleted_file)
        self.assertEqual(f.old_path, "deprecated.py")
        self.assertIsNone(f.new_path)
        self.assertEqual(f.target_path, "deprecated.py")
        self.assertEqual(f.hunks[0].deleted_lines, [1, 2])


if __name__ == "__main__":
    unittest.main()

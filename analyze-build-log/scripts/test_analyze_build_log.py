#!/usr/bin/env python3
"""Unit tests for analyze_build_log.py."""

import io
import os
import tempfile
import unittest
from unittest.mock import patch

from analyze_build_log import BuildLogAnalyzer, main


class TestBuildLogAnalyzer(unittest.TestCase):
    """Test cases for BuildLogAnalyzer."""

    def test_group_identical_errors(self):
        lines = [
            "Error: Identical error",
            "e: /path/One.kt: (1,1): Identical error",
            "Some log line",
            "Error: Identical error",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, failure_msg = analyzer.generate_report(emit_annotations=False)

        self.assertTrue(is_failed)
        self.assertIn("Found 3 errors in the build log.", failure_msg)
        self.assertIn("| ❌ Error | 1, 4 | `Error: Identical error` |", report)
        self.assertIn("| ❌ Error | 2 | `e: /path/One.kt: (1,1): Identical error` |", report)

    def test_detect_kotlin_warnings(self):
        lines = ["w: /path/Warning.kt: (1,1): Warning message"]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertFalse(is_failed)
        self.assertIn("| ⚠️ Warning | 1 | `w: /path/Warning.kt: (1,1): Warning message` |", report)

    def test_distinct_errors(self):
        lines = [
            "Error: A",
            "Error: B",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertTrue(is_failed)
        self.assertIn("| ❌ Error | 1 | `Error: A` |", report)
        self.assertIn("| ❌ Error | 2 | `Error: B` |", report)

    def test_ignore_gradle_welcome_message(self):
        lines = [
            "Welcome to Gradle 9.3.1!",
            "",
            "Here are the highlights of this release:",
            " - Test reporting improvements",
            " - Error and warning improvements",
            " - Build authoring improvements",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertFalse(is_failed)
        self.assertIn("✨ No errors or warnings found.", report)

    def test_classify_kover_deprecation_warning(self):
        lines = [
            "Using a Project object as a dependency notation has been deprecated. This will fail with an error in Gradle 10. Please use the project(String)...",
            "\tat org.gradle.api.internal.notations.DependencyProjectNotationConverter.convert(DependencyProjectNotationConverter.java:48)",
            "\tat kotlinx.kover.gradle.plugin.appliers.PrepareKoverKt.prepare(PrepareKover.kt:29)",
            "\tat kotlinx.kover.gradle.plugin.KoverGradlePlugin.apply(KoverGradlePlugin.kt:29)",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertFalse(is_failed)
        self.assertIn("#### Known Warnings / Ignorable Warnings", report)
        self.assertIn("`kotlinx-kover` プラグイン", report)
        self.assertIn("Found **0** errors and **0** warnings.", report)

    def test_classify_agp_deprecation_warning(self):
        lines = [
            "Using a Project object as a dependency notation has been deprecated. This will fail with an error in Gradle 10. Please use the project(String)...",
            "\tat org.gradle.api.internal.notations.DependencyProjectNotationConverter.convert(DependencyProjectNotationConverter.java:48)",
            "\tat com.android.build.gradle.internal.dependency.VariantDependenciesBuilder.build(VariantDependenciesBuilder.java:279)",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertFalse(is_failed)
        self.assertIn("#### Known Warnings / Ignorable Warnings", report)
        self.assertIn("`Android Gradle Plugin`", report)

    def test_classify_unknown_deprecation_warning(self):
        lines = [
            "Using a Project object as a dependency notation has been deprecated. This will fail with an error in Gradle 10. Please use the project(String)...",
            "Some normal build log line",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertFalse(is_failed)
        self.assertIn("#### Known Warnings / Ignorable Warnings", report)
        self.assertIn("`kotlinx-kover` または `Android Gradle Plugin` などの外部プラグイン", report)

    def test_parse_build_time_and_tasks(self):
        lines = [
            ":t1 UP-TO-DATE",
            "> Task :t2 SKIPPED",
            "> Task :t3",
            ":t4 FROM-CACHE",
            "BUILD SUCCESSFUL in 1m 23s",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)

        self.assertFalse(is_failed)
        self.assertIn("### Android Build Log Analysis", report)
        self.assertIn("#### Build Performance Summary", report)
        self.assertIn("#### Error and Warning Analysis", report)
        self.assertIn("- **Total Build Time**: 1m 23s", report)
        self.assertIn("- **Total Tasks**: 4", report)
        self.assertIn("  - Executed: 1", report)
        self.assertIn("  - CACHED / UP-TO-DATE: 2", report)
        self.assertIn("  - SKIPPED: 1", report)

    def test_many_error_lines_abbreviation(self):
        # Map with same message
        lines_same = ["Error: Identical error"] * 10
        analyzer = BuildLogAnalyzer("\n".join(lines_same))
        report, is_failed, _ = analyzer.generate_report(emit_annotations=False)
        self.assertTrue(is_failed)
        self.assertIn("... and 7 others", report)

    def test_emit_annotations_captured(self):
        lines = [
            "e: /path/Main.kt: (1,1): Compilation error",
            "w: /path/Warning.kt: (2,2): Deprecation warning",
        ]
        analyzer = BuildLogAnalyzer("\n".join(lines))
        fake_stdout = io.StringIO()
        with patch("sys.stdout", fake_stdout):
            report, is_failed, _ = analyzer.generate_report(emit_annotations=True)

        self.assertTrue(is_failed)
        output = fake_stdout.getvalue()
        self.assertIn("::error title=Line 1::e: /path/Main.kt: (1,1): Compilation error", output)
        self.assertIn(
            "::warning title=Line 2::w: /path/Warning.kt: (2,2): Deprecation warning", output
        )


class TestCLIExecution(unittest.TestCase):
    """Test CLI commands and argument handling."""

    def setUp(self):
        # Isolate all tests from real GitHub Actions environment variables
        self.env_patcher = patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "", "GITHUB_OUTPUT": ""})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_cli_success_with_report_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "build.log")
            report_file = os.path.join(tmpdir, "report.md")
            summary_file = os.path.join(tmpdir, "summary.md")
            output_file = os.path.join(tmpdir, "github_output.txt")

            with open(log_file, "w", encoding="utf-8") as f:
                f.write("> Task :app:assembleDebug UP-TO-DATE\nBUILD SUCCESSFUL in 5s\n")

            with (
                patch.dict(
                    os.environ, {"GITHUB_STEP_SUMMARY": summary_file, "GITHUB_OUTPUT": output_file}
                ),
                patch("sys.stdout"),
                patch("sys.stderr"),
                patch(
                    "sys.argv",
                    [
                        "analyze_build_log.py",
                        "--log-file-path",
                        log_file,
                        "--report-path",
                        report_file,
                    ],
                ),
            ):
                main()

            self.assertTrue(os.path.exists(report_file))
            with open(report_file, encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Build Performance Summary", content)

            self.assertTrue(os.path.exists(summary_file))
            with open(summary_file, encoding="utf-8") as f:
                self.assertIn("Build Performance Summary", f.read())

            self.assertTrue(os.path.exists(output_file))
            with open(output_file, encoding="utf-8") as f:
                output_content = f.read()
                self.assertIn(f"report-path={report_file}", output_content)
                self.assertIn("error-count=0", output_content)
                self.assertIn("warning-count=0", output_content)

    def test_cli_error_file_not_found(self):
        with (
            patch("sys.stdout"),
            patch("sys.stderr"),
            patch("sys.argv", ["analyze_build_log.py", "--log-file-path", "non_existent_file.log"]),
        ):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

    def test_cli_error_on_detected_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "build.log")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("e: /path/Main.kt: (1,1): Compilation error\nBUILD FAILED in 3s\n")

            with (
                patch("sys.stdout"),
                patch("sys.stderr"),
                patch("sys.argv", ["analyze_build_log.py", "--log-file-path", log_file]),
            ):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)

    def test_cli_disable_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "build.log")
            summary_file = os.path.join(tmpdir, "summary.md")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("> Task :app:assembleDebug UP-TO-DATE\nBUILD SUCCESSFUL in 5s\n")

            with (
                patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": summary_file}),
                patch("sys.stdout"),
                patch("sys.stderr"),
                patch(
                    "sys.argv",
                    [
                        "analyze_build_log.py",
                        "--log-file-path",
                        log_file,
                        "--disable-summary",
                    ],
                ),
            ):
                main()

            # summary_file should not have been created or written to
            self.assertFalse(os.path.exists(summary_file))

    def test_cli_disable_annotations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "build.log")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("e: /path/Main.kt: (1,1): Compilation error\nBUILD FAILED in 3s\n")

            fake_stdout = io.StringIO()
            with (
                patch("sys.stdout", fake_stdout),
                patch("sys.stderr"),
                patch(
                    "sys.argv",
                    [
                        "analyze_build_log.py",
                        "--log-file-path",
                        log_file,
                        "--disable-annotations",
                    ],
                ),
            ):
                with self.assertRaises(SystemExit):
                    main()

            output = fake_stdout.getvalue()
            self.assertNotIn("::error", output)


if __name__ == "__main__":
    unittest.main()

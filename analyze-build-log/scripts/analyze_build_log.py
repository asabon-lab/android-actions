#!/usr/bin/env python3
"""Android Build Log Analyzer.

Analyzes Android build logs for errors, warnings, and build performance,
outputs GitHub Actions annotations, and generates a Markdown report
for GitHub Step Summary or file output.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class BuildLogAnalyzer:
    """Parses and analyzes Android build logs."""

    TASK_REGEX = re.compile(r"(?:> Task )?(:[^\s]+)\s*([A-Z-]+)?")
    BUILD_RESULT_REGEX = re.compile(r"BUILD (SUCCESSFUL|FAILED) in (.*)")
    ERROR_REGEX = re.compile(r"^(\s*(Error|error):|^e:)")
    WARNING_REGEX = re.compile(r"^(\s*(Warning|warning):|^w:)")
    DEPRECATION_KEYWORD = (
        "Using a Project object as a dependency notation has been deprecated"
    )

    def __init__(self, log_content: str):
        self.lines = log_content.splitlines()
        self.error_count = 0
        self.warning_count = 0

    def analyze_performance(self) -> str:
        """Extracts task execution and build duration stats."""
        tasks: List[Tuple[str, str]] = []
        total_time = "Unknown"

        for line in self.lines:
            task_match = self.TASK_REGEX.match(line)
            if task_match:
                name = task_match.group(1)
                outcome = task_match.group(2) or "EXECUTED"
                tasks.append((name, outcome))

            result_match = self.BUILD_RESULT_REGEX.search(line)
            if result_match:
                total_time = result_match.group(2).strip()

        executed = sum(1 for _, outcome in tasks if outcome == "EXECUTED")
        up_to_date = sum(1 for _, outcome in tasks if outcome == "UP-TO-DATE")
        skipped = sum(1 for _, outcome in tasks if outcome == "SKIPPED")
        from_cache = sum(1 for _, outcome in tasks if outcome == "FROM-CACHE")
        cached_or_up_to_date = from_cache + up_to_date

        markdown = "### Build Performance Summary\n\n"
        markdown += f"- **Total Build Time**: {total_time}\n"
        markdown += f"- **Total Tasks**: {len(tasks)}\n"
        markdown += f"  - Executed: {executed}\n"
        markdown += f"  - CACHED / UP-TO-DATE: {cached_or_up_to_date}\n"
        markdown += f"  - SKIPPED: {skipped}\n\n"
        return markdown

    def analyze_errors_and_warnings(
        self, emit_annotations: bool = True
    ) -> Tuple[str, int, int]:
        """Detects errors, warnings, and known deprecation warnings.

        Returns (markdown_report, error_count, warning_count).
        """
        issues_map: Dict[str, Dict] = {}
        known_warnings: List[Dict] = []
        error_count = 0
        warning_count = 0

        for index, line in enumerate(self.lines):
            line_num = index + 1

            # Check for Gradle deprecation warning: Project object dependency notation
            if self.DEPRECATION_KEYWORD in line:
                cause = "unknown"
                max_scan = min(len(self.lines), index + 31)
                for j in range(index + 1, max_scan):
                    next_line = self.lines[j].strip()
                    if next_line.startswith("at ") or next_line.startswith("..."):
                        if "kotlinx.kover" in next_line:
                            cause = "kotlinx-kover"
                            break
                        elif "com.android.build.gradle" in next_line:
                            cause = "com.android.build.gradle"
                            break
                    elif (
                        not next_line
                        or next_line.startswith("> Task :")
                        or (len(next_line) > 0 and next_line[0].isupper() and " " in next_line)
                    ):
                        break

                existing = next((w for w in known_warnings if w["cause"] == cause), None)
                if existing:
                    existing["lines"].append(line_num)
                else:
                    known_warnings.append({
                        "message": line.strip(),
                        "lines": [line_num],
                        "cause": cause,
                    })
                continue

            # Check standard error and warning patterns
            issue_type: Optional[str] = None
            if self.ERROR_REGEX.search(line):
                issue_type = "Error"
            elif self.WARNING_REGEX.search(line):
                issue_type = "Warning"

            if issue_type:
                message = line.strip()
                if message in issues_map:
                    issues_map[message]["lines"].append(line_num)
                else:
                    issues_map[message] = {
                        "type": issue_type,
                        "message": message,
                        "lines": [line_num],
                    }

                if issue_type == "Error":
                    error_count += 1
                    if emit_annotations:
                        print(f"::error title=Line {line_num}::{message}")
                else:
                    warning_count += 1
                    if emit_annotations:
                        print(f"::warning title=Line {line_num}::{message}")

        # Build Markdown section
        markdown = "### Error and Warning Analysis\n\n"
        markdown += f"Found **{error_count}** errors and **{warning_count}** warnings.\n\n"

        if issues_map:
            markdown += "| Type | Lines | Message |\n"
            markdown += "| :--- | :--- | :--- |\n"

            # Sort errors first, then warnings
            sorted_issues = sorted(
                issues_map.values(),
                key=lambda x: (0 if x["type"] == "Error" else 1, x["lines"][0]),
            )

            for issue in sorted_issues:
                icon = "❌" if issue["type"] == "Error" else "⚠️"
                safe_message = issue["message"].replace("|", "\\|")
                lines_list = issue["lines"]
                if len(lines_list) > 5:
                    line_str = (
                        f"{', '.join(map(str, lines_list[:3]))} ... and {len(lines_list) - 3} others"
                    )
                else:
                    line_str = ", ".join(map(str, lines_list))

                markdown += f"| {icon} {issue['type']} | {line_str} | `{safe_message}` |\n"
        else:
            markdown += "✨ No errors or warnings found.\n"

        if known_warnings:
            markdown += "\n### Known Warnings / Ignorable Warnings\n\n"
            for kw in known_warnings:
                cause = kw["cause"]
                if cause == "kotlinx-kover":
                    cause_desc = "`kotlinx-kover` プラグイン"
                elif cause == "com.android.build.gradle":
                    cause_desc = "`Android Gradle Plugin`"
                else:
                    cause_desc = "`kotlinx-kover` または `Android Gradle Plugin` などの外部プラグイン"

                lines_list = kw["lines"]
                if len(lines_list) > 5:
                    line_str = (
                        f"{', '.join(map(str, lines_list[:3]))} ... and {len(lines_list) - 3} others"
                    )
                else:
                    line_str = ", ".join(map(str, lines_list))

                markdown += (
                    f"> ⚠️ **Gradle Deprecation Warning (Project dependency notation)** (Lines: {line_str})\n>\n"
                    f"> この警告は {cause_desc} の非推奨API呼び出しに起因するものです。"
                    "Gradle 10 に向けてプラグイン側対応予定のため、現行プロジェクトでの対応は不要です。\n\n"
                )

        self.error_count = error_count
        self.warning_count = warning_count
        return markdown, error_count, warning_count

    def generate_report(
        self, emit_annotations: bool = True
    ) -> Tuple[str, bool, str]:
        """Generates full Markdown report and returns (report, is_failed, failure_message)."""
        perf_md = self.analyze_performance()
        err_md, error_count, _ = self.analyze_errors_and_warnings(
            emit_annotations=emit_annotations
        )

        full_report = "## Android Build Log Analysis\n\n"
        full_report += perf_md
        full_report += err_md

        is_failed = error_count > 0
        failure_msg = (
            f"Found {error_count} errors in the build log." if is_failed else ""
        )
        return full_report, is_failed, failure_msg


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Android build log for errors and warnings"
    )
    parser.add_argument(
        "--log-file-path",
        required=True,
        help="Path to the Android build log file",
    )
    parser.add_argument(
        "--report-path",
        default="",
        help="Path to save the analysis report in Markdown format",
    )
    args = parser.parse_args()

    if not os.path.exists(args.log_file_path):
        print(f"[ERROR] Log file not found at: {args.log_file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Analyzing build log file at: {args.log_file_path}")

    with open(args.log_file_path, "r", encoding="utf-8", errors="replace") as f:
        log_content = f.read()

    analyzer = BuildLogAnalyzer(log_content)
    report, is_failed, failure_msg = analyzer.generate_report(emit_annotations=True)

    # Output to GitHub Step Summary if available
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(report + "\n")
            print(f"[INFO] Appended report to GITHUB_STEP_SUMMARY: {summary_path}")
        except Exception as e:
            print(f"[WARNING] Failed to write to GITHUB_STEP_SUMMARY: {e}", file=sys.stderr)

    # Save to report file if specified
    if args.report_path:
        os.makedirs(os.path.dirname(os.path.abspath(args.report_path)), exist_ok=True)
        with open(args.report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[INFO] Report saved to: {args.report_path}")

    # Set GitHub Actions outputs if available
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        try:
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"report-path={args.report_path}\n")
                f.write(f"error-count={analyzer.error_count}\n")
                f.write(f"warning-count={analyzer.warning_count}\n")
        except Exception as e:
            print(f"[WARNING] Failed to write to GITHUB_OUTPUT: {e}", file=sys.stderr)

    if is_failed:
        print(f"[ERROR] Build analysis failed: {failure_msg}", file=sys.stderr)
        sys.exit(1)
    else:
        print("[SUCCESS] Build analysis completed successfully.")


if __name__ == "__main__":
    main()

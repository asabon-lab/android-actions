#!/usr/bin/env python3
"""Unit tests for publish_release.py."""

import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

from publish_release import GitHubReleaseManager, main


class TestGitHubReleaseManager(unittest.TestCase):
    """Test cases for GitHubReleaseManager."""

    def setUp(self):
        self.manager = GitHubReleaseManager(repository="asabon-lab/android-actions")

    def test_resolve_make_latest(self):
        # auto cases
        self.assertEqual(
            self.manager.resolve_make_latest("auto", prerelease=False, draft=False),
            "true",
        )
        self.assertEqual(
            self.manager.resolve_make_latest("auto", prerelease=True, draft=False),
            "false",
        )
        self.assertEqual(
            self.manager.resolve_make_latest("auto", prerelease=False, draft=True),
            "false",
        )
        # explicit cases
        self.assertEqual(
            self.manager.resolve_make_latest("legacy", prerelease=False, draft=False),
            "legacy",
        )
        self.assertEqual(
            self.manager.resolve_make_latest("false", prerelease=False, draft=False),
            "false",
        )

    @patch.object(GitHubReleaseManager, "run_gh")
    def test_find_existing_draft(self, mock_run_gh):
        mock_run_gh.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="98765\n43210\n"
        )
        draft_id = self.manager.find_existing_draft()
        self.assertEqual(draft_id, "98765")
        mock_run_gh.assert_called_once_with(
            [
                "api",
                "repos/asabon-lab/android-actions/releases",
                "--jq",
                ".[] | select(.draft == true) | .id",
            ],
            check=False,
        )

    @patch.object(GitHubReleaseManager, "run_gh")
    def test_publish_with_existing_draft(self, mock_run_gh):
        # find_existing_draft returns draft id
        mock_run_gh.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="11223\n"),  # find draft
            subprocess.CompletedProcess(args=[], returncode=0, stdout=""),          # api PATCH
            subprocess.CompletedProcess(                                            # release view
                args=[],
                returncode=0,
                stdout=json.dumps({
                    "id": 11223,
                    "url": "https://github.com/asabon-lab/android-actions/releases/tag/v1.0.0",
                    "tagName": "v1.0.0",
                    "name": "v1.0.0",
                    "body": "Release notes",
                    "assets": [],
                }),
            ),
        ]

        info = self.manager.publish_or_update(
            tag_name="v1.0.0",
            title="Version 1.0.0",
            prerelease=False,
            draft=False,
            make_latest="auto",
            update_existing_draft=True,
        )

        self.assertEqual(info.get("id"), 11223)
        patch_call = mock_run_gh.call_args_list[1]
        self.assertIn("-X", patch_call[0][0])
        self.assertIn("PATCH", patch_call[0][0])
        self.assertIn("tag_name=v1.0.0", patch_call[0][0])
        self.assertIn("make_latest=true", patch_call[0][0])

    @patch.object(GitHubReleaseManager, "run_gh")
    def test_publish_update_existing_release(self, mock_run_gh):
        # No draft, existing release found
        mock_run_gh.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout=""),          # find draft (none)
            subprocess.CompletedProcess(args=[], returncode=0, stdout=""),          # release view exists
            subprocess.CompletedProcess(args=[], returncode=0, stdout=""),          # release edit
            subprocess.CompletedProcess(                                            # release view json
                args=[],
                returncode=0,
                stdout=json.dumps({
                    "id": 5566,
                    "url": "https://github.com/asabon-lab/android-actions/releases/tag/v1.0.0",
                }),
            ),
        ]

        info = self.manager.publish_or_update(
            tag_name="v1.0.0",
            title="v1.0.0",
            prerelease=False,
            draft=False,
            make_latest="auto",
            update_existing_draft=True,
        )

        self.assertEqual(info.get("id"), 5566)
        edit_call = mock_run_gh.call_args_list[2]
        self.assertEqual(edit_call[0][0][:3], ["release", "edit", "v1.0.0"])
        self.assertIn("--latest", edit_call[0][0])

    @patch.object(GitHubReleaseManager, "run_gh")
    def test_publish_create_new_release(self, mock_run_gh):
        # No draft, release does not exist
        mock_run_gh.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout=""),          # find draft (none)
            subprocess.CompletedProcess(args=[], returncode=1, stdout="not found"), # release view (404)
            subprocess.CompletedProcess(args=[], returncode=0, stdout=""),          # release create
            subprocess.CompletedProcess(                                            # release view json
                args=[],
                returncode=0,
                stdout=json.dumps({
                    "id": 7788,
                    "url": "https://github.com/asabon-lab/android-actions/releases/tag/v2.0.0",
                }),
            ),
        ]

        info = self.manager.publish_or_update(
            tag_name="v2.0.0",
            title="v2.0.0",
            prerelease=True,
            draft=False,
            make_latest="auto",
            generate_notes=True,
            update_existing_draft=True,
        )

        self.assertEqual(info.get("id"), 7788)
        create_call = mock_run_gh.call_args_list[2]
        self.assertEqual(create_call[0][0][:3], ["release", "create", "v2.0.0"])
        self.assertIn("--prerelease", create_call[0][0])
        self.assertIn("--latest=false", create_call[0][0])
        self.assertIn("--generate-notes", create_call[0][0])

    @patch.object(GitHubReleaseManager, "run_gh")
    def test_upload_artifacts(self, mock_run_gh):
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "app-release.aab")
            file2 = os.path.join(tmpdir, "mapping.txt")
            open(file1, "w").close()
            open(file2, "w").close()

            mock_run_gh.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout=""),  # find draft
                subprocess.CompletedProcess(args=[], returncode=1, stdout=""),  # release exists (no)
                subprocess.CompletedProcess(args=[], returncode=0, stdout=""),  # release create
                subprocess.CompletedProcess(args=[], returncode=0, stdout=""),  # release upload
                subprocess.CompletedProcess(                                    # release view
                    args=[],
                    returncode=0,
                    stdout=json.dumps({
                        "id": 9900,
                        "url": "https://github.com/asabon-lab/android-actions/releases/tag/v1.0.0",
                    }),
                ),
            ]

            pattern = os.path.join(tmpdir, "*")
            self.manager.publish_or_update(
                tag_name="v1.0.0",
                title="v1.0.0",
                artifacts_pattern=pattern,
            )

            upload_call = mock_run_gh.call_args_list[3]
            self.assertEqual(upload_call[0][0][:3], ["release", "upload", "v1.0.0"])
            self.assertIn("--clobber", upload_call[0][0])

    def test_build_summary_markdown(self):
        release_info = {
            "url": "https://github.com/asabon-lab/android-actions/releases/tag/v1.2.0",
            "assets": [
                {"name": "app-release.aab"},
                {"name": "mapping.txt"},
            ],
            "body": "## What's Changed\n* feat: awesome feature (#1)",
        }

        md = self.manager.build_summary_markdown(
            tag_name="v1.2.0",
            title="Version 1.2.0",
            release_info=release_info,
            prerelease=False,
            draft=False,
            resolved_latest="true",
        )

        self.assertIn("### 🚀 GitHub Release Published", md)
        self.assertIn("| **Release** | [Version 1.2.0](https://github.com/asabon-lab/android-actions/releases/tag/v1.2.0) |", md)
        self.assertIn("| **Tag** | `v1.2.0` |", md)
        self.assertIn("| **Release Type** | Full Release (Latest) |", md)
        self.assertIn("#### Uploaded Assets (2 files)", md)
        self.assertIn("- `app-release.aab`", md)
        self.assertIn("- `mapping.txt`", md)
        self.assertIn("<details>", md)
        self.assertIn("<summary><b>📝 Release Notes (クリックで展開)</b></summary>", md)
        self.assertIn("## What's Changed", md)
        self.assertIn("</details>", md)


class TestCLIMain(unittest.TestCase):
    """Test main CLI entry point."""

    @patch("publish_release.GitHubReleaseManager.publish_or_update")
    @patch("publish_release.GitHubReleaseManager.build_summary_markdown")
    def test_cli_outputs_and_summary(self, mock_build_summary, mock_publish):
        mock_publish.return_value = {
            "id": 12345,
            "url": "https://github.com/asabon-lab/android-actions/releases/tag/v1.0.0",
        }
        mock_build_summary.return_value = "### Summary\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "github_output.txt")
            sum_file = os.path.join(tmpdir, "step_summary.md")

            with patch.dict(os.environ, {"GITHUB_OUTPUT": out_file, "GITHUB_STEP_SUMMARY": sum_file}):
                with patch("sys.argv", ["publish_release.py", "--tag-name", "v1.0.0"]):
                    main()

            with open(out_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("release_url=https://github.com/asabon-lab/android-actions/releases/tag/v1.0.0", content)
                self.assertIn("release_id=12345", content)

            with open(sum_file, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "### Summary\n")


if __name__ == "__main__":
    unittest.main()

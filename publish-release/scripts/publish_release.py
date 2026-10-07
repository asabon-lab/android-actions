#!/usr/bin/env python3
"""Publish GitHub Release.

Creates, updates, or publishes GitHub Releases with assets and support
for draft/prerelease promotion. Outputs release info to GITHUB_OUTPUT
and GITHUB_STEP_SUMMARY.
"""

import argparse
import glob
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def append_github_output(key: str, value: str) -> None:
    """Appends key-value pair to GITHUB_OUTPUT if set."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def append_github_step_summary(content: str) -> None:
    """Appends markdown content to GITHUB_STEP_SUMMARY if set."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(content)


class GitHubReleaseManager:
    """Manages publishing and updating GitHub releases using GitHub CLI."""

    def __init__(self, repository: Optional[str] = None):
        self.repository = repository or os.environ.get("GITHUB_REPOSITORY", "")

    def run_gh(
        self,
        args: List[str],
        check: bool = True,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        """Executes a gh CLI command."""
        cmd = ["gh"] + args
        try:
            return subprocess.run(
                cmd,
                check=check,
                text=True,
                capture_output=capture_output,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError as e:
            if capture_output:
                print(f"[ERROR] Command '{' '.join(cmd)}' failed: {e.stderr}", file=sys.stderr)
            raise

    def resolve_make_latest(
        self, make_latest: str, prerelease: bool, draft: bool
    ) -> str:
        """Determines the effective make-latest value."""
        if make_latest == "auto":
            return "true" if (not prerelease and not draft) else "false"
        return make_latest

    def find_existing_draft(self) -> Optional[str]:
        """Finds the first existing draft release ID in repository."""
        repo_prefix = f"repos/{self.repository}/releases" if self.repository else "releases"
        try:
            res = self.run_gh(
                ["api", repo_prefix, "--jq", ".[] | select(.draft == true) | .id"],
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                lines = res.stdout.strip().splitlines()
                return lines[0].strip() if lines else None
        except Exception:
            pass
        return None

    def release_exists(self, tag_name: str) -> bool:
        """Checks if a release with the given tag exists."""
        res = self.run_gh(["release", "view", tag_name], check=False)
        return res.returncode == 0

    def publish_or_update(
        self,
        tag_name: str,
        title: str,
        prerelease: bool = False,
        draft: bool = False,
        make_latest: str = "auto",
        generate_notes: bool = True,
        update_existing_draft: bool = True,
        artifacts_pattern: str = "",
    ) -> Dict[str, Any]:
        """Publishes or updates the release and uploads artifacts."""
        resolved_latest = self.resolve_make_latest(make_latest, prerelease, draft)

        print(f"[INFO] Target Release: {tag_name}")
        print(f"[INFO] Title: {title}")
        print(
            f"[INFO] Pre-release: {prerelease} | Draft: {draft} | Make Latest: {resolved_latest}"
        )

        draft_id = None
        if update_existing_draft:
            print("[INFO] Searching for existing draft releases in repository...")
            draft_id = self.find_existing_draft()

        exists = False if draft_id else self.release_exists(tag_name)

        if draft_id:
            print(
                f"[INFO] Found draft release ID: {draft_id}. Publishing draft for tag {tag_name}..."
            )
            patch_target = (
                f"repos/{self.repository}/releases/{draft_id}"
                if self.repository
                else f"releases/{draft_id}"
            )
            self.run_gh(
                [
                    "api",
                    "-X",
                    "PATCH",
                    patch_target,
                    "-f",
                    f"tag_name={tag_name}",
                    "-f",
                    f"name={title}",
                    "-F",
                    f"draft={'true' if draft else 'false'}",
                    "-F",
                    f"prerelease={'true' if prerelease else 'false'}",
                    "-f",
                    f"make_latest={resolved_latest}",
                ]
            )
        elif exists:
            print(f"[INFO] Release '{tag_name}' already exists. Updating properties...")
            edit_args = [
                "release",
                "edit",
                tag_name,
                "--title",
                title,
                "--prerelease" if prerelease else "--prerelease=false",
                "--draft" if draft else "--draft=false",
            ]
            if resolved_latest == "true":
                edit_args.append("--latest")
            elif resolved_latest == "false":
                edit_args.append("--latest=false")

            self.run_gh(edit_args)
        else:
            print(f"[INFO] Creating new release for tag '{tag_name}'...")
            create_args = ["release", "create", tag_name, "--title", title]
            if prerelease:
                create_args.append("--prerelease")
            if draft:
                create_args.append("--draft")
            if resolved_latest == "true":
                create_args.append("--latest")
            elif resolved_latest == "false":
                create_args.append("--latest=false")
            if generate_notes:
                create_args.append("--generate-notes")

            self.run_gh(create_args)

        # Upload artifacts if provided
        uploaded_files: List[str] = []
        if artifacts_pattern:
            print(f"[INFO] Uploading release artifacts matching '{artifacts_pattern}'...")
            files = sorted(glob.glob(artifacts_pattern))
            if not files:
                print(f"::warning::No files matched artifact pattern: {artifacts_pattern}")
            else:
                print(f"[INFO] Uploading {len(files)} file(s): {', '.join(files)}")
                self.run_gh(["release", "upload", tag_name] + files + ["--clobber"])
                uploaded_files = files

        # Fetch release details
        release_info = self.get_release_info(tag_name)
        return release_info

    def get_release_info(self, tag_name: str) -> Dict[str, Any]:
        """Fetches release info JSON using gh release view."""
        try:
            res = self.run_gh(
                [
                    "release",
                    "view",
                    tag_name,
                    "--json",
                    "url,id,name,tagName,isDraft,isPrerelease,assets,body",
                ],
                check=False,
            )
            if res.returncode == 0:
                return json.loads(res.stdout)
        except Exception as e:
            print(f"[WARN] Failed to retrieve release info JSON: {e}", file=sys.stderr)
        return {}

    def build_summary_markdown(
        self,
        tag_name: str,
        title: str,
        release_info: Dict[str, Any],
        prerelease: bool,
        draft: bool,
        resolved_latest: str,
    ) -> str:
        """Constructs formatted Markdown for GitHub Step Summary."""
        url = release_info.get("url", "")
        safe_title = title.replace("|", "\\|")
        display_link = f"[{safe_title}]({url})" if url else safe_title

        if draft:
            type_desc = "Draft Release"
        elif prerelease:
            type_desc = "Pre-release"
        else:
            type_desc = "Full Release"

        if resolved_latest == "true":
            type_desc += " (Latest)"

        assets = release_info.get("assets", [])
        body = release_info.get("body", "")

        markdown = "### 🚀 GitHub Release Published\n\n"
        markdown += "| 項目 | 内容 |\n"
        markdown += "| :--- | :--- |\n"
        markdown += f"| **Release** | {display_link} |\n"
        markdown += f"| **Tag** | `{tag_name}` |\n"
        markdown += f"| **Release Type** | {type_desc} |\n\n"

        if assets:
            markdown += f"#### Uploaded Assets ({len(assets)} files)\n\n"
            for a in assets:
                name = a.get("name", "")
                markdown += f"- `{name}`\n"
            markdown += "\n"

        if body and body.strip():
            markdown += "<details>\n"
            markdown += "<summary><b>📝 Release Notes (クリックで展開)</b></summary>\n\n"
            markdown += f"{body.strip()}\n\n"
            markdown += "</details>\n\n"

        return markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish, update, or draft-promote a GitHub Release"
    )
    parser.add_argument("--tag-name", required=True, help="Release tag name")
    parser.add_argument("--release-title", default="", help="Release title")
    parser.add_argument(
        "--prerelease",
        type=lambda v: str(v).lower() in ("yes", "true", "t", "1"),
        default=False,
        help="Mark as pre-release",
    )
    parser.add_argument(
        "--draft",
        type=lambda v: str(v).lower() in ("yes", "true", "t", "1"),
        default=False,
        help="Mark as draft release",
    )
    parser.add_argument(
        "--make-latest",
        default="auto",
        help="Mark as latest release ('true', 'false', 'legacy', 'auto')",
    )
    parser.add_argument(
        "--generate-notes",
        type=lambda v: str(v).lower() in ("yes", "true", "t", "1"),
        default=True,
        help="Automatically generate release notes",
    )
    parser.add_argument(
        "--update-existing-draft",
        type=lambda v: str(v).lower() in ("yes", "true", "t", "1"),
        default=True,
        help="Update and publish existing draft release if found",
    )
    parser.add_argument(
        "--artifacts",
        default="",
        help="Glob pattern of artifacts to upload",
    )
    parser.add_argument(
        "--repository",
        default="",
        help="GitHub repository (owner/repo)",
    )
    args = parser.parse_args()

    title = args.release_title or args.tag_name

    manager = GitHubReleaseManager(repository=args.repository)
    release_info = manager.publish_or_update(
        tag_name=args.tag_name,
        title=title,
        prerelease=args.prerelease,
        draft=args.draft,
        make_latest=args.make_latest,
        generate_notes=args.generate_notes,
        update_existing_draft=args.update_existing_draft,
        artifacts_pattern=args.artifacts,
    )

    release_url = release_info.get("url", "")
    release_id = str(release_info.get("id", ""))

    print(f"[SUCCESS] Release finalized: {release_url or args.tag_name}")
    append_github_output("release_url", release_url)
    append_github_output("release_id", release_id)

    # Step Summary
    resolved_latest = manager.resolve_make_latest(
        args.make_latest, args.prerelease, args.draft
    )
    summary_md = manager.build_summary_markdown(
        tag_name=args.tag_name,
        title=title,
        release_info=release_info,
        prerelease=args.prerelease,
        draft=args.draft,
        resolved_latest=resolved_latest,
    )
    append_github_step_summary(summary_md)


if __name__ == "__main__":
    main()

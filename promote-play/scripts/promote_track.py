#!/usr/bin/env python3
"""
Promotes an Android app release between Google Play tracks (e.g., internal -> production)
using the Google Play Developer API (androidpublisher v3).

Features:
- Flexible track promotion (internal, alpha, beta, production).
- VersionCode guard: Aborts with exit code 2 if target track already contains the versionCode.
- Dry-run mode for pre-flight testing.
- Outputs promoted versionCode and editId to $GITHUB_OUTPUT.
"""

import argparse
import json
import os
import sys

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    service_account = None
    build = None
    HttpError = Exception


def parse_args():
    parser = argparse.ArgumentParser(
        description="Promote an Android release between Google Play tracks."
    )
    parser.add_argument(
        "--package-name",
        required=True,
        help="Android application package name (e.g. com.example.app)",
    )
    parser.add_argument(
        "--service-account-json",
        default=None,
        help="Path to service account JSON file, or raw JSON string. Fallback to PLAY_CONSOLE_SERVICE_ACCOUNT_JSON env var.",
    )
    parser.add_argument(
        "--source-track",
        default="internal",
        help="Source track to promote from (default: internal)",
    )
    parser.add_argument(
        "--target-track",
        default="production",
        help="Target track to promote to (default: production)",
    )
    parser.add_argument(
        "--version-code",
        type=int,
        default=None,
        help="Specific versionCode to promote. Defaults to latest release in source track.",
    )
    parser.add_argument(
        "--status",
        default="completed",
        choices=["completed", "inProgress", "draft", "halted"],
        help="Release status for target track (default: completed)",
    )
    parser.add_argument(
        "--user-fraction",
        type=float,
        default=None,
        help="User fraction for staged rollout (e.g. 0.1 for 10%%). Only valid if status is inProgress.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate promotion without committing the edit.",
    )
    return parser.parse_args()


def get_credentials(service_account_input):
    if service_account is None:
        print(
            "Error: Missing required Python packages. Run: pip install google-api-python-client google-auth",
            file=sys.stderr,
        )
        sys.exit(1)

    sa_content = service_account_input or os.environ.get("PLAY_CONSOLE_SERVICE_ACCOUNT_JSON")
    if not sa_content:
        print(
            "Error: Service account JSON must be provided via --service-account-json or PLAY_CONSOLE_SERVICE_ACCOUNT_JSON environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    sa_content = sa_content.strip()
    scopes = ["https://www.googleapis.com/auth/androidpublisher"]

    if sa_content.startswith("{") and sa_content.endswith("}"):
        try:
            info = json.loads(sa_content)
        except json.JSONDecodeError as e:
            print(f"Error parsing service account JSON string: {e}", file=sys.stderr)
            sys.exit(1)
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)
    elif os.path.isfile(sa_content):
        return service_account.Credentials.from_service_account_file(sa_content, scopes=scopes)
    else:
        print(
            f"Error: Invalid service account path or raw JSON format: {sa_content[:30]}...",
            file=sys.stderr,
        )
        sys.exit(1)


def append_github_output(key: str, value: str):
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def main():
    # Ensure stdout/stderr handles UTF-8 on Windows environments if possible
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    args = parse_args()
    credentials = get_credentials(args.service_account_json)
    package_name = args.package_name
    source_track_name = args.source_track
    target_track_name = args.target_track

    service = build("androidpublisher", "v3", credentials=credentials)

    print(f"[1/4] Creating application edit for '{package_name}'...")
    try:
        edit = service.edits().insert(body={}, packageName=package_name).execute()
        edit_id = edit["id"]
        print(f"      Created editId: {edit_id}")
    except HttpError as e:
        print(f"Failed to create app edit: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[2/4] Inspecting tracks (source: '{source_track_name}', target: '{target_track_name}')...")

    # 1. Fetch source track
    try:
        source_track = (
            service.edits()
            .tracks()
            .get(packageName=package_name, editId=edit_id, track=source_track_name)
            .execute()
        )
    except HttpError as e:
        print(f"Failed to get source track '{source_track_name}': {e}", file=sys.stderr)
        sys.exit(1)

    source_releases = source_track.get("releases", [])
    if not source_releases:
        print(f"Error: No releases found in source track '{source_track_name}' to promote.", file=sys.stderr)
        sys.exit(1)

    # 2. Identify target release to promote
    target_release = None
    if args.version_code:
        for r in source_releases:
            if str(args.version_code) in [str(vc) for vc in r.get("versionCodes", [])]:
                target_release = r
                break
        if not target_release:
            print(
                f"Error: Release with versionCode {args.version_code} not found in source track '{source_track_name}'.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # Use first (most recent) release
        target_release = source_releases[0]

    target_vcs = [int(vc) for vc in target_release.get("versionCodes", [])]
    target_name = target_release.get("name", f"versionCode-{target_vcs}")
    primary_vc = target_vcs[0] if target_vcs else 0
    print(f"      Target release from '{source_track_name}': {target_name} (versionCodes: {target_vcs})")

    # 3. Fetch target track & Duplicate Guard Check
    try:
        target_track = (
            service.edits()
            .tracks()
            .get(packageName=package_name, editId=edit_id, track=target_track_name)
            .execute()
        )
        target_existing_releases = target_track.get("releases", [])
    except HttpError as e:
        if getattr(e, "resp", None) and getattr(e.resp, "status", None) == 404:
            target_existing_releases = []
        else:
            print(f"Warning: Failed to fetch existing '{target_track_name}' track: {e}", file=sys.stderr)
            target_existing_releases = []

    target_existing_vcs = set()
    for r in target_existing_releases:
        for vc in r.get("versionCodes", []):
            target_existing_vcs.add(int(vc))

    print(f"      Existing '{target_track_name}' track versionCodes: {list(target_existing_vcs)}")

    # GUARD: Abort if already released in target track
    already_in_target = [vc for vc in target_vcs if vc in target_existing_vcs]
    if already_in_target:
        print(
            f"[GUARD TRIGGERED] Version code(s) {already_in_target} already exist in '{target_track_name}' track!",
            file=sys.stderr,
        )
        print("Aborting promotion to prevent duplicate/redundant release.", file=sys.stderr)
        sys.exit(2)

    # 4. Prepare promotion release payload
    print(f"[3/4] Preparing release for '{target_track_name}' track...")
    new_release = {
        "name": target_name,
        "versionCodes": [str(vc) for vc in target_vcs],
        "status": args.status,
        "releaseNotes": target_release.get("releaseNotes", []),
    }

    if args.user_fraction is not None and args.status == "inProgress":
        new_release["userFraction"] = args.user_fraction

    if args.dry_run:
        print(f"[DRY-RUN] Would update track '{target_track_name}' with:")
        print(json.dumps(new_release, ensure_ascii=False, indent=2))
        print("Dry run complete. No changes were committed.")
        append_github_output("promoted_version_code", str(primary_vc))
        append_github_output("edit_id", edit_id)
        sys.exit(0)

    try:
        service.edits().tracks().update(
            packageName=package_name,
            editId=edit_id,
            track=target_track_name,
            body={"track": target_track_name, "releases": [new_release]},
        ).execute()
    except HttpError as e:
        print(f"Failed to update '{target_track_name}' track: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Commit edit
    print(f"[4/4] Committing edit '{edit_id}'...")
    try:
        commit_res = service.edits().commit(packageName=package_name, editId=edit_id).execute()
        print(f"[SUCCESS] Successfully promoted {target_name} (versionCodes: {target_vcs}) to '{target_track_name}' track!")
        print(f"          Commit response: {commit_res}")
        append_github_output("promoted_version_code", str(primary_vc))
        append_github_output("edit_id", edit_id)
    except HttpError as e:
        print(f"Failed to commit edit: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

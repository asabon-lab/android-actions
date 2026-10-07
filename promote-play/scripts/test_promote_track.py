import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add scripts directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import promote_track


class TestPromoteTrack(unittest.TestCase):
    def test_parse_args_defaults(self):
        test_args = ["promote_track.py", "--package-name", "com.example.app"]
        with patch.object(sys, "argv", test_args):
            args = promote_track.parse_args()
            self.assertEqual(args.package_name, "com.example.app")
            self.assertEqual(args.source_track, "internal")
            self.assertEqual(args.target_track, "production")
            self.assertEqual(args.status, "completed")
            self.assertFalse(args.dry_run)
            self.assertIsNone(args.version_code)
            self.assertIsNone(args.user_fraction)

    def test_parse_args_custom(self):
        test_args = [
            "promote_track.py",
            "--package-name",
            "net.asabon.intervaltimer",
            "--source-track",
            "beta",
            "--target-track",
            "production",
            "--version-code",
            "42",
            "--status",
            "inProgress",
            "--user-fraction",
            "0.25",
            "--dry-run",
        ]
        with patch.object(sys, "argv", test_args):
            args = promote_track.parse_args()
            self.assertEqual(args.package_name, "net.asabon.intervaltimer")
            self.assertEqual(args.source_track, "beta")
            self.assertEqual(args.target_track, "production")
            self.assertEqual(args.version_code, 42)
            self.assertEqual(args.status, "inProgress")
            self.assertEqual(args.user_fraction, 0.25)
            self.assertTrue(args.dry_run)

    @patch("promote_track.build")
    @patch("promote_track.get_credentials")
    def test_guard_aborts_when_already_in_target(self, mock_creds, mock_build):
        # Setup mock Google API client
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock edit insert
        mock_service.edits().insert().execute.return_value = {"id": "test-edit-123"}

        # Mock tracks().get() responses
        # source track has versionCode 100
        # target track ALREADY has versionCode 100
        def mock_tracks_get(packageName, editId, track):
            track_mock = MagicMock()
            if track == "internal":
                track_mock.execute.return_value = {
                    "releases": [
                        {
                            "name": "1.0.0",
                            "versionCodes": ["100"],
                            "status": "completed",
                        }
                    ]
                }
            elif track == "production":
                track_mock.execute.return_value = {
                    "releases": [
                        {
                            "name": "1.0.0",
                            "versionCodes": ["100"],
                            "status": "completed",
                        }
                    ]
                }
            return track_mock

        mock_service.edits().tracks().get.side_effect = mock_tracks_get

        test_args = [
            "promote_track.py",
            "--package-name",
            "com.example.app",
            "--service-account-json",
            '{"type": "service_account"}',
        ]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as cm:
                promote_track.main()
            # Guard must abort with exit code 2
            self.assertEqual(cm.exception.code, 2)

    @patch("promote_track.build")
    @patch("promote_track.get_credentials")
    def test_dry_run_success(self, mock_creds, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.edits().insert().execute.return_value = {"id": "dry-edit-456"}

        def mock_tracks_get(packageName, editId, track):
            track_mock = MagicMock()
            if track == "internal":
                track_mock.execute.return_value = {
                    "releases": [{"name": "1.1.0", "versionCodes": ["101"]}]
                }
            elif track == "production":
                track_mock.execute.return_value = {
                    "releases": [{"name": "1.0.0", "versionCodes": ["100"]}]
                }
            return track_mock

        mock_service.edits().tracks().get.side_effect = mock_tracks_get

        test_args = [
            "promote_track.py",
            "--package-name",
            "com.example.app",
            "--service-account-json",
            '{"type": "service_account"}',
            "--dry-run",
        ]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as cm:
                promote_track.main()
            self.assertEqual(cm.exception.code, 0)
            mock_service.edits().commit.assert_not_called()

    @patch("promote_track.build")
    @patch("promote_track.get_credentials")
    def test_promotion_commit_success(self, mock_creds, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.edits().insert().execute.return_value = {"id": "commit-edit-789"}
        mock_service.edits().commit().execute.return_value = {"id": "commit-edit-789"}

        def mock_tracks_get(packageName, editId, track):
            track_mock = MagicMock()
            if track == "internal":
                track_mock.execute.return_value = {
                    "releases": [{"name": "1.2.0", "versionCodes": ["102"]}]
                }
            elif track == "production":
                track_mock.execute.return_value = {
                    "releases": [{"name": "1.1.0", "versionCodes": ["101"]}]
                }
            return track_mock

        mock_service.edits().tracks().get.side_effect = mock_tracks_get

        test_args = [
            "promote_track.py",
            "--package-name",
            "com.example.app",
            "--service-account-json",
            '{"type": "service_account"}',
        ]
        with patch.object(sys, "argv", test_args):
            promote_track.main()
            mock_service.edits().tracks().update.assert_called_once()
            mock_service.edits().commit().execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()

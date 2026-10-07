# Issue #009: publish-release を scripts/publish_release.py へ分離・Python化

- **ステータス**: 完了
- **作成日**: 2026-10-08
- **対象ブランチ**: `refactor/009-refactor-publish-release-to-python`

---

## 🎯 目的 / 概要

`publish-release/action.yml` にインラインで記述されている約155行の Bash スクリプトを、他の Action（`promote-play`, `analyze-build-log`）と同様に `publish-release/scripts/publish_release.py` へ分離・Python化する。
これにより、YAML 定義をスリム化し、`unittest` による単体テスト（`test_publish_release.py`）を整備して CI での自動検証を可能にする。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `publish-release/scripts/publish_release.py` が作成され、既存の Bash ロジックと同等の機能を持つこと:
  - ドラフト検索 & 昇格（`update_existing_draft`）
  - 既存リリース更新（`gh release edit`）
  - 新規リリース作成（`gh release create`）
  - `make_latest` の auto 判定ロジック
  - アセットの glob 展開 & アップロード（`gh release upload --clobber`）
  - 出力変数（`release-url`, `release-id`）の設定
  - Job Summary Markdown（確定情報テーブル、アセット一覧、折りたたみリリースノート）の生成と書き込み
- [x] Python 標準ライブラリのみを使用し、外部依存（pip）を不要とすること
- [x] `publish-release/scripts/test_publish_release.py` を作成し、GitHub CLI 呼び出しをモックした単体テストが全件パスすること
- [x] `.github/workflows/ci.yml` に `publish-release` の単体テスト実行ステップを追加すること
- [x] `publish-release/action.yml` が `python3` / `python` スクリプトの呼び出しのみの薄いラッパーにスリム化されていること

---

## 🛠️ 設計方針・技術的メモ

- `subprocess.run` を用いて `gh` CLI コマンドを実行するヘルパーメソッドを用意し、テスト時に `unittest.mock.patch` で容易にモック可能にする。
- Windows 環境（cp932）でのエンコーディング配慮（`sys.stdout.reconfigure(encoding="utf-8")`）。
- 引数は `argparse` または環境変数渡し。`action.yml` からの引数渡しは CLI 引数（`--tag-name`, `--title` など）として整理。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] 単体テスト（`test_publish_release.py`）の作成と全件パス
- [x] CI ワークフロー（`.github/workflows/ci.yml`）へのテスト追加
- [x] Action / ワークフロー構文の確認
- [x] ローカルテスト・CI（GitHub Actions）の通過

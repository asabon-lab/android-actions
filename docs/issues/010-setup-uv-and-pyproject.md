# Issue #010: uv によるパッケージ管理と pyproject.toml の整備

- **ステータス**: 進行中
- **作成日**: 2026-10-08
- **対象ブランチ**: `chore/010-setup-uv-and-pyproject`

---

## 🎯 目的 / 概要

本リポジトリ内の Python スクリプト群（`promote-play`, `analyze-build-log`, `publish-release`）のローカルテストおよび開発環境を高速かつ決定論的に管理するため、リポジトリルートに `pyproject.toml` を導入し、`uv` によるパッケージ管理・仮想環境管理体制を整備する。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [ ] リポジトリルートに PEP 621 準拠の `pyproject.toml` が作成されていること
  - 依存関係（`google-api-python-client`, `google-auth` 等）が明記されていること
  - Python バージョン制約（`>=3.10`）が設定されていること
- [ ] `.gitignore` に Python 仮想環境ディレクトリ（`.venv/` 等）が含まれていること
- [ ] `uv` によるロックファイル作成（`uv.lock`）および `uv run` によるテスト実行が動作すること
- [ ] `AGENTS.md` の主要コマンド集に `uv run` によるテスト実行手順を追記すること

---

## 🛠️ 設計方針・技術的メモ

- 本リポジトリは配布用 Python パッケージではないため、wheel ビルド設定（`[build-system]`）は不要または最小限とし、スタンドアロンプロジェクト（`[project]` + `[tool.uv]`）として構成する。
- 外部 Action 利用側には影響を与えない構造とする。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・更新
- [ ] `uv run` によるローカル単体テストの全件通過確認
- [ ] ドキュメント（`AGENTS.md` 等）の更新
- [ ] Action / ワークフローへの悪影響がないことの確認

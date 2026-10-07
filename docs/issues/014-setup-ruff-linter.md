# Issue #014: Ruff Linter の導入と CI チェックの追加

- **ステータス**: 進行中
- **作成日**: 2026-10-08
- **対象ブランチ**: `chore/014-setup-ruff-linter`

---

## 🎯 目的 / 概要

Python コードの品質・スタイルの一貫性を担保し、コードベースの保守性を高めるため、超高速 Python Linter / Formatter である **Ruff** を導入する。
ローカル開発（`uv run ruff check .`）および GitHub Actions CI（`.github/workflows/ci.yml`）で自動的に静的解析が実行されるようにする。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [ ] `pyproject.toml` に開発用依存関係（`dependency-groups.dev`）として `ruff` を追加し、`uv.lock` を更新すること
- [ ] `pyproject.toml` に `[tool.ruff]` 設定（ターゲット Python バージョン 3.10、行長 100〜120等）を記述すること
- [ ] 既存の Python スクリプト（`promote-play/scripts/`, `analyze-build-log/scripts/`, `publish-release/scripts/`）に対して `ruff check` を実行し、全件パス（警告・エラーゼロ）すること
- [ ] `.github/workflows/ci.yml` に Ruff Lint チェック用ジョブ（`lint-python` 等）を追加し、PR / Push 時に自動実行されること
- [ ] ドキュメント（`docs/TESTING.md`, `AGENTS.md`）に Ruff による静的解析コマンドの説明を追記すること

---

## 🛠️ 設計方針・技術的メモ

- **設定ファイル**: `pyproject.toml` に `[tool.ruff]` および `[tool.ruff.lint]` を定義。
- **CI 実装**:
  - `lint-python` ジョブを新設。
  - GitHub Actions アノテーション連携を考慮し、`ruff check --output-format=github .` または公式 Action を検討。
  - `ci.yml` の `paths:` トリガーに `pyproject.toml`, `uv.lock` を追加。
- **ローカル開発**:
  - `uv run ruff check .` および `uv run ruff check --fix .` で実行可能にする。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・テスト
- [ ] ローカルでの `uv run ruff check .` パス確認
- [ ] CI 設定の更新と動作確認
- [ ] Issue ステータスの完了更新

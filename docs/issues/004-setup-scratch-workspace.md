# Issue #004: scratch/ 一時作業ワークスペースの導入とルール化

- **ステータス**: 完了
- **作成日**: 2026-10-05
- **対象ブランチ**: `chore/004-setup-scratch-workspace`

---

## 🎯 目的 / 概要

PR 本文や一時的なスクリプト、API 送信用 JSON ファイル、検証ログなどの一時ファイルがリポジトリルートに散乱・誤コミットされるのを防ぐため、`scratch/` ディレクトリを一時作業用ワークスペースとして定義・ルール化し、`.gitignore` に追加する。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `.gitignore`: `scratch/` を無視パターンに追加
- [x] `.agents/rules/environment-isolation.md`: 一時ファイル配置場所として `scratch/` の利用ルールを明記
- [x] `.agents/skills/create-pr/SKILL.md`: PR 本文一時ファイルを `scratch/pr_body.md` に統一
- [x] `AGENTS.md`: コマンドチートシート等の一時ファイルパスを `scratch/` に統一

---

## 🛠️ 設計方針・技術的メモ

- PowerShell や各種 CLI でのエスケープ崩れ対策として、インライン文字列（`--body "..."` 等）ではなく一時ファイル（`scratch/pr_body.md`）経由で渡す運用を標準化する。
- `scratch/` 配下は `.gitignore` で除外されているため、一時ファイルが残っても git 追跡対象外となり安全。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] `.gitignore` の動作確認
- [x] CI（GitHub Actions）の通過

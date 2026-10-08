# Issue #016: sync-harness スキルの取り込み

- **ステータス**: 進行中
- **作成日**: 2026-10-08
- **対象ブランチ**: `chore/016-import-sync-harness-skill`

---

## 🎯 目的 / 概要

同じローカル環境にクローンされている `IntervalTimer` リポジトリから、AI ハーネス環境（運用規約、ルール、スキル、テンプレート等）の差分を安全に同期・検証するためのスキル `sync-harness` を `android-actions` へ取り込む。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [ ] `.agents/skills/sync-harness/SKILL.md` を配置し、android-actions 視点に適した記述（例示リポジトリや注意事項）になっていること
- [ ] `.agents/skills/sync-harness/scripts/diff-harness.ps1` を配置し、PowerShell スクリプトとして正常に動作すること
- [ ] `diff-harness.ps1` を実行し、`../IntervalTimer` との間で差分スキャンが正常に動作することを確認すること

---

## 🛠️ 設計方針・技術的メモ

- `IntervalTimer` の `.agents/skills/sync-harness/` 配下をインポートする。
- `SKILL.md` 内のリポジトリ例示（`android-actions` 等 -> `IntervalTimer` 等）を本リポジトリ向けに調整。
- PowerShell スクリプト（`diff-harness.ps1`）の実行確認。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・更新
- [ ] Action / ワークフロー構文やローカルテストの確認
- [ ] Issue ファイルの完了更新

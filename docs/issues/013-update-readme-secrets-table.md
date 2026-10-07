# Issue #013: README の Repository Secrets 記載を Action 対応表に改善

- **ステータス**: 完了
- **作成日**: 2026-10-08
- **対象ブランチ**: `docs/013-update-readme-secrets-table`

---

## 🎯 目的 / 概要

ルート `README.md` の「必要な Repository Secrets」セクションにおいて、すべての Action がすべての Secret を必要とするわけではないため、各 Action と Secret の対応関係を整理したマトリクス形式の表に改善する。
これにより、利用者が導入する Action に応じて必要な Secret のみを迷わず設定できるようにする。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] ルート `README.md` の「必要な Repository Secrets」セクションが Action と Secrets の対応表に更新されていること:
  - `setup-keystore`: `KEYSTORE_BASE64`
  - `promote-play`: `PLAY_CONSOLE_SERVICE_ACCOUNT_JSON`
  - `publish-release`: `GITHUB_TOKEN`（通常は自動提供・`contents: write` 権限について言及）
  - `analyze-build-log`: Secret 不要である旨
  - （参考）Gradle リリースビルド用 Secret（`KEY_ALIAS`, `KEYSTORE_PASSWORD`, `KEY_PASSWORD`）の区別明記
- [x] ドキュメントのレイアウト・Markdown テーブル構文が崩れていないこと

---

## 🛠️ 設計方針・技術的メモ

- Action 利用側が「自分の使いたい Action に必要な Secret だけ」を直感的に把握できる分かりやすい表構成とする。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] Markdown 表示の確認
- [x] Issue ステータスの完了更新

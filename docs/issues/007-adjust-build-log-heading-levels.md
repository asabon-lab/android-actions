# Issue #007: analyze-build-log の出力見出しレベルを一段下げる

- **ステータス**: 進行中
- **作成日**: 2026-10-08
- **対象ブランチ**: `refactor/007-adjust-build-log-heading-levels`

---

## 🎯 目的 / 概要

`analyze-build-log` が生成する Markdown レポートの見出しレベルが他のサードパーティ製 Action と比較して一段高く設定されているため、全体の統一感を図る目的で見出しレベルを全体的に一段下げる（H2 → H3、H3 → H4）。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [ ] `analyze-build-log/scripts/analyze_build_log.py` で出力される Markdown レポートの各見出しレベルが一段下げられていること
  - トップ見出し: `## Android Build Log Analysis` → `### Android Build Log Analysis`
  - 各セクション見出し: `### Build Performance Summary` → `#### Build Performance Summary`
  - エラー・警告解析: `### Error and Warning Analysis` → `#### Error and Warning Analysis`
  - 既知の警告セクション: `### Known Warnings / Ignorable Warnings` → `#### Known Warnings / Ignorable Warnings`
- [ ] 単体テスト（`test_analyze_build_log.py`）が更新され、すべてのテストがパスすること
- [ ] 既存の機能（アノテーション出力、エラー検出、終了コード等）に影響を与えないこと

---

## 🛠️ 設計方針・技術的メモ

- `analyze_build_log.py` 内の見出し文字列プレフィックスを変更。
- 見出し検証を含む単体テストアサーションを更新。
- 単体テスト（`test_analyze_build_log.py`）およびリポジトリ全体のテストを実行して検証。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・更新
- [ ] 単体テスト（test_*.py）の作成または更新
- [ ] Action / ワークフロー構文の確認
- [ ] ローカルテスト・CI（GitHub Actions）の通過
- [ ] 各 Action の README.md およびルート README.md の更新（該当する場合）

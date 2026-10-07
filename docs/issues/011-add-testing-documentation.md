# Issue #011: ローカルテスト & 開発ガイド (docs/TESTING.md) の作成

- **ステータス**: 完了
- **作成日**: 2026-10-08
- **対象ブランチ**: `docs/011-add-testing-documentation`

---

## 🎯 目的 / 概要

本リポジトリの開発者およびコントリビューター向けに、ローカル環境での Python スクリプト単体テスト実行手順や `uv` による環境構築方法をまとめた `docs/TESTING.md` を作成する。
また、利用者向けであるルート `README.md` から `docs/TESTING.md` への適切な導線を整備する。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `docs/TESTING.md` が作成され、以下の情報が網羅されていること:
  - 前提条件（Python 3.10+, uv）
  - `uv` を使用した単体テスト実行コマンド（一括実行・Action 個別実行）
  - 標準 Python（venv）でのテスト実行コマンド
  - CI（GitHub Actions）との連携・検証方針
- [x] ルート `README.md` に開発・テストガイドへの導線リンク（`docs/TESTING.md`）が追加されていること
- [x] `AGENTS.md` に `docs/TESTING.md` への参照が追加されていること

---

## 🛠️ 設計方針・技術的メモ

- ルート `README.md` は Action 利用者向けの「使い方」に集中させ、開発者向けの環境構築・テスト手順を `docs/TESTING.md` に分離することで関心の分離を保つ。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] ドキュメント内のリンク・コマンドの動作確認
- [x] Issue ステータスの完了更新

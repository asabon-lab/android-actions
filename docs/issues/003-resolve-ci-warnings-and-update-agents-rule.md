# Issue #003: CI 警告の解消と AGENTS.md 監視ルールの追加

- **ステータス**: 進行中
- **作成日**: 2026-10-05
- **対象ブランチ**: `chore/003-resolve-ci-warnings`

---

## 🎯 目的 / 概要

GitHub Actions CI で発生している Node.js 20 廃止警告（Annotations）を解消するため、`actions/checkout`、`actions/setup-python`、`release-drafter` のバージョンを Node.js 24 対応版（最新バージョン）へアップデートする。
また、`AntigravityQuota` リポジトリと同様に、警告（Warnings/Annotations）の監視・解消を義務付けるルールを `AGENTS.md` に取り込む。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `AGENTS.md`: 「GitHub Actions CI & 警告（Warnings/Annotations）監視ルール」を追加
- [x] `.github/workflows/ci.yml`: `actions/checkout@v7`, `actions/setup-python@v7` にアップデート
- [x] `.github/workflows/release-drafter.yml`: `release-drafter/release-drafter@v7` にアップデート
- [x] `promote-play/action.yml`: `actions/setup-python@v7` にアップデート
- [ ] CI を実行し、Annotations の警告（Node.js 20 is deprecated...）がゼロになることを確認

---

## 🛠️ 設計方針・技術的メモ

- GitHub Actions ランナーの Node.js 24 移行に伴い、公式アクションの Node.js 24 対応バージョン（`checkout@v7`, `setup-python@v7`）を採用する。
- 警告は放置せず、速やかに修正・解消する運用体制を `AGENTS.md` に明文化する。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・更新
- [ ] CI（GitHub Actions）の通過
- [ ] CI ログ上で警告（Node.js 20 非推奨等）が解消されていることの確認

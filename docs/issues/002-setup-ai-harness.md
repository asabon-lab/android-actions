# Issue #002: AI ハーネス開発環境の整備

- **ステータス**: 完了
- **作成日**: 2026-10-05
- **対象ブランチ**: `chore/002-setup-ai-harness`

---

## 🎯 目的 / 概要

`IntervalTimer` と同等の品質管理・Issue駆動・PR運用・Gitフック・エージェントスキル体系を本リポジトリに導入し、AI とのペアプログラミングや継続的な Action 開発・保守を安全かつ効率的に進められる AI ハーネス環境を構築する。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `AGENTS.md`: 本リポジトリの目的、Action 開発規約、Git Flow、Issue 駆動、テスト方針を定義
- [x] `.githooks/`: `main` への直接コミット・プッシュ防止、ブランチ命名規則検証（`pre-commit`, `pre-push`）
- [x] `.agents/`: エージェント用ルール（`environment-isolation.md`）およびスキル（`create-issue`, `create-pr`, `check-ci`, `tag-release`）の配置
- [x] `docs/`: `ROADMAP.md`, `RELEASE.md`, `issues/` 運用環境の構築
- [x] `.github/pull_request_template.md`: 統一 PR テンプレートの配置

---

## 🛠️ 設計方針・技術的メモ

- `IntervalTimer` の成功パターンを踏襲しつつ、本リポジトリ（GitHub Composite Actions & Python）の特性に合致した規約とスキル構成に調整する。
- バージョニング運用として、Composite Action の呼び出しで一般的なメジャーバインディング（`@v1`）およびパッチタグ（`@v1.0.0`）を管理する `tag-release` スキルを用意する。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] Git hooks の動作確認
- [x] CI（GitHub Actions）の通過

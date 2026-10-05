# Issue #001: 汎用的な 3 つの Android 用 Composite Action の作成

- **ステータス**: 完了
- **作成日**: 2026-10-05
- **対象ブランチ**: `feature/initial-composite-actions`

---

## 🎯 目的 / 概要

Android アプリケーション（IntervalTimer 等）のリリースパイプラインで共通利用可能な 3 つの Composite Action（`setup-keystore`, `promote-play`, `publish-release`）およびテスト・ドキュメントを作成し、CI/CD を共通化・効率化する。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `setup-keystore/action.yml`: Base64 署名キーストアのバリデーション・デコード・配置
- [x] `promote-play/action.yml` & `scripts/promote_track.py`: Google Play トラック昇格（二重防止ガード・Dry-run・段階公開対応）
- [x] `publish-release/action.yml`: GitHub Releases の作成・ドラフト公開・アセット添付・Pre-release/Full Release 切替
- [x] 各 Action の `README.md` およびルート `README.md`（実践ワークフロー例付き）
- [x] Python 単体テスト（`test_promote_track.py`）および CI（`.github/workflows/ci.yml`）の通過

---

## 🛠️ 設計方針・技術的メモ

- GitHub Composite Action (`using: composite`) として構築し、呼び出し側リポジトリでワンライナーで利用可能とする。
- `promote-play` スクリプトは `${{ github.action_path }}` を参照して Action 側に同梱し、呼び出し元にスクリプトを配置不要にする。
- Windows 環境の cp932 文字コード問題に配慮し、ログプレフィックスはプレーンなブラケット形式を採用。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] 単体テスト（test_*.py）の作成
- [x] CI（GitHub Actions）の通過
- [x] 各 Action の README.md およびルート README.md の作成

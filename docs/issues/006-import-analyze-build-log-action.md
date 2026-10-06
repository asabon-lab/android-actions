# Issue #006: android-build-log-analyzer の取り込み (analyze-build-log)

- **ステータス**: 進行中
- **作成日**: 2026-10-07
- **対象ブランチ**: `feature/006-import-analyze-build-log-action`

---

## 🎯 目的 / 概要

`android-build-log-analyzer`（旧スタンドアロンリポジトリ / Marketplace 公開Action）を本リポジトリ（`asabon-lab/android-actions`）へ統合・取り込みを行う。
本リポジトリの設計方針（Composite Action + 依存ゼロの Python スクリプト）に沿って再構成し、Android アプリの CI/CD でビルドログ解析・アノテーション・Job Summary 出力を一元的に利用可能にする。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [ ] `analyze-build-log/action.yml` を Composite Action として定義し、以下の入力をサポートすること:
  - `log-file-path` (必須): 解析対象のビルドログファイルパス
  - `report-path` (任意): 解析レポート (Markdown) の出力先ファイルパス
- [ ] `analyze-build-log/scripts/analyze_build_log.py` を実装し、以下を満たすこと:
  - Python 標準ライブラリのみで動作し、外部依存を持たないこと
  - ビルド時間の抽出およびタスク実行状態（Executed, Cached/Up-to-date, Skipped）の集計
  - エラー・警告の正規表現検出（`e:`, `w:`, `Error:`, `Warning:` 等）および行番号グルーピング
  - Gradle の既知の非推奨警告（Kover, AGP 関連の Project object dependency notation）の検知・分類
  - GitHub Workflow Commands によるアノテーション出力（`::error::`, `::warning::`）
  - GitHub Step Summary（`$GITHUB_STEP_SUMMARY`）へのレポート追記
  - エラー検出時に非 0 終了コードで失敗すること
  - Windows 環境（cp932）でもエラーとならない UTF-8 出力配慮
- [ ] `analyze-build-log/scripts/test_analyze_build_log.py` を作成し、旧リポジトリと同等以上のケースをカバーする単体テスト（`unittest`）が全件パスすること
- [ ] `.github/workflows/ci.yml` に `analyze-build-log` の単体テスト実行および Action 動作検証を追加すること
- [ ] `analyze-build-log/README.md` およびルートの `README.md` を更新すること

---

## 🛠️ 設計方針・技術的メモ

- **言語・設計**:
  - 旧リポジトリの Node.js / TypeScript 実装から、本リポジトリの共通基盤である Python（標準ライブラリのみ）+ Composite Action に移行する（案 A）。
  - `npm`, `dist/`, `node_modules` のビルド・コミット管理が不要となり、ランタイム警告（Node 20 非推奨問題など）も回避できる。
- **Action 仕様**:
  - 入力: `log-file-path` (required: true), `report-path` (required: false, default: '')
  - 出力・副作用: GitHub アノテーション発行、`$GITHUB_STEP_SUMMARY` への Markdown 出力、エラー時プロセス終了。
- **CI**:
  - `ci.yml` の test ジョブで `python -m unittest discover -s analyze-build-log/scripts -p "test_*.py"` を実行。
  - テスト用のダミービルドログを用いたローカル Composite Action の実動作ステップも CI に追加。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・更新
- [ ] 単体テスト（test_*.py）の作成または更新
- [ ] Action / ワークフロー構文の確認
- [ ] ローカルテスト・CI（GitHub Actions）の通過
- [ ] 各 Action の README.md およびルート README.md の更新（該当する場合）

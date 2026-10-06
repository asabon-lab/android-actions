# Issue #005: ワークフロー例の samples/ 分離と README のリンク化

- **ステータス**: 進行中
- **作成日**: 2026-10-07
- **対象ブランチ**: `docs/005-extract-samples-and-link-readme`

---

## 🎯 目的 / 概要

現在 `README.md` に直接埋め込まれている実践ワークフロー例（`release.yml` および `promote-production.yml`）を `samples/` ディレクトリ配下に独立した YAML ファイルとして切り出す。
これにより、以下を実現する：
1. `README.md` の可読性と一覧性を大幅に向上（要点スニペットとリンクに集約）。
2. 利用者がサンプルワークフローをファイル単位で直接参照・コピー・流用しやすくする。
3. エディタや Linter による YAML 構文検証を容易にする。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [ ] `samples/release.yml` を作成し、リリースビルド & 内部テスト配布ワークフローを配置する。
- [ ] `samples/promote-production.yml` を作成し、本番昇格ワークフローを配置する。
- [ ] `README.md` の「クイックスタート：実践ワークフロー例」を案A（コアステップの要約スニペット ＋ `samples/` へのリンク）にリファクタリングする。
- [ ] `samples/` 内の YAML 構文が正常であり、リポジトリ内のリンク切れがないこと。

---

## 🛠️ 設計方針・技術的メモ

- `samples/` ディレクトリを新設し、以下のファイルを配置：
  - `samples/release.yml`
  - `samples/promote-production.yml`
- 各サンプルファイル冒頭に、用途や前提条件のコメントを付与。
- `README.md` 側は、全体の流れを把握しやすい最小限のハイライトスニペットに絞り、`[samples/release.yml](samples/release.yml)` への相対リンクを明記する。

---

## ✅ 完了チェックリスト

- [ ] 受け入れ基準を満たす実装・更新
- [ ] 単体テスト（test_*.py）の実行（既存機能に影響がないことの確認）
- [ ] Action / ワークフロー構文の確認
- [ ] ローカルテスト・CI（GitHub Actions）の通過
- [ ] 各 Action の README.md およびルート README.md の更新（該当する場合）

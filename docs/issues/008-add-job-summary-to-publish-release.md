# Issue #008: publish-release に Job Summary 出力機能を追加（折りたたみ式リリースノート対応）

- **ステータス**: 完了
- **作成日**: 2026-10-08
- **対象ブランチ**: `feature/008-add-job-summary-to-publish-release`

---

## 🎯 目的 / 概要

`publish-release` Action の実行完了時に、GitHub Actions の Job Summary（`$GITHUB_STEP_SUMMARY`）へリリース情報、アップロードされた成果物（Assets）一覧、および `<details>` タグを用いた折りたたみ形式のリリースノートを出力する機能を追加する。
これにより、Actions 画面から直接ワンクリックで作成された GitHub Release を確認でき、画面を縦長に圧迫することなくリリースノートの内容も確認できるようにする。

---

## 📋 要件 / 受け入れ基準 (Acceptance Criteria)

- [x] `GITHUB_STEP_SUMMARY` 環境変数が存在する場合に Job Summary へ Markdown を出力すること
- [x] 見出しレベルが `###` から開始され、サードパーティ製 Action と統一感があること
- [x] 確定情報テーブルを出力すること:
  - リリースタイトルおよびリンク（`[Title](URL)`）
  - タグ名（`Tag`）
  - リリース種別（Full Release / Pre-release / Draft、Latest Release 表示）
- [x] アップロードされた成果物（Assets）の一覧およびファイル数を出力すること
- [x] リリースノート（Release Body）が存在する場合、`<details><summary><b>📝 Release Notes (クリックで展開)</b></summary> ... </details>` の折りたたみ形式で出力すること
- [x] 各 Action の README.md （`publish-release/README.md`）に本機能の記述を追加すること

---

## 🛠️ 設計方針・技術的メモ

- `gh release view "$TAG_NAME" --json url,id,name,tagName,isDraft,isPrerelease,assets,body` を利用してリリース情報を取得。
- jq または bash 文字列操作により Summary 用 Markdown を組み立て。
- POSIX 準拠の bash で記述し、Windows/Linux ランナーでの動作を保証。

---

## ✅ 完了チェックリスト

- [x] 受け入れ基準を満たす実装・更新
- [x] Action 構文の確認
- [x] 各 Action の README.md およびドキュメントの更新
- [x] ローカル検証・CI（GitHub Actions）の通過

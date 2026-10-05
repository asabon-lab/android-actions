---
name: create-pr
description: >-
  Create a standardized GitHub Pull Request using GitHub CLI (gh pr create)
  based on .github/pull_request_template.md and current branch diff.
---

# GitHub Pull Request 作成スキル (create-pr)

トピックブランチでの作業完了時に、統一フォーマットで GitHub Pull Request を作成・発行するためのスキルです。

## 前提条件
- 現在の作業がすべてコミットされており、リモートブランチへ push されていること。
- `gh auth status` で GitHub CLI が認証済みであること。

## 手順

1. **ブランチとコミット履歴の確認**
   - 対象ブランチ、ベースブランチ（通常 `main`）、コミットを確認。
   ```bash
   git log origin/main..HEAD --oneline
   ```

2. **PR タイトルと本文の構成**
   - タイトル形式: `[接頭辞] Issue #XXX: 概要`
     - 例: `[Feature] Issue #001: 汎用的な 3 つの Composite Action の作成`
     - 例: `[Chore] Issue #002: AI ハーネス開発環境の整備`
   - 本文形式: `.github/pull_request_template.md` の項目（概要、関連 Issue、変更内容、確認項目、備考）に沿って一時ファイル `scratch/pr_body.md` に書き出し。
   - ※ シェルのエスケープ崩れを防ぐため、`--body` による直接指定は禁止し、必ず `--body-file` を使用する。
   - ※ 一時ファイルは必ず `.gitignore` 済みの `scratch/` ディレクトリ配下に作成する。

3. **PR 作成コマンドの実行**
   ```bash
   gh pr create --title "[接頭辞] Issue #XXX: タイトル" --body-file "scratch/pr_body.md" --base main
   ```
   - PR 発行後、`scratch/pr_body.md` は削除して作業領域をクリーンに保つ。

4. **結果の報告**
   - 作成された PR の URL と概要をユーザーに提示し、レビュー・マージを依頼する。

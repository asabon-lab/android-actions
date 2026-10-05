---
name: create-issue
description: >-
  Create a new Issue markdown file under docs/issues/ and switch to a corresponding
  topic branch (<type>/<number>-<summary>) following the standard workflow.
---

# Issue 起票 & ブランチ作成スキル (create-issue)

新機能追加、バグ修正、リファクタリング、ドキュメント更新、CI保守など、**作業を開始する際に必ず実行するスキル**です。

## 手順

1. **既存 Issue の確認と採番**
   - `docs/issues/` 配下のファイル一覧を確認し、最大の3桁連番を特定して次の番号を決定（例: `002` の次は `003`）。
   ```bash
   Get-ChildItem docs/issues/*.md
   ```

2. **Issue ファイルの作成**
   - [`docs/issues/TEMPLATE.md`](docs/issues/TEMPLATE.md) をコピーして `docs/issues/<3桁番号>-<概要>.md` を作成。
   - タイトル、目的、受け入れ基準（Acceptance Criteria）、設計メモを記述。
   - ステータスを `進行中` に設定。

3. **トピックブランチの作成と切り替え**
   - タイプを選択（`feature`, `fix`, `refactor`, `docs`, `chore`, `test`）。
   - `main` ブランチが最新であることを確認の上、ブランチを作成・切り替え。
   ```bash
   git switch main
   git pull origin main
   git switch -c <タイプ>/<3桁番号>-<概要>
   ```

4. **Issue ファイルのコミット**
   - 作成した Issue ファイルをブランチの初期コミットとして追加。
   ```bash
   git add docs/issues/<3桁番号>-<概要>.md
   git commit -m "docs: Issue #<3桁番号> <タイトル> 起票"
   ```

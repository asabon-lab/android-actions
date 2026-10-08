---
name: sync-harness
description: >-
  Compare and sync AI harness configurations (.agents/, rules, skills, AGENTS.md,
  githooks, templates) from another local repository safely following standard workflows.
---

# ハーネス環境同期スキル (sync-harness)

ローカルの他リポジトリ（例: `IntervalTimer` 等）との間で、AI ハーネス環境（運用規約、ルール、スキル、テンプレート等）の差分を走査・選別し、現在のプロジェクトへ安全に取り込むための手順書です。

---

## 🎯 目的

- 他リポジトリで先行して洗練されたルールやスキル等の知見を、抜け漏れなくスムーズに取り込む。
- プロジェクト固有設定（言語・ビルドツール・環境依存パス等）の誤った混入・上書きを未然に防止する。
- 必ずユーザーとの事前すり合わせと Issue 駆動開発フロー（Issue 起票 → トピックブランチ → PR）を経て反映する。

---

## 🛡️ プロジェクト固有設定の除外ガード（最重要）

他リポジトリから取り込む際、**以下のプロジェクト固有設定は絶対に機械的に同期・上書きしてはならない**:

1. **ビルドツール・言語・Linter 固有の設定**:
   - Android / Kotlin / Gradle / ktlint 固有の設定（`gradle.properties`, `build.gradle.kts` 等）
   - Python / uv / ruff / pytest 固有の設定
2. **環境隔離・ホスト依存設定**:
   - `gradle.properties` の環境固有パス禁止ルール（Android 特有）
   - 各プロジェクト固有の Secrets / トークン規約
3. **リポジトリ固有の履歴・ドキュメント**:
   - `docs/issues/` の過去 Issue ファイル
   - `docs/ROADMAP.md` の機能ロードマップ（ハーネス項目以外のプロジェクト固有内容）
   - ブランチ命名規則の具体例（各リポジトリのドメイン名）
4. **先祖返り（デグレード）防止ガード（手元が新しい場合の保護）**:
   - スキャナーで `Target (Newer [CAUTION])` と判定された項目（手元のコミット日時の方が新しい場合）は、**相手側の内容で機械的に上書きしてはならない**。
   - 相手側のコミットログ（`git -C <同期元パス> log -1 <ファイル>`）を確認し、手元にない純粋な追加改善がある場合のみ「手元の最新状態に相手の追加分をマージ（追記）」する。手元で先行して実装された最新ルールを相手の古い版で消去することは厳禁。

---

## 📋 実行手順

### 1. 同期元リポジトリのパス指定とスキャン

ユーザーから同期元リポジトリのパス（例: `e:\work\IntervalTimer` や `../IntervalTimer`）を受け取り、同梱の差分スキャナースクリプトを実行してハーネス全体の差分および新旧関係（Git コミット日時）を把握します。

```powershell
& .\.agents\skills\sync-harness\scripts\diff-harness.ps1 "<同期元リポジトリの絶対パス>"
```

- **判定結果の確認**:
  - `Source (Update [CANDIDATE])`: 相手側の方が新しく更新されているため、優先的な取り込み候補。
  - `Target (Newer [CAUTION])`: 手元の方が新しい状態。相手側の古い版による上書き（先祖返り）を警戒。
  - `Source Only`: 相手側にのみ存在する新規ファイル（取り込み候補）。

### 2. 差分のあるファイルの詳細確認

スキャナーで差分が検出された項目について、`git diff --no-index` を使用して内容の差分を確認します。

```bash
# 例: AGENTS.md の差分確認
git diff --no-index AGENTS.md "<同期元パス>/AGENTS.md"

# 例: ルールやスキルの差分確認
git diff --no-index .agents/skills/check-ci/SKILL.md "<同期元パス>/.agents/skills/check-ci/SKILL.md"
```

### 3. 取り込み提案とユーザー合意

差分のうち、現在のプロジェクトに取り込む価値のある「汎用ルール」「スキルの機能改善」「テンプレートの改善」等を抽出し、一覧表形式でユーザーに提案・相談します。
手元の方が新しい項目（`Target (Newer [CAUTION])`）については、相手側の記述が古い版に戻すものでないかを明記して安全性を提示します。

- **提案フォーマット**:
  - 分類（ブランチ規約、CI監視、一時ファイル運用等）
  - 対象ファイル
  - 新旧ステータス（Source Newer / Target Newer）
  - 取り込む内容とメリット
- ユーザーから「進めてください」等の合意を得るまで、実際のコード・設定変更には着手しない。

### 4. Issue 起票 & トピックブランチ作成

合意が得られたら、標準の Issue 駆動開発フローに従って着手します：

```bash
# 1. create-issue スキルに従い docs/issues/ に Issue 起票
# 2. chore ブランチの作成・切り替え
git switch main
git pull origin main
git switch -c chore/<3桁番号>-sync-ai-harness-from-<同期元名>

# 3. Issue ファイルの初期コミット
git add docs/issues/<3桁番号>-*.md
git commit -m "Issue #<3桁番号>: <タイトル> を起票"
```

### 5. 適用・検証・Pull Request 発行

1. ファイルの修正・適用（プロジェクト固有の整合性を保ちながら適用）。
2. プロジェクトの品質チェックを実行（例: `uv run ruff check .` や Python 単体テスト）。
3. 論理単位で日本語コミットを作成。
4. Issue ファイルの受け入れ基準チェックを完了に更新してコミット。
5. リモートへ push し、`create-pr` スキルに従い PR を発行：
   ```bash
   # scratch/pr_body.md を作成して実行
   gh pr create --title "[Chore] Issue #<3桁番号>: <タイトル>" --body-file "scratch/pr_body.md" --label "chore" --base main
   # 発行後、scratch/pr_body.md を削除
   Remove-Item scratch/pr_body.md
   ```

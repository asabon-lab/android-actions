# AGENTS.md - android-actions 開発ガイドライン

本ドキュメントは、本リポジトリ（`asabon-lab/android-actions`）における AI エージェントおよび開発者の行動指針、開発規約、Git 運用ルール、および品質基準を定義するものです。

---

## 1. プロジェクト概要 & 基本方針

本リポジトリは、Android アプリケーション（`IntervalTimer` 等）の CI/CD（ビルド・署名・Google Play 配布・GitHub Releases 管理）を共通化・再利用可能にするための **GitHub Composite Actions** 集です。

### 提供するコア Actions
1. **`setup-keystore/`**: Base64 署名キーストアのデコード・安全なファイル配置
2. **`promote-play/`**: Google Play Developer API によるトラック間リリース昇格（二重防止ガード・Dry-run・段階公開対応）
3. **`publish-release/`**: GitHub Releases 作成・Release Drafter 下書き昇格・アセット添付・Pre-release/Full Release 切替
4. **`analyze-build-log/`**: Android ビルドログの解析・エラー/警告アノテーション・Job Summary レポート出力

### コア設計哲学
- **疎結合 & 高凝集**: 各 Action は単一の明確な責務を持ち、他リポジトリから個別に参照可能とする。
- **ゼロ外部スクリプト依存（呼び出し側視点）**: 必要なスクリプト（Python 等）は Action 内部（`${{ github.action_path }}`）に内包し、呼び出し側リポジトリに余計なファイルを配置させない。
- **安全第一のガード機構**: 二重リリース防止ガードや入力バリデーションなど、本番障害を防ぐ仕組みを標準搭載する。

---

## 2. 開発規約 & 品質基準

### Composite Action 実装規約
- **シェル指定の徹底**: 各ステップに必ず `shell: bash` を指定し、POSIX 準拠で Linux / macOS / Windows runner のいずれでも一貫して動作するように記述する。
- **Inputs & Outputs の定義**: すべての入力パラメータには明確な `description`、適切な `required`、`default` を定義し、後続ステップで参照可能な情報は `outputs` として公開する。
- **クォーティング & パス**: 変数展開時は常にダブルクォート（`"$VAR"`）を使用し、パス区切りには `/` を使用する。

### Python スクリプト規約 (`promote-play/scripts/` 等)
- **依存関係の最小化**: 必要最小限の公式クライアント（`google-api-python-client`, `google-auth` 等）のみを使用する。
- **クロスプラットフォーム配慮**: Windows 環境（cp932）での `UnicodeEncodeError` を防ぐため、コンソール出力には装飾絵文字ではなくプレーンなテキストプレフィックス（`[INFO]`, `[SUCCESS]`, `[GUARD]` など）を使用し、`sys.stdout.reconfigure(encoding="utf-8")` を配慮する。
- **単体テストの必須化**: スクリプトのロジック（引数パース、ガード条件、dry-run、API 呼び出し）は、外部 API をモックした単体テスト（`test_*.py`）を必ず作成し、`python -m unittest` で全件パスすることを保証する。

### CI（GitHub Actions）との連携
- プルリクエスト作成時および `main` ブランチ push 時に `.github/workflows/ci.yml` が自動実行され、以下を検証する：
  1. Python スクリプトの単体テスト実行
  2. `setup-keystore` などのローカル Composite Action の実動作テスト

### GitHub Actions CI & 警告（Warnings/Annotations）監視ルール
GitHub Actions による CI 実行結果を確認する際は、単にジョブの「成功・失敗（Success / Failure）」を見るだけでなく、**警告（Annotations, Deprecation Warnings, Runner Notices）の有無を必ず確認し、迅速に対応・解消する**こと。

1. **警告の確認方法**:
   - `gh pr checks` や `gh run view <RUN_ID>` の出力において、`ANNOTATIONS` や `Warning:`、非推奨メッセージの有無を確認する（`.agents/skills/check-ci/` の活用）。
2. **対象となる警告の例**:
   - ランタイムや Action の非推奨警告（例: `Node.js 20 is deprecated... forced to run on Node.js 24`, `actions/checkout` や `setup-python` 等の最新バージョンへのアップグレード）。
   - パッケージやツールの非推奨警告、依存関係の脆弱性通知。
   - OS ランナー環境の移行予告（例: Ubuntu runner バージョン更新）。
3. **対応指針**:
   - 非推奨（Deprecation）や設定不備による警告は放置せず、速やかに修正コミットを作成して解消する。
   - プラットフォーム全体の移行予告についても、影響有無を調査してユーザーに報告・提案する。

---

## 3. Git / GitHub ワークフロー & コミット規約

### ブランチ戦略 (GitHub Flow)
- **`main` ブランチ**: 常に安定し、リリース可能な状態を維持する。**直接の `commit` および `push` は禁止**。
- **トピックブランチ**: 作業目的に応じたプレフィックスを付け、`<タイプ>/<3桁のIssue番号>-<概要>` の形式で作成する（例: `feature/001-setup-keystore`）。

| プレフィックス | 用途・選択基準 | 例 |
| :--- | :--- | :--- |
| **`feature/`** | 新しい Action の追加や新機能の実装 | `feature/003-setup-android-sdk` |
| **`fix/`** | バグや不具合の修正 | `fix/004-play-track-pagination` |
| **`refactor/`** | 仕様を変えない構造改善・リファクタリング | `refactor/005-streamline-scripts` |
| **`docs/`** | ドキュメント（README, ROADMAP, 設計書）の追加・修正 | `docs/006-update-usage-examples` |
| **`chore/`** | CI設定・依存関係・開発環境・フック等の保守 | `chore/002-setup-ai-harness` |
| **`test/`** | 単体テストや検証ワークフローの追加・更新 | `test/007-add-release-tests` |

### Git Hooks による誤操作防止
- 本リポジトリでは `.githooks/` 配下に `pre-commit` および `pre-push` を用意し、`main` への直接コミット・プッシュをブロックする。
- 設定コマンド: `git config core.hooksPath .githooks`

### プルリクエスト (PR) 運用
- すべての変更は GitHub 上で Pull Request を作成し、レビュー・検証（CI All Green）後に `main` へマージする。
- PR 作成時は [`.github/pull_request_template.md`](.github/pull_request_template.md) のフォーマットを適用し、タイトルは `[接頭辞] Issue #XXX: 概要` とする。
- PR 発行には GitHub CLI (`gh pr create`) または `.agents/skills/create-pr/` スキルを活用する。

### コミット単位 & メッセージ
- 1つの論理的な変更ごとに小さな単位でコミットする。
- コミットメッセージは **日本語** で、変更内容が明確にわかるように記述する（例: `feat: promote-play に段階的ロールアウト引数を追加`, `docs: README に release.yml の連携例を追記`）。

---

## 4. Issue 駆動ワークフロー (`docs/issues/`)

すべての変更（新 Action 追加、バグ修正、リファクタリング、ドキュメント更新、CI 保守）において、**例外なく以下のステップに従って作業を進める**。

### 標準作業フロー（5ステップ）
1. **Issue の起票**:
   - 作業開始前に必ず `docs/issues/<3桁番号>-<概要>.md` を作成（例: `002-setup-ai-harness.md`）。
   - ひな型として [`docs/issues/TEMPLATE.md`](docs/issues/TEMPLATE.md) を使用し、目的と受け入れ基準（Acceptance Criteria）を明記する。
   - ※ Issue 作成には `.agents/skills/create-issue/` スキルを活用する。
2. **トピックブランチの作成**:
   - 起票した Issue 番号に基づき、`<タイプ>/<3桁番号>-<概要>` のブランチを作成して切り替える。
3. **実装 & 単体コミット**:
   - 定義した受け入れ基準を満たす実装・テストを行い、小さな単位でコミットする。
4. **受け入れ基準の検証と Issue 更新**:
   - 動作確認を行い、Issue ファイルの受け入れ基準チェックボックスを埋め、ステータスを `完了` に更新してコミットする。
   - 関連する [`docs/ROADMAP.md`](docs/ROADMAP.md) のチェック項目も併せて更新する。
5. **Pull Request (PR) の発行**:
   - リモートへ push し、`.agents/skills/create-pr/` スキルまたは `gh pr create` を使用して PR を発行する。

---

## 5. バージョニング & リリース運用 (`docs/RELEASE.md`)

- 本リポジトリの Composite Action はセマンティックバージョニング（`vX.Y.Z`）およびメジャーフローティングタグ（`v1`）で管理する。
- PR が `main` にマージされた後、ユーザーの指示に基づき `.agents/skills/tag-release/` スキルを実行してタグを発行・更新する。

---

## 6. 主要コマンドチートシート

```bash
# Git Hooks の有効化
git config core.hooksPath .githooks

# Python 単体テストの実行
python -m unittest discover -s promote-play/scripts -p "test_*.py"

# GitHub Actions CI 状況の確認
gh run list --limit 5
gh run view <RUN_ID>
gh run view <RUN_ID> --log-failed

# PR 作成（本文は必ず scratch/pr_body.md 経由で指定）
gh pr create --title "[Chore] Issue #002: AI ハーネス開発環境の整備" --body-file "scratch/pr_body.md" --base main
```

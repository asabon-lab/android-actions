# publish-release

GitHub Releases の作成・ドラフト公開・アセット添付・ステータス更新（Pre-release から Full Release への昇格など）を統一的に処理する GitHub Composite Action です。

## 特長

- **Release Drafter との協調**: リポジトリ内に未公開のドラフトが存在する場合、そのドラフトのリリースノート（自動生成されたチェンジログ）を維持したまま、指定のタグ名で公開（Pre-release または Full Release）へ昇格。
- **柔軟なライフサイクル管理**:
  - 新規作成（`gh release create`）
  - 既存リリースのプロパティ更新（`gh release edit`）
  - Pre-release（`prerelease: true`）から本番 Full Release（`prerelease: false` & `make-latest: true`）への昇格
- **アセットの一括アップロード**: ワイルドカード（glob パターン）でビルド成果物（`.aab` や `.apk` 等）を指定して一括アップロード（`--clobber` で上書き対応）。
- **`make-latest` のスマート自動判定**: `auto`（デフォルト）の場合、Full Release（draft=false かつ prerelease=false）なら自動的に Latest に設定し、Pre-release や Draft なら Latest フラグを外します。
- **リッチな Job Summary レポート**: リリース完了時に GitHub Actions の Job Summary（`$GITHUB_STEP_SUMMARY`）へリリース情報、アップロードされたアセット一覧、および `<details>` による折りたたみ形式のリリースノートを自動出力。

## Inputs

| パラメータ名 | 必須 | デフォルト値 | 説明 |
|---|:---:|---|---|
| `tag-name` | **はい** | - | リリースタグ名（例: `v1.2.0`, `${{ github.ref_name }}`） |
| `release-title` | いいえ | *(tag-name と同一)* | リリースのタイトル |
| `prerelease` | いいえ | `false` | Pre-release として公開する場合は `true` |
| `draft` | いいえ | `false` | 下書き（Draft）として保持する場合は `true` |
| `make-latest` | いいえ | `auto` | 最新リリース（Latest）とするか（`true`, `false`, `legacy`, `auto`） |
| `generate-notes` | いいえ | `true` | 新規作成時に GitHub の自動リリースノート生成を利用するか |
| `artifacts` | いいえ | `''` | アップロードするファイルの glob パターン（例: `release-artifacts/*`） |
| `update-existing-draft` | いいえ | `true` | 既存ドラフトが存在する場合にそれを更新・公開するか |
| `github-token` | いいえ | `${{ github.token }}` | GitHub トークン（`contents: write` 権限が必要） |

## Outputs

| パラメータ名 | 説明 |
|---|---|
| `release-url` | 作成・更新された GitHub Release の URL |
| `release-id` | GitHub Release の ID |
| `tag-name` | 対象のタグ名 |

## 使用例

### 1. タグ push 時の Pre-release 公開 & AAB 添付（CI/CD リリース）

```yaml
- name: Publish Pre-release
  uses: asabon-lab/android-actions/publish-release@v1
  with:
    tag-name: ${{ github.ref_name }}
    prerelease: true
    artifacts: release-artifacts/*
```

### 2. 本番昇格ワークフローでの Full Release 化（Latest に設定）

```yaml
- name: Finalize Full Release
  uses: asabon-lab/android-actions/publish-release@v1
  with:
    tag-name: ${{ inputs.tag_name }}
    prerelease: false
    make-latest: true
```

# promote-play

Google Play Developer API を使用して、テストトラック（例: `internal`）のリリースを別トラック（例: `production` 本番）へワンストップで昇格（Promote）させる GitHub Composite Action です。

## 特長

- **柔軟なトラック間昇格**: `internal` から `production` への昇格はもちろん、`alpha` や `beta` への昇格、特定 `versionCode` の指定昇格に対応。
- **二重リリース防止ガード**: 昇格対象の `versionCode` がすでに昇格先端トラックに存在する場合は、自動でガード（終了コード 2）を発動して重複更新を防止。
- **段階的公開（Staged Rollout）対応**: `status: inProgress` と `user-fraction` を指定することで、10% や 20% などの段階的ロールアウトが可能。
- **Dry-run シミュレーション**: 実際に Google Play Console 側にコミットすることなく動作確認が可能。
- **スクリプト同梱**: 呼び出し元リポジトリ側に Python スクリプトを用意する必要はありません。

## Inputs

| パラメータ名 | 必須 | デフォルト値 | 説明 |
|---|:---:|---|---|
| `package-name` | **はい** | - | 対象アプリのパッケージ名（例: `net.asabon.intervaltimer`） |
| `service-account-json` | **はい** | - | Google Play Console のサービスアカウント JSON 文字列またはファイルパス |
| `source-track` | いいえ | `internal` | 昇格元のトラック名 |
| `target-track` | いいえ | `production` | 昇格先のトラック名 |
| `version-code` | いいえ | *(最新)* | 昇格させる特定の versionCode（省略時は元トラックの最新） |
| `status` | いいえ | `completed` | 昇格先トラックのリリース状態（`completed`, `inProgress`, `draft`, `halted`） |
| `user-fraction` | いいえ | - | 段階的公開の割合（例: `0.1` で 10%）。`status: inProgress` 時に有効 |
| `dry-run` | いいえ | `false` | コミットを行わずにシミュレーション実行する場合は `true` |
| `python-version` | いいえ | `3.11` | 使用する Python バージョン |

## Outputs

| パラメータ名 | 説明 |
|---|---|
| `promoted-version-code` | 昇格されたリリースの versionCode |
| `edit-id` | Google Play Console の application edit ID |

## 使用例

### 1. Internal テストから本番（Production）への標準プロモーション

```yaml
- name: Promote to Production
  uses: asabon-lab/android-actions/promote-play@v1
  with:
    package-name: net.asabon.intervaltimer
    service-account-json: ${{ secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON }}
    source-track: internal
    target-track: production
```

### 2. Dry-run 付きの workflow_dispatch 連携

```yaml
- name: Promote to Production (with Dry-run support)
  uses: asabon-lab/android-actions/promote-play@v1
  with:
    package-name: net.asabon.intervaltimer
    service-account-json: ${{ secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON }}
    dry-run: ${{ inputs.dry_run }}
```

### 3. 段階的ロールアウト（20% 配信）

```yaml
- name: Staged Rollout to Production (20%)
  uses: asabon-lab/android-actions/promote-play@v1
  with:
    package-name: net.asabon.intervaltimer
    service-account-json: ${{ secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON }}
    target-track: production
    status: inProgress
    user-fraction: 0.2
```

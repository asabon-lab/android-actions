# analyze-build-log

Android のビルドログ（Gradle ログ等）を解析し、エラー・警告のアノテーション表示、既知の非推奨警告の分類、およびビルドパフォーマンスサマリーを GitHub Actions の Job Summary（`$GITHUB_STEP_SUMMARY`）や Markdown ファイルへ出力する GitHub Composite Action です。

## 特長

- **GitHub UI との連携**: 検出されたコンパイルエラーや警告を GitHub Workflow Commands（`::error::`, `::warning::`）として出力し、PR の該当行やログにアノテーション表示。
- **リッチなサマリーレポート**: 総ビルド時間やタスク実行状況（Executed, Cached/Up-to-Date, Skipped）の集計表、エラー/警告一覧を Job Summary に自動表示。
- **誤検知防止 & 既知の非推奨警告分類**: Gradle の Welcome メッセージ等の誤検知を防ぎ、`kotlinx-kover` や `Android Gradle Plugin` に起因する既知の非推奨警告（Project dependency notation）を個別枠で分かりやすく解説。
- **外部依存ゼロ**: Python 標準ライブラリのみで動作し、追加パッケージのインストールが不要。
- **エラー時ガード**: ビルドログ内にエラー（`e:`, `Error:` 等）が検出された場合、ステップを自動的に失敗（exit code 1）させてパイプラインに通知。

## Inputs

| パラメータ名 | 必須 | デフォルト値 | 説明 |
|---|:---:|---|---|
| `log-file-path` | **はい** | - | 解析対象の Android ビルドログファイルパス |
| `report-path` | いいえ | `""` | 解析レポート（Markdown）を保存するファイルパス（任意） |

## Outputs

| パラメータ名 | 説明 |
|---|---|
| `report-path` | 生成されたレポートファイルのパス（指定された場合） |
| `error-count` | 検出されたビルドエラーの件数 |
| `warning-count` | 検出された警告の件数 |

## 使用例

```yaml
- name: Build with Gradle
  run: ./gradlew assembleDebug --stacktrace | tee build.log

- name: Analyze Build Log
  uses: asabon-lab/android-actions/analyze-build-log@v1
  if: always() # ビルドが失敗した場合でもログ解析を実行
  with:
    log-file-path: build.log
    report-path: build-report.md
```

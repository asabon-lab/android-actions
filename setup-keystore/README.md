# setup-keystore

Base64 エンコードされた Android リリース用キーストア（JKS）をデコードし、指定のファイルパスへ安全に配置する GitHub Composite Action です。

## 特長

- **自動バリデーション**: Secret が未設定または空文字の場合に分かりやすいエラーメッセージを出力。
- **自動ディレクトリ生成**: 指定した保存先パスの親ディレクトリ（`mkdir -p`）を自動作成。
- **生成後サイズ確認**: デコード結果が空ファイルでないかを検証。
- **ファイルパスの出力**: 後続のビルドステップ（Gradle 等）で参照可能な output を提供。

## Inputs

| パラメータ名 | 必須 | デフォルト値 | 説明 |
|---|:---:|---|---|
| `keystore-base64` | **はい** | - | Base64 エンコードされた Keystore ファイル文字列（例: `${{ secrets.KEYSTORE_BASE64 }}`） |
| `keystore-path` | いいえ | `keystore/release.jks` | デコードしたキーストアの書き込み先相対パス |

## Outputs

| パラメータ名 | 説明 |
|---|---|
| `keystore-path` | 生成されたキーストアファイルのパス |

## 使用例

```yaml
- name: Decode Release Keystore
  id: keystore
  uses: asabon-lab/android-actions/setup-keystore@v1
  with:
    keystore-base64: ${{ secrets.KEYSTORE_BASE64 }}
    keystore-path: keystore/release.jks

- name: Build Release Bundle
  env:
    KEYSTORE_PATH: ${{ steps.keystore.outputs.keystore-path }}
    KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
    KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
    KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
  run: ./gradlew bundleRelease
```

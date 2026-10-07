# Android Actions

[![CI](https://github.com/asabon-lab/android-actions/actions/workflows/ci.yml/badge.svg)](https://github.com/asabon-lab/android-actions/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Android アプリケーションの CI/CD（ビルド・署名・Google Play 配布・GitHub Releases 管理）を効率化・共通化するための GitHub Composite Actions 集です。

## 含まれる Actions

| Action | パス | 説明 |
|---|---|---|
| **[setup-keystore](setup-keystore/README.md)** | `asabon-lab/android-actions/setup-keystore@v1` | Base64 エンコードされた署名用キーストアをデコードし、ファイルとして安全に配置 |
| **[promote-play](promote-play/README.md)** | `asabon-lab/android-actions/promote-play@v1` | Google Play Developer API を用いて、Internal トラックから Production（本番）等へリリースを昇格（二重リリース防止ガード・Dry-run付き） |
| **[publish-release](publish-release/README.md)** | `asabon-lab/android-actions/publish-release@v1` | GitHub Releases のドラフト公開・Pre-release/Full Release 切替・ビルド成果物（AAB/APK）のアップロード |
| **[analyze-build-log](analyze-build-log/README.md)** | `asabon-lab/android-actions/analyze-build-log@v1` | Android ビルドログの解析、エラー/警告のアノテーション、既知の非推奨警告分類、および Job Summary レポート出力 |

---

## クイックスタート：実践ワークフロー例

プロジェクトですぐに利用可能な実践的ワークフロー YAML は、[samples/](samples/) ディレクトリに用意されています。

### 1. リリースビルド & 内部テスト配布 (`.github/workflows/release.yml`)

タグ push（`v*`）時に署名付き Bundle（AAB）をビルドし、Google Play の内部テスト（Internal）トラックへアップロードすると同時に、GitHub Pre-release を作成して成果物を添付します。

> 📄 **完全なワークフローファイル**: [samples/release.yml](samples/release.yml)

```yaml
      # 1. Keystore のセットアップ
      - name: Setup Keystore
        id: keystore
        uses: asabon-lab/android-actions/setup-keystore@v1
        with:
          keystore-base64: ${{ secrets.KEYSTORE_BASE64 }}
          keystore-path: keystore/release.jks

      # 2. リリースビルド (AAB)
      - name: Build Release Bundle
        env:
          KEYSTORE_PATH: ${{ steps.keystore.outputs.keystore-path }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      # 3. GitHub Release (Pre-release) の公開 & AAB アップロード
      - name: Publish GitHub Pre-Release
        uses: asabon-lab/android-actions/publish-release@v1
        with:
          tag-name: ${{ github.ref_name }}
          prerelease: true
          artifacts: release-artifacts/*
```

---

### 2. 本番昇格 (`.github/workflows/promote-production.yml`)

Internal トラックでテスト済みのリリースを Google Play の本番（Production）トラックへ昇格し、GitHub Release を Full Release（Latest）へ更新します。

> 📄 **完全なワークフローファイル**: [samples/promote-production.yml](samples/promote-production.yml)

```yaml
      # 1. Google Play トラック昇格 (Internal -> Production)
      - name: Promote on Google Play
        uses: asabon-lab/android-actions/promote-play@v1
        with:
          package-name: com.example.myapp
          service-account-json: ${{ secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON }}
          source-track: internal
          target-track: production
          dry-run: ${{ inputs.dry_run }}

      # 2. GitHub Release を本番 Full Release (Latest) に昇格
      - name: Finalize GitHub Release
        if: inputs.dry_run != true
        uses: asabon-lab/android-actions/publish-release@v1
        with:
          tag-name: ${{ steps.target.outputs.tag_name }}
          prerelease: false
          make-latest: true
```

---

### 3. PR ビルド & ログ解析 (`.github/workflows/build.yml`)

Pull Request 作成時や push 時に Gradle ビルドを実行し、ビルドエラーや警告を自動的に解析・アノテーション表示します。

> 📄 **完全なワークフローファイル**: [samples/build.yml](samples/build.yml)

```yaml
      # 1. Gradle ビルド（ログをファイルに記録）
      - name: Build with Gradle
        run: ./gradlew assembleDebug --stacktrace | tee build.log

      # 2. ビルドログ解析 & アノテーション・Job Summary 出力
      - name: Analyze Build Log
        uses: asabon-lab/android-actions/analyze-build-log@v1
        if: always() # ビルドが失敗した場合でも実行
        with:
          log-file-path: build.log
          report-path: build-report.md
```

---

## 必要な Repository Secrets

呼び出し元のリポジトリの Settings > Secrets and variables > Actions に以下を設定します。

| Secret 名 | 用途 |
|---|---|
| `KEYSTORE_BASE64` | `base64 release.jks` でエンコードしたキーストアの文字列 |
| `KEY_ALIAS` | キーストアのキーエイリアス |
| `KEYSTORE_PASSWORD` | キーストアのパスワード |
| `KEY_PASSWORD` | キーのパスワード |
| `PLAY_CONSOLE_SERVICE_ACCOUNT_JSON` | Google Play Console API アクセス用のサービスアカウント JSON |

---

## ライセンス

[MIT License](LICENSE)
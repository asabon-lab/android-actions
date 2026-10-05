# Android Actions

Android アプリケーションの CI/CD（ビルド・署名・Google Play 配布・GitHub Releases 管理）を効率化・共通化するための GitHub Composite Actions 集です。

## 含まれる Actions

| Action | パス | 説明 |
|---|---|---|
| **[setup-keystore](setup-keystore/README.md)** | `asabon-lab/android-actions/setup-keystore@v1` | Base64 エンコードされた署名用キーストアをデコードし、ファイルとして安全に配置 |
| **[promote-play](promote-play/README.md)** | `asabon-lab/android-actions/promote-play@v1` | Google Play Developer API を用いて、Internal トラックから Production（本番）等へリリースを昇格（二重リリース防止ガード・Dry-run付き） |
| **[publish-release](publish-release/README.md)** | `asabon-lab/android-actions/publish-release@v1` | GitHub Releases のドラフト公開・Pre-release/Full Release 切替・ビルド成果物（AAB/APK）のアップロード |

---

## クイックスタート：実践ワークフロー例

### 1. リリースビルド & 内部テスト配布 (`.github/workflows/release.yml`)

タグ push（`v*`）時に署名付き Bundle（AAB）をビルドし、Google Play の内部テスト（Internal）トラックへアップロードすると同時に、GitHub Pre-release を作成して成果物を添付します。

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      create_release:
        description: 'Create a GitHub Release draft'
        required: false
        type: boolean
        default: false

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  release:
    name: Build & Release Artifacts
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Set up JDK 17
        uses: actions/setup-java@v5
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v6

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

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

      # 3. 成果物の整理
      - name: Prepare Release Assets
        run: |
          VERSION="${GITHUB_REF_NAME:-latest}"
          mkdir -p release-artifacts
          cp app/build/outputs/bundle/release/*.aab "release-artifacts/MyApp-${VERSION}.aab" || cp app/build/outputs/bundle/release/*.aab release-artifacts/

      # 4. GitHub Release (Pre-release) の公開 & AAB アップロード
      - name: Publish GitHub Pre-Release
        if: startsWith(github.ref, 'refs/tags/') || (github.event_name == 'workflow_dispatch' && inputs.create_release == true)
        uses: asabon-lab/android-actions/publish-release@v1
        with:
          tag-name: ${{ github.ref_name }}
          prerelease: true
          artifacts: release-artifacts/*

      # 5. Google Play (Internal トラック) へのアップロード
      - name: Upload to Google Play (Internal)
        if: (startsWith(github.ref, 'refs/tags/') || (github.event_name == 'workflow_dispatch' && inputs.create_release == true)) && secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON != ''
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON }}
          packageName: com.example.myapp
          releaseFiles: release-artifacts/*.aab
          tracks: internal
          status: completed
          whatsNewDirectory: distribution/whatsnew
```

---

### 2. 本番昇格 (`.github/workflows/promote-production.yml`)

Internal トラックでテスト済みのリリースを Google Play の本番（Production）トラックへ昇格し、GitHub Release を Full Release（Latest）へ更新します。

```yaml
name: Promote to Production

on:
  workflow_dispatch:
    inputs:
      tag_name:
        description: 'Tag name to promote (e.g. v1.2.0). Leave empty for latest pre-release.'
        required: false
        type: string
        default: ''
      dry_run:
        description: 'Simulate promotion without committing changes'
        required: false
        type: boolean
        default: false

concurrency:
  group: promote-production
  cancel-in-progress: false

jobs:
  promote:
    name: Promote Release to Production
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      # 1. 昇格対象タグの決定 & 既存本番重複ガード
      - name: Determine Target Release
        id: target
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INPUT_TAG: ${{ inputs.tag_name }}
        run: |
          TAG_NAME="${INPUT_TAG}"
          if [ -z "$TAG_NAME" ]; then
            echo "🔍 Searching for latest pre-release..."
            TAG_NAME=$(gh api "repos/${{ github.repository }}/releases" --jq '.[] | select(.prerelease == true and .draft == false) | .tag_name' | head -n 1 || true)
          fi

          if [ -z "$TAG_NAME" ]; then
            echo "::error::No pre-release tag found to promote."
            exit 1
          fi

          echo "Target tag: ${TAG_NAME}"

          IS_PRERELEASE=$(gh release view "${TAG_NAME}" --json isPrerelease --jq '.isPrerelease' 2>/dev/null || true)
          if [ "$IS_PRERELEASE" = "false" ]; then
            echo "::error::Release '${TAG_NAME}' is ALREADY marked as full release! Aborting."
            exit 1
          fi

          echo "tag_name=${TAG_NAME}" >> "$GITHUB_OUTPUT"

      # 2. Google Play トラック昇格 (Internal -> Production)
      - name: Promote on Google Play
        uses: asabon-lab/android-actions/promote-play@v1
        with:
          package-name: com.example.myapp
          service-account-json: ${{ secrets.PLAY_CONSOLE_SERVICE_ACCOUNT_JSON }}
          source-track: internal
          target-track: production
          dry-run: ${{ inputs.dry_run }}

      # 3. GitHub Release を本番 Full Release (Latest) に昇格
      - name: Finalize GitHub Release
        if: inputs.dry_run != true
        uses: asabon-lab/android-actions/publish-release@v1
        with:
          tag-name: ${{ steps.target.outputs.tag_name }}
          prerelease: false
          make-latest: true
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
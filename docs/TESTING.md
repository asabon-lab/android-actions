# テスト & 開発ガイド (TESTING.md)

本リポジトリ (`asabon-lab/android-actions`) の各 Composite Action（`promote-play`, `analyze-build-log`, `publish-release`）に含まれる Python スクリプトのローカルテスト手順および開発環境のセットアップガイドです。

---

## 1. 前提条件 & 推奨ツール

- **Python**: 3.10 以上
- **[uv](https://docs.astral.sh/uv/)**（推奨）: 高速な Python パッケージ & プロジェクトマネージャー

> [!TIP]
> `uv` が未インストールの場合は、公式ドキュメントに従ってインストールしてください：
> ```bash
> # Windows (PowerShell)
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
> 
> # macOS / Linux
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

---

## 2. 単体テストの実行 (`uv` 推奨)

リポジトリルートに `pyproject.toml` および `uv.lock` が用意されているため、`uv run` を使用することで仮想環境の構築から依存解決、テスト実行まで手動セットアップ不要で自動かつ高速（数ミリ秒）に行われます。

### 全 Action のテストを一括実行

```bash
uv run python -m unittest discover -s promote-play/scripts -p "test_*.py"
uv run python -m unittest discover -s analyze-build-log/scripts -p "test_*.py"
uv run python -m unittest discover -s publish-release/scripts -p "test_*.py"
```

### Action ごとの個別テスト実行

```bash
# 1. Google Play トラック昇格 (promote-play)
uv run python -m unittest discover -s promote-play/scripts -p "test_*.py"

# 2. ビルドログ解析 (analyze-build-log)
uv run python -m unittest discover -s analyze-build-log/scripts -p "test_*.py"

# 3. GitHub Releases 公開 (publish-release)
uv run python -m unittest discover -s publish-release/scripts -p "test_*.py"
```

---

## 3. 標準 Python (`venv` / `pip`) で実行する場合

`uv` を使用せず、標準の Python 仮想環境で実行する場合の手順です。

```bash
# 1. 仮想環境の作成と有効化
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux (bash/zsh)
source .venv/bin/activate

# 2. 依存関係のインストール
pip install google-api-python-client google-auth

# 3. テストの実行
python -m unittest discover -s promote-play/scripts -p "test_*.py"
python -m unittest discover -s analyze-build-log/scripts -p "test_*.py"
python -m unittest discover -s publish-release/scripts -p "test_*.py"
```

---

## 4. テスト設計方針とモック

各 Action の単体テストは以下の設計方針に従っています：

1. **外部 API への直接通信ゼロ**:
   - Google Play Developer API や GitHub API（`gh` CLI）への通信は、`unittest.mock` によりすべてモック化されています。
   - 外部認証情報（サービスアカウント JSON や GITHUB_TOKEN）がなくても、完全オフラインで安全に実行できます。
2. **高速 & 決定論的**:
   - 全テストスイートが 0.1 秒未満で完了し、環境に依存せず同一の結果を返します。
3. **境界値・ガードロジックの検証**:
   - 二重リリース防止ガード、Dry-run、エラー・警告アノテーション判定、`make-latest: auto` の判定など、障害防止ロジックが網羅されています。

---

## 5. CI（GitHub Actions）との連携

Pull Request 作成時および `main` ブランチ push 時に、[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) が自動実行されます。

- **`Test Python Scripts` ジョブ**: 本ガイドに記載の全単体テストを Ubuntu ランナー上で自動検証します。
- **`Test Composite Actions` ジョブ**: `setup-keystore` などのシェルスクリプトを含む Action の実動作を検証します。

コードを変更した際は、ローカルでテストが全件パスすることを確認した上で PR を作成してください。

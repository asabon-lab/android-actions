# リリースマニュアル (RELEASE.md)

本リポジトリ (`asabon-lab/android-actions`) の Composite Action におけるバージョニング方針とリリース手順です。

---

## 📌 バージョニング方針

本リポジトリで提供する Composite Action は、セマンティックバージョニング（SemVer）および GitHub Actions の標準的なタグ運用に従います。

### 1. タグ形式
- **パッチ/マイナー/メジャー固定タグ**: `v1.0.0`, `v1.1.0`, `v2.0.0`
- **メジャーバージョンのフローティングタグ**: `v1`, `v2`
  - 呼び出し側ワークフローでは通常 `uses: asabon-lab/android-actions/<action>@v1` のようにメジャーバージョンを指定します。
  - 新しい `v1.x.x` をリリースするたびに、`v1` タグの参照先コミットを最新リリースへ移動（上書き）させます。

### 2. バージョンアップの判断基準
- **パッチ更新 (`v1.0.1`)**: バグ修正、ドキュメント修正、内部実装の改善（互換性破壊なし）
- **マイナー更新 (`v1.1.0`)**: 既存の inputs/outputs を維持したまま新機能や新引数の追加（後方互換あり）
- **メジャー更新 (`v2.0.0`)**: 既存の inputs/outputs の削除や破壊的変更（互換性破壊あり）

---

## 🚀 リリース手順

### 1. `main` ブランチでの CI 検証確認
`main` ブランチの最新コミットに対して GitHub Actions CI がパスしていることを確認します。

```bash
gh run list --branch main --limit 1
```

### 2. 新規バージョンの決定
直前のタグを確認し、セマンティックバージョニングに従って新タグを決定します。
（例: `v1.0.0`）

### 3. タグの作成とプッシュ
ローカルでタグを作成し、リモートにプッシュします。

```bash
git switch main
git pull origin main

# 固定バージョンの作成
git tag v1.0.0
git push origin v1.0.0

# メジャーフローティングタグの更新（強制移動）
git tag -fa v1 -m "Update v1 tag to v1.0.0"
git push origin v1 --force
```

### 4. GitHub Release の作成
GitHub CLI を使用して Release を作成します。

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
```

> [!TIP]
> 上記の一連の作業は、`.agents/skills/tag-release/` スキルを使用することで自動化できます。

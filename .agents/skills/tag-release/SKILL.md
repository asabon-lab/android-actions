---
name: tag-release
description: >-
  Create and push semver release tag (vX.Y.Z) and update floating major tag (vX)
  for composite actions after main branch merge.
---

# Composite Action リリースタグ発行スキル (tag-release)

ユーザーから「リリースして」「タグを打って」「v1.0.0 をリリースして」と依頼された際に実行するスキルです。

---

## 📋 手順

### 1. `main` の最新状態確認 & CI 通過確認
```bash
git switch main
git pull origin main
gh run list --branch main --limit 1
```

### 2. 対象バージョンの決定
- 既存タグを確認：
  ```bash
  git tag --sort=-v:refname | head -n 5
  ```
- 変更内容（互換性破壊があるか、新機能か、修正か）に応じてセマンティックバージョン（例: `v1.0.0`）を決定。
- メジャーバージョンタグ（例: `v1`）を特定。

### 3. タグの作成とプッシュ
```bash
# 1. 固定バージョンの作成と push
git tag <新バージョン>
git push origin <新バージョン>

# 2. フローティングメジャータグの強制更新と push
git tag -fa <メジャータグ> -m "Update <メジャータグ> to <新バージョン>"
git push origin <メジャータグ> --force
```

### 4. GitHub Release の作成
```bash
gh release create <新バージョン> --title "<新バージョン>" --generate-notes
```

### 5. ユーザーへの完了報告
- 発行した固定タグ、更新したメジャータグ、Release URL を提示する。

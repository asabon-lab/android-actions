---
name: check-ci
description: >-
  Inspect, monitor, and analyze GitHub Actions workflow runs, summaries,
  annotations, and failure logs using GitHub CLI (gh).
---

# GitHub Actions ログ確認・解析スキル (check-ci)

GitHub Actions（CI、テスト等）の実行状況、サマリー、Annotations（警告・非推奨通知）、エラーログを迅速に取得・解析するためのスキルです。

---

## 🎯 目的

- 膨大なログ全体を漫然と取得するのではなく、**サマリー、Annotations、失敗ステップのログ** をピンポイントで抽出し、CI 失敗時の原因特定・修正を高速化する。

---

## 📋 実行手順

### 1. ワークフロー実行（Run）の一覧確認

```bash
# 直近 5 件のワークフロー実行を確認
gh run list --limit 5

# ブランチに紐づく実行を確認
gh run list --branch <ブランチ名> --limit 3
```

### 2. サマリー & Annotations（警告・注記）の確認

```bash
gh run view <RUN_ID>
```

### 3. 失敗ステップのログ抽出

```bash
# 失敗ステップのログのみを抽出
gh run view <RUN_ID> --log-failed
```

### 4. 実行中ワークフローの完了待機

```bash
# 完了まで待機
gh run watch <RUN_ID>
```

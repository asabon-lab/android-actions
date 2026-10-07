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
# PR に紐づく全チェックおよび Run URL を確認
gh pr checks <PR番号>

# 直近 5 件のワークフロー実行を確認
gh run list --limit 5

# ブランチに紐づく実行を確認
gh run list --branch <ブランチ名> --limit 5
```

### 2. サマリー & Annotations（警告・注記）の網羅確認

> [!IMPORTANT]
> **全 Run の点検が必須**: `CI` だけでなく、`Release Drafter` など PR でトリガーされた**すべてのワークフローの Run ID** に対して、例外なく個別に `gh run view` を実行すること。「pass しているから大丈夫」と確認を省くことは禁止。

```bash
# 各 Run ID ごとに Annotations を確認
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

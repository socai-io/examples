<div align="center">

<h1>
  <a href="https://socai.io/"><img src="https://raw.githubusercontent.com/socai-io/socai/main/site/public/icon-192.png" width="36" alt="socai アイコン" align="absmiddle"></a>
  socai examples
</h1>

**アプリから実際のソーシャルリサーチを実行。**

[English](README.md) · [简体中文](README.zh-CN.md) · **日本語** · [한국어](README.ko.md)

[![website](https://img.shields.io/badge/website-socai.io-555?style=flat-square&color=blue)](https://socai.io/)
[![API reference](https://img.shields.io/badge/API-reference-555?style=flat-square&color=blue)](https://agent.socai.io/api/server/docs.md)

</div>

Socai クラウド API の小さなサーバーサイドサンプルです。各言語で、調査の作成、結果の取得、ソースレコードの取得、未完了タスクのキャンセルを実行できます。ブラウザーはクラウド上で動作し、ローカルの Chrome は不要です。

## クイックスタート

Socai にログインし、サイドバーの **API keys** でキーを作成します。一度だけコピーし、サーバーのシークレット管理に保存してください。

```bash
export SOCAI_API_BASE_URL='https://agent.socai.io/api/server/v1'
# SOCAI_API_KEY はサーバーの環境変数として安全に設定します。
export SOCAI_IDEMPOTENCY_KEY="$(uuidgen)"
python3 python/demo.py create 'X 上の AI ウェアラブルへの最近の反応を、元の投稿リンク付きで調査してください。'
```

中国向けには `https://agentcn.socai.io/api/server/v1`、開発環境には `https://agent-dev.socai.io/api/server/v1` を使用します。作成は HTTP `202` とタスクの `id` を返します。ID と冪等性キーを保存してください。

```bash
python3 python/demo.py get resp_REPLACE_WITH_REAL_ID
python3 python/demo.py records resp_REPLACE_WITH_REAL_ID
# タスクを停止する場合のみ実行します。
python3 python/demo.py cancel resp_REPLACE_WITH_REAL_ID
```

## 言語を選ぶ

[Python](python/)、[JavaScript](javascript/)、[TypeScript](typescript/)、[Go](go/)、[Rust](rust/)、[Java](java/)、[C#](csharp/)、[Ruby](ruby/)、[PHP](php/)、[Swift](swift/)、[Kotlin](kotlin/) の各ディレクトリに、コードと実行手順があります。

## API の操作

| コマンド | リクエスト | 用途 |
| --- | --- | --- |
| `create '質問'` | `POST /responses` | 固定の `Idempotency-Key` を付けて非同期調査を作成。 |
| `get resp_…` | `GET /responses/{id}` | 状態と最終的な `output_text` を取得。 |
| `records resp_… [cursor]` | `GET /responses/{id}/records` | 元の投稿などの証拠をページ単位で取得。 |
| `cancel resp_…` | `POST /responses/{id}/cancel` | 未完了タスクを明示的に停止。 |

`queued` または `in_progress` の間は、約 3 秒ごとに同じ ID を照会します。`requires_action` の場合、Socai にログインしているユーザーが `socai.required_action.authorization_url` を開いてプラットフォーム認証を完了し、同じ ID の照会を再開します。終了状態は `completed`、`failed`、`cancelled` です。

レコードは `next_cursor` を次のコマンドに渡し、null になるまで取得します。空のレコードも正常な結果です。各コマンドは 30 秒のタイムアウトで一度だけリクエストし、リダイレクトや自動再試行は行いません。タイムアウトしてもサーバーのタスクはキャンセルされません。作成結果が不明な場合は、同じキーと同じ質問だけで再試行してください。

## 認証とエラー

キーはアカウントの Credits、管理済みプラットフォーム認証、プロジェクト権限を使用します。フロントエンド、プロンプト、ログ、スクリーンショット、Git に含めないでください。期限切れ・失効は `401`、アカウント制限は `403`、冪等性の競合は `409` です。`429` では残高不足と再試行可能な制限を区別し、`Retry-After` に従います。失敗時は終了コードが非ゼロになります。

詳細なスキーマ、継続対話、監視、分析については [Markdown API リファレンス](https://agent.socai.io/api/server/docs.md) を参照してください。Chat Completions と Messages も `background: true` の非同期拡張を使用し、同期ストリーミングとは異なります。

<div align="center">

<h1>
  <a href="https://socai.io/"><img src="https://raw.githubusercontent.com/socai-io/socai/main/site/public/icon-192.png" width="36" alt="socai 图标" align="absmiddle"></a>
  socai examples
</h1>

**为你的应用接入真实的社交平台调研。**

[English](README.md) · **简体中文** · [日本語](README.ja.md) · [한국어](README.ko.md)

[![website](https://img.shields.io/badge/website-socai.io-555?style=flat-square&color=blue)](https://socai.io/)
[![API reference](https://img.shields.io/badge/API-reference-555?style=flat-square&color=blue)](https://agentcn.socai.io/api/server/docs.md)

</div>

简单、可运行的 Socai 云端 API 示例。每种语言都支持创建调研、查询结果、读取素材和取消任务四个操作。使用的是云端浏览器，不需要在调用程序的机器上打开 Chrome。

## 快速开始

登录 Socai，在侧边栏打开 **API 密钥**，创建并复制密钥，保存到服务端的密钥管理工具。

```bash
export SOCAI_API_BASE_URL='https://agentcn.socai.io/api/server/v1'
# 在服务端安全设置 SOCAI_API_KEY，不要写入前端或 Git。
export SOCAI_IDEMPOTENCY_KEY="$(uuidgen)"
python3 python/demo.py create '调研小红书上近期 AI 可穿戴设备的真实反馈，附原帖链接。'
```

海外使用 `https://agent.socai.io/api/server/v1`，开发环境使用 `https://agent-dev.socai.io/api/server/v1`。选择与你的账号环境对应的地址。

创建返回 HTTP `202` 和 `id`。保存任务 ID 和幂等键，再查询同一个任务：

```bash
python3 python/demo.py get resp_替换为真实任务ID
python3 python/demo.py records resp_替换为真实任务ID
# 仅在明确希望停止任务时调用：
python3 python/demo.py cancel resp_替换为真实任务ID
```

## 选择语言

支持 [Python](python/)、[JavaScript](javascript/)、[TypeScript](typescript/)、[Go](go/)、[Rust](rust/)、[Java](java/)、[C#](csharp/)、[Ruby](ruby/)、[PHP](php/)、[Swift](swift/) 和 [Kotlin](kotlin/)。每个目录包含代码、运行方式和环境要求。

## 四个接口

| 命令 | 请求 | 用途 |
| --- | --- | --- |
| `create '问题'` | `POST /responses` | 携带固定的 `Idempotency-Key`，异步创建一次任务。 |
| `get resp_…` | `GET /responses/{id}` | 查询状态和最终 `output_text`。 |
| `records resp_… [cursor]` | `GET /responses/{id}/records` | 分页读取原帖、评论和素材记录。 |
| `cancel resp_…` | `POST /responses/{id}/cancel` | 主动停止未结束的任务。 |

`queued`、`in_progress` 时约每三秒查询一次。遇到 `requires_action`，由已登录 Socai 的用户打开 `socai.required_action.authorization_url`，完成平台登录，再继续查询原任务。`completed`、`failed`、`cancelled` 是结束状态。

读取素材时，将返回的 `next_cursor` 原样传给下一次命令，直到它为 null。没有记录时返回空列表，不代表可以编造来源。每条命令只发起一次请求，HTTP 超时为 30 秒，不自动重试、不跟随重定向。客户端超时不会自动取消服务端任务；创建结果不确定时只能用原幂等键和同样的问题重试。

## 认证和错误

密钥使用当前账号的 Credits、托管平台账号和项目权限。不要把它放到网页代码、Prompt、日志或截图中。过期或撤销的密钥返回 `401`；账号限制返回 `403`；幂等冲突返回 `409`。遇到 `429`，区分余额不足与可重试的限流，并遵循 `Retry-After`，不要立即循环重试。非成功响应会以非零状态退出，可保存请求 ID 联系支持。

完整参数、多轮对话、监测与分析能力见 [Markdown 接口文档](https://agentcn.socai.io/api/server/docs.md)。Chat Completions 和 Messages 兼容入口同样使用 `background: true` 异步扩展，不能当作同步流式模型接口使用。

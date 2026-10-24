<div align="center">

<h1>
  <a href="https://socai.io/"><img src="https://raw.githubusercontent.com/socai-io/socai/main/site/public/icon-192.png" width="36" alt="socai 아이콘" align="absmiddle"></a>
  socai examples
</h1>

**앱에서 실제 소셜 리서치를 실행하세요.**

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · **한국어**

[![website](https://img.shields.io/badge/website-socai.io-555?style=flat-square&color=blue)](https://socai.io/)
[![API reference](https://img.shields.io/badge/API-reference-555?style=flat-square&color=blue)](https://agent.socai.io/api/server/docs.md)

</div>

Socai 클라우드 API를 위한 간단한 서버 측 예제입니다. 모든 언어에서 리서치 생성, 결과 조회, 출처 레코드 조회, 미완료 작업 취소를 제공합니다. 브라우저는 클라우드에서 실행되므로 로컬 Chrome은 필요하지 않습니다.

## 빠른 시작

Socai에 로그인한 뒤 사이드바의 **API keys**에서 키를 생성하세요. 키를 한 번 복사하여 서버의 비밀 관리 도구에 저장하세요.

```bash
export SOCAI_API_BASE_URL='https://agent.socai.io/api/server/v1'
# SOCAI_API_KEY는 서버 환경 변수에 안전하게 설정하세요.
export SOCAI_IDEMPOTENCY_KEY="$(uuidgen)"
python3 python/demo.py create 'X의 AI 웨어러블에 대한 최근 반응을 원본 게시물 링크와 함께 조사해 주세요.'
```

중국 환경은 `https://agentcn.socai.io/api/server/v1`, 개발 환경은 `https://agent-dev.socai.io/api/server/v1`을 사용합니다. 생성 요청은 HTTP `202`와 `id`를 반환합니다. 작업 ID와 멱등성 키를 함께 보관하세요.

```bash
python3 python/demo.py get resp_REPLACE_WITH_REAL_ID
python3 python/demo.py records resp_REPLACE_WITH_REAL_ID
# 미완료 작업을 중단하려는 경우에만 실행하세요.
python3 python/demo.py cancel resp_REPLACE_WITH_REAL_ID
```

## 언어 선택

[Python](python/), [JavaScript](javascript/), [TypeScript](typescript/), [Go](go/), [Rust](rust/), [Java](java/), [C#](csharp/), [Ruby](ruby/), [PHP](php/), [Swift](swift/), [Kotlin](kotlin/) 디렉터리에 코드와 실행 방법이 있습니다.

## API 작업

| 명령 | 요청 | 용도 |
| --- | --- | --- |
| `create '질문'` | `POST /responses` | 고정된 `Idempotency-Key`로 비동기 리서치를 생성합니다. |
| `get resp_…` | `GET /responses/{id}` | 상태와 최종 `output_text`를 조회합니다. |
| `records resp_… [cursor]` | `GET /responses/{id}/records` | 원본 게시물 등 출처 자료를 페이지 단위로 읽습니다. |
| `cancel resp_…` | `POST /responses/{id}/cancel` | 미완료 작업을 명시적으로 중단합니다. |

`queued` 또는 `in_progress` 상태에서는 약 3초마다 같은 ID를 조회하세요. `requires_action`이면 Socai에 로그인한 사용자가 `socai.required_action.authorization_url`을 열어 플랫폼 로그인을 마치고 같은 ID의 조회를 재개해야 합니다. 종료 상태는 `completed`, `failed`, `cancelled`입니다.

레코드의 `next_cursor`를 다음 명령에 전달하고 null이 될 때까지 반복하세요. 빈 레코드 목록도 정상적인 응답입니다. 각 명령은 30초 제한으로 요청을 한 번만 보내며 리디렉션이나 자동 재시도를 하지 않습니다. 클라이언트 시간 초과는 서버 작업을 취소하지 않습니다. 생성 결과가 불확실할 때는 원래 멱등성 키와 동일한 질문으로만 재시도하세요.

## 인증과 오류

키는 계정의 Credits, 관리형 플랫폼 로그인, 프로젝트 권한을 사용합니다. 프런트엔드, 프롬프트, 로그, 스크린샷 또는 Git에 넣지 마세요. 만료·철회된 키는 `401`, 계정 제한은 `403`, 멱등성 충돌은 `409`를 반환합니다. `429`에서는 잔액 부족과 재시도 가능한 제한을 구분하고 `Retry-After`를 따르세요. 실패한 명령은 0이 아닌 종료 코드를 반환합니다.

전체 스키마, 다중 턴 대화, 모니터링과 분석은 [Markdown API 문서](https://agent.socai.io/api/server/docs.md)를 참고하세요. Chat Completions와 Messages 호환 API도 `background: true` 비동기 확장을 사용하며 동기 스트리밍 API와는 다릅니다.

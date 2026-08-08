# Codex/LLM利用におけるSLO（サービスレベル目標）運用とユーザー体験保護

## 1. コンセプト：LLM利用へのSLO組み込み

従来の Web サービスにおける SLO（可用性 99.9% や P99 レイテンシ < 200ms）と同様に、**「LLM（Codex）利用における開発体験（DX）」にもSLOを定義する。**

目的は、コンテキスト肥大化による「回答精度の低下（Lost in the Middle）」や「レスポンス遅延（TTFT悪化）」、「思考のスタック（迷走）」を未然に防ぎ、**開発者の生産性と快適な体験を維持すること**にある。

---

## 2. 定義するSLI/SLO指標（Lokiログベース）

Lokiに記録されるログから以下の SLI（Service Level Indicator）を抽出し、閾値（SLO）を超えた場合に**「体験悪化の予兆」**として検出する。

| 対象 | SLI（測定指標） | 目標とするSLO（正常値） | SLO逸脱（体験低下）の閾値 |
| :--- | :--- | :--- | :--- |
| **応答速度** | `ttft_ms`（初回レスポンス時間） | **< 2.0 秒** | **> 3.5 秒**（Prefill読み込みで体験悪化） |
| **コンテキスト** | `input_token_count` | **< 40,000 / 65,000 Tokens** | モデル別限界値（Lost in the Middle発生） |
| **思考コスト** | `reasoning_token_count` | **< 500 Tokens** | **> 1,500 Tokens**（過去ログのノイズでモデルが迷走） |
| **同一課題ターン数** | 同一セッションでのリクエスト数 | **< 6 回** | **> 8 回**（解決できず開発者がスタック） |

---

## 3. モデル別SLOポリシー（Lokiレコメンド判定）

モデルの特性に応じた SLO ポリシーを定義し、LogQL で常時モニタリングする。

### モデル別 SLO 逸脱ライン
* **標準モデル（gpt-4o等）:** `input_token_count > 40,000`
* **高機能・推論モデル（gpt-5.6-luna等）:** `input_token_count > 65,000` または `ttft_ms > 3,500`

### LogQL による SLO 逸脱セッションの検出
```logql
# SLO閾値を逸脱した（＝体験損ねの予兆がある）セッションを検出するクエリ
{service_name=~".+"}
| unwrap input_token_count
| (model =~ "gpt-4.*" and input_token_count > 40000)
  or (model =~ "gpt-5.*" and (input_token_count > 65000 or ttft_ms > 3500))

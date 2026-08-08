# Codex OpenTelemetry local stack

Codex CLI の OpenTelemetry データを、ローカルの Grafana、Tempo、Loki、Prometheus で確認するための構成です。データは Docker volume にのみ保存され、外部サービスへ送信しません。

## 起動

Docker Desktop を起動してから、このディレクトリで実行します。

```sh
docker-compose up -d
```

Docker Compose v2 プラグインがある環境では、次でも起動できます。

```sh
docker compose up -d
```

Grafana は http://localhost:3000 で開けます。初期ログインは `admin` / `admin` です。初回ログイン時にパスワード変更を求められます。

## Codex の設定

リポジトリ直下に `.codex` ディレクトリを作成し、サンプルを `config.toml` としてコピーします。

```sh
mkdir -p .codex
cp llm-observability/codex/codex.config.toml.example .codex/config.toml
```

Codex CLI を新規に開始し、短いタスクを1つ実行します。既存のプロセスは設定を再読込しないため、必ず再起動してください。

```sh
codex "このリポジトリの構成を一文で説明して"
```

## 確認

1. Grafana の **Dashboards** → **Codex** → **Codex observability** を開く。
2. trace は **Explore** → **Tempo** で `{ resource.service.name = "codex" }` を検索する。
3. metric は **Explore** → **Prometheus** で `codex_turn_token_usage_sum` を検索する。
4. log は **Explore** → **Loki** で `{service_name=~".+"}` を検索する。

ダッシュボード下部の **Log fields — expand a row to inspect** パネルでも、ログ行を展開して取得済みのラベル・フィールドを確認できます。

メトリクス名は Codex のバージョンで変わる可能性があります。Prometheus の `codex_` から始まる時系列を Explore で確認し、ダッシュボードのクエリを調整してください。

## 停止と初期化

停止だけなら、以下です。観測データは維持されます。

```sh
docker-compose down
```

データも削除して初期状態に戻す場合だけ、以下を実行します。

```sh
docker-compose down -v
```

## プライバシー

`log_user_prompt = false` にしています。ただし trace 属性や tool の入出力にパス・コマンド・エラー文が含まれる可能性はあります。機密リポジトリで使う前に、Collector に属性の削除・マスキング処理を追加してください。

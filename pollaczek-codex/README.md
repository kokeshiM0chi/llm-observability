# codex-mg1-analyzer

Grafana Loki からエクスポートした Codex 利用ログ（OTEL Telemetry ログ）を解析し、**オペレーションズ・リサーチ（OR）の「待ち行列理論 ($M/G/1$ モデル)」**を用いて、同時利用開発者数に応じた Token 制限（TPM: Tokens Per Minute）の限界点を試算・可視化するプロジェクトです。

---

## 1. 概要

Codex 等の LLM アシスタントは、会話のターンが進むにつれて過去コンテキストを含めてリクエストを送信するため、1回あたりの消費トークン数（$S$）が非常に大きくなる特徴があります。

本ツールは、実際の利用ログから以下のパラメータを抽出し、$M/G/1$ 待ち行列モデルを適用して**「何人の開発者が同時にアクティブになると API の TPM 制限（レートリミット）に達するか」**をシミュレーションします。

* **到着過程 ($M$):** 開発者のリクエスト発生（ポアソン到着）
* **サービス時間 ($G$):** 1リクエストあたりの消費トークン数（平均 $E[S]$ および 分散 $Var[S]$）
* **窓口数 ($1$):** API 全体の容量制限 (TPM Limit)

---

## 2. ログデータの取得手順 (Grafana Loki)

1. **Grafana Explore 画面を開く**
   * サイドメニューの **Explore 🧭** をクリック（またはキーボードショートカット `g` ➔ `e`）。
2. **データソースの設定**
   * 左上のデータソース選択で **`Loki`** を選択。
3. **LogQL の実行**
   * 以下の LogQL を入力して **Run query** を実行：
     ```logql
     {service_name=~".+"} | json | input_token_count > 0
     ```
4. **CSV のエクスポート**
   * 画面右上の **Inspect** ➔ **Data** タブを開く。
   * **Apply panel transformations** を **ON** に設定。
   * **Download CSV** をクリックして CSV ファイルを取得し、本プロジェクトのルートディレクトリに配置。

---

## 3. セットアップと実行手順 (`uv` を使用)

本プロジェクトでは、高速な Python パッケージマネージャー [uv](https://github.com/astral-sh/uv) を使用します。

### 動作要件
* Python 3.8 以上
* [uv](https://docs.astral.sh/uv/)

### ① リポジトリの初期化とパッケージ追加 (初回のみ)
```bash
# プロジェクトの作成
uv init

# 分析に必要な依存パッケージのインストール
uv add pandas numpy matplotlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def analyze_tpm_mg1(csv_path: str):
    # 1. CSVデータの読み込みと前処理
    df = pd.read_csv(csv_path)

    # 日時列の変換と昇順ソート
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
    df = df.sort_values("event_timestamp").reset_index(drop=True)

    # 1リクエストあたりの総トークン数 (S = input + output)
    df["total_tokens"] = df["input_token_count"] + df["output_token_count"]

    # 2. 実測データからのパラメータ抽出 (OR / M/G/1モデル用)
    total_requests = len(df)
    min_time = df["event_timestamp"].min()
    max_time = df["event_timestamp"].max()
    total_minutes = (max_time - min_time).total_seconds() / 60.0

    # 1ユーザーあたりの1分間平均到着率 λ_1 (req/min)
    lambda_1 = total_requests / total_minutes

    # 1リクエストあたりの平均トークン数 E[S] および 分散 Var[S]
    E_S = df["total_tokens"].mean()
    Var_S = df["total_tokens"].var()
    C_v2 = Var_S / (E_S**2)  # 変動係数の自乗

    print("=== データ抽出結果 ===")
    print(f"計測範囲: {min_time} 〜 {max_time} ({total_minutes:.2f} 分)")
    print(f"総リクエスト数: {total_requests} 件")
    print(
        f"1人あたりのリクエスト到着率 (λ_1): {lambda_1:.4f} req/min (約 {60/lambda_1:.1f} 秒に1回)"
    )
    print(f"1リクエストの平均トークン数 (E[S]): {E_S:,.1f} tokens")
    print(f"トークン数の変動係数の自乗 (C_v^2): {C_v2:.4f}\n")

    # 3. N（開発者数）を増やした際のTPM利用率シミュレーション
    tpm_limits = [500000, 1000000, 2000000]  # 想定するAPI制限値 (TPM)
    n_range = range(1, 35)
    results = []

    for N in n_range:
        lambda_sys = N * lambda_1
        expected_tpm = lambda_sys * E_S

        for tpm in tpm_limits:
            rho = expected_tpm / tpm  # 設備利用率
            results.append(
                {
                    "N": N,
                    "TPM_Limit": tpm,
                    "Expected_TPM": expected_tpm,
                    "Rho": rho,
                }
            )

    res_df = pd.DataFrame(results)

    # 4. グラフ化と保存
    plt.figure(figsize=(10, 6))
    for tpm in tpm_limits:
        sub = res_df[res_df["TPM_Limit"] == tpm]
        plt.plot(
            sub["N"],
            sub["Rho"] * 100,
            label=f"TPM Limit: {tpm:,} (Util %)",
            marker="o",
        )

    plt.axhline(
        100, color="red", linestyle="--", label="100% Capacity (Bottleneck)"
    )
    plt.title(
        "Developer Count vs TPM Capacity Utilization (M/G/1 Model)",
        fontsize=14,
    )
    plt.xlabel("Number of Active Developers (N)", fontsize=12)
    plt.ylabel("TPM Utilization (%)", fontsize=12)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()

    output_filename = "mg1_tpm_utilization.png"
    plt.savefig(output_filename, dpi=300)
    print(f"グラフを出力しました: {output_filename}")


if __name__ == "__main__":
    # ダウンロードしたCSVファイル名を指定して実行
    analyze_tpm_mg1("./data/Explore-logs-A-data-2026-08-08 10_36_15.csv")

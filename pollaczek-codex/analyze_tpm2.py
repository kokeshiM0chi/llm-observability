import matplotlib.pyplot as plt
import numpy as np

# 1. 時間軸の設定 (0分〜90分)
t = np.linspace(0, 90, 500)

# 2. 個人利用時の1リクエストあたりのトークン成長モデル
# 初期状態: 10,000 tokens / 1分ごとに約1,100 tokens増加
# リクエスト頻度 λ = 1.0 (回/分) のため、TPM(t) = 1.0 * T(t) となる
tpm = 10000 + 1100 * t

# 3. 想定するRate Limit（TPM）の閾値設定
limits = {
    "Strict Limit (40k TPM)": 40000,
    "Standard Limit (60k TPM)": 60000,
    "High Limit (80k TPM)": 80000,
}

# 4. グラフの描画準備
fig, ax = plt.subplots(figsize=(10, 6))

# 個人のTPM消費曲線（青線）
ax.plot(
    t,
    tpm,
    label="Personal Token Consumption (TPM)",
    color="#1f77b4",
    linewidth=3,
)

# 制限値（赤・オレンジ・ピンクのライン）と交点の描画
colors = [
    "#e377c2",
    "#ff7f0e",
    "#d62728",
]  # 40k: ピンク, 60k: オレンジ, 80k: 赤
styles = [":", "--", "-."]

for (name, limit_val), col, style in zip(limits.items(), colors, styles):
    # 限界到達時間 Y (分) の算定
    y_time = (limit_val - 10000) / 1100

    # 制限値線 (横線)
    ax.axhline(
        y=limit_val,
        color=col,
        linestyle=style,
        linewidth=2,
        label=f"Limit: {limit_val:,} TPM",
    )

    # 交点プロットとテキストラベルの追加
    if y_time <= 90:
        ax.plot(y_time, limit_val, marker="o", markersize=8, color=col)
        ax.vlines(
            x=y_time, ymin=0, ymax=limit_val, color=col, linestyle=":", alpha=0.6
        )
        ax.text(
            y_time + 1.5,
            limit_val - 3000,
            f"Reaches Limit in {y_time:.1f} min\n({y_time/60:.2f} hrs)",
            fontsize=9,
            fontweight="bold",
            color=col,
            bbox=dict(
                boxstyle="round,pad=0.2", fc="white", ec=col, lw=1, alpha=0.9
            ),
        )

# 5. グラフの装飾
ax.set_title(
    "Individual Rate Limit Analysis: Time to Hit Limit by TPM Threshold",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
ax.set_xlabel(
    "Elapsed Time in Single Session (Minutes)", fontsize=11, fontweight="bold"
)
ax.set_ylabel(
    "Token Consumption per Minute (TPM)", fontsize=11, fontweight="bold"
)
ax.set_xlim(0, 90)
ax.set_ylim(0, 95000)
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper left", frameon=True)

plt.tight_layout()

# 画像として保存
plt.savefig("personal_tpm_limit_time.png", dpi=300)
plt.show()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ページ設定とテーマカラー
st.set_page_config(page_title="GPIF取りくずしシミュレーター", layout="centered")
st.markdown("""
    <style>
    body {
        background-color: #f78da7;
    }
    .highlight-red {
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 GPIF取りくずしシミュレーター")

# 入力欄
col1, col2 = st.columns(2)
with col1:
    start_age = st.number_input("取りくずし開始年齢（歳）", min_value=40, max_value=100, value=65)
    initial_assets = st.number_input("初期資産額（万円）", min_value=0, value=3000, step=100)
with col2:
    fixed_withdrawal = st.number_input("年間引出額（定額・万円）", min_value=0, value=120, step=10)
    percent_withdrawal = st.slider("年間引出率（定率・％）", min_value=0.0, max_value=20.0, value=4.0, step=0.1)

# データ読み込み
EXCEL_URL = "https://raw.githubusercontent.com/kiku-hub-design/gpif-app/main/gpif_data_2001_2023.xlsx"
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_URL)

df = load_data()
gpif_rates = df['指定配分_収益率（％）'] / 100

# GPIF収益率を無限ループ的に繰り返す
max_years = 50
repeated_rates = (gpif_rates.tolist() * ((max_years // len(gpif_rates)) + 1))[:max_years]

# 初期設定
ages = list(range(start_age, start_age + max_years))
fixed_assets = [initial_assets]
percent_assets = [initial_assets]
fixed_withdrawals = []
percent_withdrawals = []
zero_flag_fixed = False
zero_flag_percent = False

for i in range(max_years):
    rate = repeated_rates[i]

    # 定額方式
    last_fixed = fixed_assets[-1]
    interest_fixed = last_fixed * rate
    next_fixed = last_fixed + interest_fixed - fixed_withdrawal
    if next_fixed < 0:
        next_fixed = 0
        zero_flag_fixed = True
    fixed_assets.append(next_fixed)
    fixed_withdrawals.append(fixed_withdrawal if not zero_flag_fixed else 0)

    # 定率方式
    last_percent = percent_assets[-1]
    withdrawal_percent = last_percent * (percent_withdrawal / 100)
    interest_percent = last_percent * rate
    next_percent = last_percent + interest_percent - withdrawal_percent
    if next_percent < 0:
        next_percent = 0
        zero_flag_percent = True
    percent_assets.append(next_percent)
    percent_withdrawals.append(withdrawal_percent if not zero_flag_percent else 0)

# データフレーム化
result_df = pd.DataFrame({
    "年齢": ages,
    "収益率（％）": [round(r * 100, 1) for r in repeated_rates[:len(ages)]],
    "定額：資産残高": fixed_assets[1:],
    "定額：引出額": fixed_withdrawals,
    "定率：資産残高": percent_assets[1:],
    "定率：引出額": percent_withdrawals,
})

# 資産が０の行を赤にする条件
def highlight_zero(s):
    return ['color: red' if v == 0 else '' for v in s]

# 表示
st.markdown("### 📋 シミュレーション結果")
st.dataframe(result_df.style.apply(highlight_zero, subset=["定額：資産残高", "定率：資産残高"]), use_container_width=True)

# グラフ
st.markdown("### 📈 資産残高の推移")
fig, ax = plt.subplots()
ax.plot(result_df["年齢"], result_df["定額：資産残高"], label="定額", marker='o')
ax.plot(result_df["年齢"], result_df["定率：資産残高"], label="定率", marker='x')
ax.set_xlabel("年齢")
ax.set_ylabel("資産残高（万円）")
ax.set_title("定額 vs 定率 取りくずし比較")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.info("※ GPIFの過去収益率を使用した試算です。将来の利回りを保証するものではありません。")

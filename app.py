# ------------------------------------------------------------
# このコードは 木村久美（Kumi Kimura） によって作成されました。
# 著作権は放棄されておらず、無断での商用利用・転載・再配布を禁じます。
# 教育目的・参考利用は歓迎しますが、必ず出典を明記してください。
#
# Created by Kumi Kimura
# Copyright retained. Unauthorized commercial use, reproduction,
# or redistribution is strictly prohibited.
# Educational or personal reference use is allowed with proper attribution.
# ------------------------------------------------------------

import streamlit as st
import pandas as pd

# ページ設定とテーマカラー（印刷時は白背景）
st.set_page_config(page_title="取りくずしシミュレーター", layout="centered")
st.markdown("""
    <style>
    body {
        background-color: #f78da7;
    }
    @media print {
        body {
            background-color: white !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 取りくずしシミュレーター")

# 入力欄
col1, col2 = st.columns(2)
with col1:
    start_age = st.number_input("取りくずし開始年齢（歳）", min_value=40, max_value=100, value=65)
    initial_assets = st.number_input("初期資産額（万円）", min_value=0, value=2000, step=100)
with col2:
    fixed_withdrawal = st.number_input("年間引出額（定額・万円）", min_value=0, value=120, step=10)
    percent_withdrawal = st.slider("年間引出率（定率・％）", min_value=0.0, max_value=6.0, value=4.0, step=0.1)

# データ読み込み
EXCEL_URL = "https://raw.githubusercontent.com/kiku-hub-design/gpif-app/main/gpif_data_2001_2023.xlsx"
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_URL)

df = load_data()
gpif_rates = df['指定配分_収益率（％）'].fillna(0) / 100

# GPIF収益率を35年分繰り返す
max_years = 35
repeated_rates = (gpif_rates.tolist() * ((max_years // len(gpif_rates)) + 1))[:max_years]

# 計算
ages = list(range(start_age, start_age + max_years))
fixed_assets = [initial_assets]
percent_assets = [initial_assets]
fixed_withdrawals = []
percent_withdrawals = []
zero_flag_fixed = False
zero_flag_percent = False

for i in range(max_years):
    rate = repeated_rates[i]

    # 定額
    last_fixed = fixed_assets[-1]
    temp_fixed = last_fixed - fixed_withdrawal if last_fixed > 0 else 0
    if temp_fixed < 0:
        temp_fixed = 0
        zero_flag_fixed = True
    interest_fixed = int(round(temp_fixed * rate))
    next_fixed = int(round(temp_fixed + interest_fixed))
    fixed_assets.append(next_fixed)
    fixed_withdrawals.append(fixed_withdrawal if not zero_flag_fixed else 0)

    # 定率
    last_percent = percent_assets[-1]
    withdrawal_percent = int(round(last_percent * (percent_withdrawal / 100))) if last_percent > 0 else 0
    temp_percent = last_percent - withdrawal_percent
    if temp_percent < 0:
        temp_percent = 0
        zero_flag_percent = True
    interest_percent = int(round(temp_percent * rate))
    next_percent = int(round(temp_percent + interest_percent))
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

# スタイル適用：資産残高が0のセルを赤文字に
def highlight_zero(val):
    return 'color: red;' if val == 0 else ''

styled_df = result_df.style \
    .applymap(highlight_zero, subset=["定額：資産残高", "定率：資産残高"]) \
    .format({"収益率（％）": "{:.1f}"})

# 表示
st.markdown("### 📋 シミュレーション結果")
st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.info("※ GPIFの過去収益率を参照に、50代プランを元に算出した仮試算です。将来の利回りを保証するものではありません。")

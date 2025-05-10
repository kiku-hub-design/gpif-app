import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit設定
st.set_page_config(page_title="取りくずしシミュレーション", layout="centered")

# タイトルと説明
st.title("📊 GPIF取りくずしシミュレーター")
st.markdown("指定配分での過去収益率を使って、資産の取りくずしシミュレーションを行います。")

# 入力項目
col1, col2 = st.columns(2)
with col1:
    initial_assets = st.number_input("初期資産額（万円）", min_value=0, value=3000, step=100)
    withdrawal = st.number_input("年間引出額（万円）", min_value=0, value=120, step=10)
with col2:
    start_age = st.number_input("取りくずし開始年齢（歳）", min_value=40, max_value=100, value=65, step=1)

# データ読み込み
EXCEL_URL = "https://raw.githubusercontent.com/kiku-hub-design/gpif-app/main/gpif_data_2001_2023.xlsx"
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_URL)

df = load_data()
rates = df['指定配分_収益率（％）'] / 100  # 実数に変換

# シミュレーション
ages = list(range(start_age, start_age + len(rates)))
results = []
assets = initial_assets

for age, rate in zip(ages, rates):
    interest = round(assets * rate, 2)
    new_assets = round(assets + interest - withdrawal, 2)
    results.append({
        "年齢": age,
        "利回り（％）": round(rate * 100, 1),
        "年初資産": assets,
        "利息": interest,
        "引出額": withdrawal,
        "年末残高": max(new_assets, 0)
    })
    assets = max(new_assets, 0)
    if assets <= 0:
        break

# データフレームに変換
result_df = pd.DataFrame(results)

# 表示
st.markdown("### 📋 シミュレーション結果")
st.dataframe(result_df, use_container_width=True)

# グラフ
st.markdown("### 📈 残高推移グラフ")
fig, ax = plt.subplots()
ax.plot(result_df["年齢"], result_df["年末残高"], marker='o')
ax.set_xlabel("年齢")
ax.set_ylabel("残高（万円）")
ax.set_title("資産残高の推移")
ax.grid(True)
st.pyplot(fig)

# 注意書き
st.info("※ この結果は過去の収益率をもとにしたシミュレーションであり、将来の運用成果を保証するものではありません。")

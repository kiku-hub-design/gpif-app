import streamlit as st
import pandas as pd

# ファイルの読み込み（GitHub上のExcelファイルURLを指定）
EXCEL_URL = "https://raw.githubusercontent.com/kiku-hub-design/gpif-app/main/GPIF_収益率_配分比率_均等＋指定運用_2001_2023.xlsx"

# ページ設定
st.set_page_config(page_title="GPIFシミュレーター", layout="centered")

# タイトル表示
st.title("GPIFシミュレーション")

# Excelデータの読み込み
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_URL, sheet_name=0)

df = load_data()

# 表示
st.write("読み込んだデータの一部：")
st.dataframe(df.head())

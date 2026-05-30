import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"

# --- FUNGSI LOAD DATA ---
def load_data():
    try:
        df = pd.read_csv(FILE_PATH, sep=";").fillna("")
        df.columns = df.columns.str.strip().str.title()
        return df
    except:
        return pd.DataFrame(columns=["Status", "Model", "Serial Number"])

if 'df' not in st.session_state: st.session_state.df = load_data()
df = st.session_state.df

# --- MENU ---
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", ["📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop"])

if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    
    # 1. Metrik
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total", len(df))
    c2.metric("🟢 Tersedia", len(df[df['Status'] == 'Tersedia']))
    c3.metric("🔵 Di Pakai", len(df[df['Status'] == 'Di Pakai']))
    c4.metric("🟡 Perbaikan", len(df[df['Status'] == 'Perlu Perbaikan']))
    c5.metric("🔴 Rusak", len(df[df['Status'] == 'Rusak']))

    # 2. Tabel
    st.dataframe(df, use_container_width=True)

    # 3. CHART (WAJIB MUNCUL DI BAWAH)
    st.markdown("---")
    st.subheader("📈 Analisis Data Visual")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("##### Distribusi Status Laptop")
        status_data = df['Status'].value_counts().reset_index()
        status_data.columns = ['Status', 'Jumlah']
        fig_pie = px.pie(status_data, values='Jumlah', names='Status', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_b:
        st.write("##### Top 5 Model Laptop")
        model_data = df['Model'].value_counts().head(5).reset_index()
        model_data.columns = ['Model', 'Jumlah']
        fig_bar = px.bar(model_data, x='Model', y='Jumlah', color='Model')
        st.plotly_chart(fig_bar, use_container_width=True)

elif menu == "👥 User Directory":
    st.title("👥 User Directory")
    st.write("Data user...")

elif menu == "➕ Tambah Laptop":
    st.title("➕ Tambah Laptop")
    st.write("Form tambah...")

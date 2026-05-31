import streamlit as st
import pandas as pd
import requests
import base64
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"
LOG_PATH = "audit_log.csv"
BU_OPTIONS = ["UNB", "UCR", "RNB", "LBI", "SMI", "UMK"]

# --- CONFIG & LOAD DATA ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    GITHUB_TOKEN = None

def load_data(path):
    try:
        df = pd.read_csv(path, sep=";").fillna("")
        df.columns = df.columns.str.strip().str.title()
        return df
    except:
        if "audit_log" in path:
            return pd.DataFrame(columns=["Timestamp", "Action", "Detail"])
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Tahun Beli", "Notes"])

def save_to_github(dataframe, path):
    if not GITHUB_TOKEN: return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha", "") if res.status_code == 200 else ""
    csv_content = dataframe.to_csv(index=False, sep=";")
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    payload = {"message": "Update Data", "content": encoded_content, "sha": sha if sha else None}
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

# Load Data ke Session State
if 'df' not in st.session_state: st.session_state.df = load_data(FILE_PATH)
if 'audit_df' not in st.session_state: st.session_state.audit_df = load_data(LOG_PATH)

def add_log(action, detail):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{"Timestamp": ts, "Action": action, "Detail": detail}])
    updated_logs = pd.concat([new_log, st.session_state.audit_df], ignore_index=True)
    if save_to_github(updated_logs, LOG_PATH):
        st.session_state.audit_df = updated_logs

# --- SIDEBAR ---
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log"
])

# --- LOGIKA APLIKASI ---
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    
    # Ambil status unik, handle jika kosong
    status_list = st.session_state.df['Status'].unique().tolist() if not st.session_state.df.empty else []
    all_status = ["Semua"] + status_list
    filter_status = st.selectbox("🔍 Filter Berdasarkan Status:", all_status)
    
    display_df = st.session_state.df[st.session_state.df['Status'] == filter_status] if filter_status != "Semua" else st.session_state.df
    
    status_counts = st.session_state.df['Status'].value_counts()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total", len(st.session_state.df))
    c2.metric("🟢 Tersedia", status_counts.get('Tersedia', 0))
    c3.metric("🔵 Di Pakai", status_counts.get('Di Pakai', 0))
    c4.metric("🟡 Perbaikan", status_counts.get('Perlu Perbaikan', 0))
    c5.metric("🔴 Rusak", status_counts.get('Rusak', 0))
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔹 Distribusi Status")
        if not status_counts.empty:
            fig_pie = px.pie(status_counts.reset_index(), values='count', names='Status', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.subheader("🔹 Top 5 Model Laptop")
        if 'Model' in st.session_state.df.columns:
            top_model = st.session_state.df['Model'].value_counts().head(5).reset_index()
            fig_bar = px.bar(top_model, x='Model', y='count', color='Model')
            st.plotly_chart(fig_bar, use_container_width=True)

# ... (Menu lainnya tetap seperti kode asli Anda) ...

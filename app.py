import streamlit as st
import pandas as pd
import requests
import base64
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

# --- KONFIGURASI ---
GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"
LOG_PATH = "audit_log.csv"
BU_OPTIONS = ["UNB", "UCR", "RNB", "LBI", "SMI", "UMK"]

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    GITHUB_TOKEN = None

# --- FUNGSI UTAMA ---
def load_data(path):
    try:
        df = pd.read_csv(path, sep=";").fillna("")
        df.columns = df.columns.str.strip().str.title()
        return df
    except:
        return pd.DataFrame()

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

# Inisialisasi Session State
if 'df' not in st.session_state: st.session_state.df = load_data(FILE_PATH)
if 'audit_df' not in st.session_state: st.session_state.audit_df = load_data(LOG_PATH)

# --- SIDEBAR ---
st.sidebar.title("💻 IT Asset Control")
menu = st.sidebar.radio("Navigasi:", ["📊 Dashboard", "👥 User Directory", "➕ Tambah Data", "✏️ Edit/Hapus", "📋 Audit Log"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard IT Asset")
    
    # Metrik
    status_counts = st.session_state.df['Status'].value_counts()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", len(st.session_state.df))
    c2.metric("Tersedia", status_counts.get('Tersedia', 0))
    c3.metric("Dipakai", status_counts.get('Di Pakai', 0))
    c4.metric("Perbaikan", status_counts.get('Perlu Perbaikan', 0))
    c5.metric("Rusak", status_counts.get('Rusak', 0))

    # Pencarian Global
    search = st.text_input("🔍 Cari Laptop (User/SN/Model):")
    df_show = st.session_state.df
    if search:
        mask = df_show.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        df_show = df_show[mask]
    
    st.dataframe(df_show, use_container_width=True)
    
    # Export
    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export CSV", csv, "data_aset.csv", "text/csv")

elif menu == "➕ Tambah Data":
    st.title("➕ Tambah Laptop Baru")
    with st.form("f_add"):
        m, sn = st.columns(2)
        model = m.text_input("Model")
        serial = sn.text_input("Serial Number")
        bu_o, bu_u = st.columns(2)
        bo = bu_o.selectbox("BU Owner", BU_OPTIONS)
        bu = bu_u.selectbox("BU User", BU_OPTIONS)
        stt = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"])
        user = st.text_input("User")
        submit = st.form_submit_button("💾 Simpan Data")
        
        if submit:
            if serial in st.session_state.df['Serial Number'].values:
                st.error("SN sudah terdaftar!")
            else:
                with st.spinner("Menyimpan ke server..."):
                    new_data = {"Model": model, "Serial Number": serial, "Bu Owner": bo, "Bu User": bu, "User": user, "Status": stt}
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
                    if save_to_github(st.session_state.df, FILE_PATH):
                        st.success("Berhasil disimpan!")
                        st.rerun()

elif menu == "✏️ Edit/Hapus":
    st.title("✏️ Edit atau Hapus Data")
    s_sn = st.selectbox("Pilih SN:", st.session_state.df['Serial Number'].tolist())
    idx = st.session_state.df[st.session_state.df['Serial Number'] == s_sn].index[0]
    
    col1, col2 = st.columns(2)
    if col1.button("🗑️ Hapus Data"):
        st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
        save_to_github(st.session_state.df, FILE_PATH)
        st.rerun()
    
    # (Edit logic bisa ditambah di sini mengikuti format form Tambah Data)

elif menu == "📋 Audit Log":
    st.title("📋 Log Aktivitas")
    st.dataframe(st.session_state.audit_df, use_container_width=True)

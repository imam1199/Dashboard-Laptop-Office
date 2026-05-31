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
        # Mencoba membaca dengan titik koma, jika gagal/kolom cuma 1, pakai koma
        df = pd.read_csv(path, sep=";")
        if len(df.columns) <= 1:
            df = pd.read_csv(path, sep=",")
        return df.fillna("")
    except:
        if "audit_log" in path:
            return pd.DataFrame(columns=["Timestamp", "Action", "Detail"])
        return pd.DataFrame()

def save_to_github(dataframe, path):
    if not GITHUB_TOKEN: 
        st.error("GITHUB_TOKEN tidak ditemukan!")
        return False
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Ambil SHA file untuk proses update
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha", "") if res.status_code == 200 else ""
    
    # Simpan sebagai CSV dengan pemisah koma (lebih standar untuk GitHub)
    csv_content = dataframe.to_csv(index=False, sep=",") 
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    payload = {"message": "Update Data", "content": encoded_content, "sha": sha if sha else None}
    
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return True
    else:
        st.error(f"Gagal simpan ke GitHub! Code: {response.status_code}")
        return False

# Load Data
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
    "📊 Dashboard & Analytics", "✏️ Edit Data", "📋 Audit Log"
])

# --- LOGIKA APLIKASI ---
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    all_status = ["Semua"] + st.session_state.df['Status'].unique().tolist()
    filter_status = st.selectbox("🔍 Filter Berdasarkan Status:", all_status)
    display_df = st.session_state.df[st.session_state.df['Status'] == filter_status] if filter_status != "Semua" else st.session_state.df
    st.dataframe(display_df, use_container_width=True)

elif menu == "✏️ Edit Data":
    st.title("✏️ Edit Data Laptop")
    s_sn = st.selectbox("Pilih SN:", st.session_state.df['Serial Number'].tolist())
    idx = st.session_state.df[st.session_state.df['Serial Number'] == s_sn].index[0]
    row = st.session_state.df.loc[idx]
    
    with st.form("f_ed"):
        em = st.text_input("Model", value=row.get('Model', ''))
        ebo = st.selectbox("BU Owner", BU_OPTIONS, index=BU_OPTIONS.index(row.get('Bu Owner')) if row.get('Bu Owner') in BU_OPTIONS else 0)
        ebu = st.selectbox("BU User", BU_OPTIONS, index=BU_OPTIONS.index(row.get('Bu User')) if row.get('Bu User') in BU_OPTIONS else 0)
        ejt = st.text_input("Job Title", value=row.get('Job Title', ''))
        eus = st.text_input("User", value=row.get('User', ''))
        est = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"], index=["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"].index(row.get('Status', 'Tersedia')) if row.get('Status') in ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"] else 0)
        etb = st.number_input("Tahun Beli", 2015, 2030, int(row.get('Tahun Beli', 2026)))
        ent = st.text_area("Notes", value=row.get('Notes', ''))
        
        if st.form_submit_button("✅ Simpan Perubahan"):
            changes = []
            if row['Model'] != em: changes.append(f"Model: {row['Model']} -> {em}")
            if row['Status'] != est: changes.append(f"Status: {row['Status']} -> {est}")
            if row['User'] != eus: changes.append(f"User: {row['User']} -> {eus}")
            if row['Notes'] != ent: changes.append("Notes diupdate")
            
            detail_log = f"SN {s_sn}: " + (", ".join(changes) if changes else "Update data umum")
            
            # Update data
            st.session_state.df.at[idx, 'Model'] = em
            st.session_state.df.at[idx, 'Bu Owner'] = ebo
            st.session_state.df.at[idx, 'Bu User'] = ebu
            st.session_state.df.at[idx, 'Job Title'] = ejt
            st.session_state.df.at[idx, 'User'] = eus
            st.session_state.df.at[idx, 'Status'] = est
            st.session_state.df.at[idx, 'Tahun Beli'] = etb
            st.session_state.df.at[idx, 'Notes'] = ent
            
            if save_to_github(st.session_state.df, FILE_PATH): 
                add_log("EDIT", detail_log)
                st.toast('Perubahan berhasil disimpan!', icon='💾')
                time.sleep(1.5)
                st.rerun()

elif menu == "📋 Audit Log":
    st.title("📋 Audit Log")
    if not st.session_state.audit_df.empty:
        st.dataframe(st.session_state.audit_df, use_container_width=True)
    else:
        st.info("Belum ada data log.")

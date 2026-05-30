import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    GITHUB_TOKEN = None

def load_data():
    try:
        df = pd.read_csv(FILE_PATH, sep=";").fillna("")
        df.columns = df.columns.str.strip().str.title()
        # Paksa Tahun Beli jadi angka, kalau kosong isi 2023
        df['Tahun Beli'] = pd.to_numeric(df['Tahun Beli'], errors='coerce').fillna(2023)
        return df
    except:
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Notes", "Tahun Beli"])

def save_to_github(dataframe):
    if not GITHUB_TOKEN: return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha", "") if res.status_code == 200 else ""
    csv_content = dataframe.to_csv(index=False, sep=";")
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    payload = {"message": "Update Data", "content": encoded_content, "sha": sha if sha else None}
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

if 'df' not in st.session_state: st.session_state.df = load_data()
df = st.session_state.df

st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log"
])

if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    # Logika Perbaikan Umur
    df['Umur'] = datetime.now().year - df['Tahun Beli']
    perlu_ganti = len(df[df['Umur'] >= 3])
    
    # Hitung status
    status_counts = df['Status'].value_counts()
    tersedia = status_counts.get('Tersedia', 0)
    dipakai = status_counts.get('Di Pakai', 0)
    perbaikan = status_counts.get('Perlu Perbaikan', 0)
    rusak = status_counts.get('Rusak', 0)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📦 Total", len(df))
    c2.metric("🟢 Tersedia", tersedia)
    c3.metric("🔵 Di Pakai", dipakai)
    c4.metric("🟡 Perbaikan", perbaikan)
    c5.metric("🔴 Rusak", rusak)
    c6.metric("⚠️ Perlu Ganti", perlu_ganti)
    
    st.dataframe(df, use_container_width=True)

elif menu == "👥 User Directory":
    st.title("👥 User Directory")
    list_users = sorted([u for u in df['User'].unique() if str(u).strip() != ""])
    s_user = st.selectbox("🎯 Pilih Nama Karyawan:", list_users)
    u_data = df[df['User'] == s_user]
    st.dataframe(u_data, use_container_width=True)

# ... (Pastikan menu lain tetap di bawah dengan struktur elif yang sama)

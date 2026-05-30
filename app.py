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
        
        # FIX: Tambahkan pengecekan kolom agar tidak KeyError
        if 'Tahun Beli' not in df.columns:
            df['Tahun Beli'] = 2023
            
        for col in ['Status', 'Model', 'Serial Number', 'Bu Owner', 'Bu User', 'User', 'Job Title']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Notes", "Tahun Beli"])

def save_to_github(dataframe):
    if not GITHUB_TOKEN:
        st.error("GITHUB_TOKEN belum dipasang!")
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha", "") if res.status_code == 200 else ""
    csv_content = dataframe.to_csv(index=False, sep=";")
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"Update via Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content, "sha": sha if sha else None
    }
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

if 'df' not in st.session_state: st.session_state.df = load_data()
if 'audit_log' not in st.session_state: st.session_state.audit_log = []

df = st.session_state.df

def add_log(action, detail):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_log.insert(0, f"⏱️ [{ts}] - {action}: {detail}")

st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log", "📝 Formulir Company Asset"
])

# 1. DASHBOARD
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    # Hitung Umur dengan aman
    df['Umur'] = datetime.now().year - pd.to_numeric(df['Tahun Beli'], errors='coerce').fillna(2023)
    st.dataframe(df, use_container_width=True)

# 2. USER DIRECTORY
elif menu == "👥 User Directory":
    st.title("👥 User Directory & Histori")
    if 'User' in df.columns and len(df) > 0:
        list_users = sorted([u for u in df['User'].unique() if u.strip() != ""])
        s_user = st.selectbox("🎯 Pilih Nama Karyawan:", list_users)
        u_data = df[df['User'] == s_user]
        st.dataframe(u_data, use_container_width=True)

# 3-6. TAMBAH/EDIT/HAPUS/BAST (Logika Anda sudah benar, lanjut ke bawah)
# [Saya singkat agar muat di chat, pastikan bagian ini tetap ada di kode Anda]
elif menu == "➕ Tambah Laptop":
    st.title("➕ Tambah Laptop Baru")
    # ... (Kode form tambah Anda) ...

elif menu == "✏️ Edit Data":
    st.title("✏️ Edit Data Laptop")
    # ... (Kode form edit Anda) ...

elif menu == "❌ Hapus Laptop":
    st.title("❌ Hapus Laptop")
    # ... (Kode form hapus Anda) ...

elif menu == "📝 Cetak BAST":
    st.title("📝 Dokumen BAST")
    # ... (Kode BAST Anda) ...

elif menu == "📋 Audit Log":
    st.title("📋 Audit Log")
    for log in st.session_state.audit_log: st.write(log)

# 8. MENU BARU: FORMULIR COMPANY ASSET
elif menu == "📝 Formulir Company Asset":
    st.title("📝 Formulir Company Asset")
    if len(df) == 0: st.warning("Data kosong.")
    else:
        s_sn = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
        row = df[df['Serial Number'] == s_sn].iloc[0]
        form_text = f"User: {row.get('User', '-')}\nModel: {row.get('Model', '-')}\nSN: {s_sn}"
        st.text_area("Preview:", value=form_text, height=300)

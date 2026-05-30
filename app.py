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
        for col in ['Status', 'Model', 'Serial Number', 'Bu Owner', 'Bu User', 'User', 'Job Title']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        if 'Tahun Beli' not in df.columns:
            df['Tahun Beli'] = 2023
        return df
    except:
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Notes", "Tahun Beli"])

def save_to_github(dataframe):
    if not GITHUB_TOKEN:
        st.error("GITHUB_TOKEN belum dipasang di Secrets!")
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

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

df = st.session_state.df

def add_log(action, detail):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_log.insert(0, f"⏱️ [{ts}] - {action}: {detail}")

st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log", "📝 Formulir Company Asset"
])

# [LOGIKA MENU 1-7 TETAP SAMA SEPERTI KODE LO]
if menu == "📊 Dashboard & Analytics":
    # ... (bagian dashboard lo tetap sama) ...
    st.title("📊 Dashboard IT Asset Umara Group")
    # ... [KODE DASHBOARD LO] ...
    # (Karena keterbatasan karakter, pastikan lo copy bagian ini dari kode asli lo atau pakai yang sudah gua kasih sebelumnya)

# ... [BAGIAN MENU 2 SAMPAI 7 TETAP SAMA] ...

# 8. MENU BARU: Formulir Company Asset
elif menu == "📝 Formulir Company Asset":
    st.title("📝 Formulir Company Asset")
    if len(df) == 0: st.warning("Data kosong.")
    else:
        s_sn = st.selectbox("Pilih SN untuk Cetak Formulir:", df['Serial Number'].tolist())
        row = df[df['Serial Number'] == s_sn].iloc[0]
        
        st.markdown("---")
        form_template = f"""
        UMARA GROUP FOOD INDUSTRIES
        Formulir Company Asset (FR.ICT.04-00)
        
        User Information:
        - Name          : {row.get('User', '-')}
        - Business Unit : {row.get('Bu User', '-')}
        - Job Title     : {row.get('Job Title', '-')}
        
        Device Information:
        - Model         : {row.get('Model', '-')}
        - Serial Number : {row.get('Serial Number', '-')}
        - Notes         : {row.get('Notes', '-')}
        
        Ketentuan:
        - Laptop untuk kepentingan operasional perusahaan.
        - Tidak boleh dipindah tangankan tanpa seijin perusahaan.
        - Segala bentuk kerusakan ditanggung pengguna.
        
        Jakarta, {datetime.now().strftime('%d %B %Y')}
        ( {row.get('User', '-')} )
        """
        st.text_area("Preview Formulir:", value=form_template, height=400)
        st.download_button("📥 Download Formulir", form_template, f"Form_Asset_{s_sn}.txt")

# [KODE LAINNYA TETAP DIBAWAH]

import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"

# Ambil Secret
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    GITHUB_TOKEN = None

# Fungsi Data
def load_data():
    try:
        df = pd.read_csv(FILE_PATH, sep=";").fillna("")
        df.columns = df.columns.str.strip().str.title()
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
    payload = {"message": "Update", "content": encoded_content, "sha": sha if sha else None}
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

# Session State
if 'df' not in st.session_state: st.session_state.df = load_data()
df = st.session_state.df

# Sidebar Menu
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard", "👥 User Directory", "➕ Tambah", "✏️ Edit", "❌ Hapus", "📝 BAST"
])

# LOGIKA MENU (Harus dimulai dengan IF, baru ELIF)
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.dataframe(df, use_container_width=True)

elif menu == "👥 User Directory":
    st.title("👥 User Directory")
    if 'User' in df.columns:
        list_users = sorted([u for u in df['User'].unique() if u.strip() != ""])
        if list_users:
            s_user = st.selectbox("Pilih Karyawan:", list_users)
            u_data = df[df['User'] == s_user]
            p1, p2, p3 = st.columns(3)
            p1.metric("👤 Nama", s_user)
            p2.metric("💼 Jabatan", u_data.iloc[0].get('Job Title', '-'))
            p3.metric("💻 Aset", len(u_data))
            st.dataframe(u_data, use_container_width=True)

elif menu == "➕ Tambah":
    st.title("➕ Tambah Laptop")
    # ... (form tambah laptop kamu di sini) ...

elif menu == "✏️ Edit":
    st.title("✏️ Edit Data")

elif menu == "❌ Hapus":
    st.title("❌ Hapus Data")

elif menu == "📝 BAST":
    st.title("📝 Cetak BAST")

else:
    st.write("Silakan pilih menu di samping.")

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
        "message": "Update via Dashboard",
        "content": encoded_content, "sha": sha if sha else None
    }
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log", "📝 Formulir Company Asset"
])

if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    st.dataframe(df, use_container_width=True)

elif menu == "👥 User Directory":
    st.title("👥 User Directory & Histori")
    if 'User' in df.columns:
        list_users = sorted([u for u in df['User'].unique() if u.strip() != ""])
        s_user = st.selectbox("🎯 Pilih Nama Karyawan:", list_users)
        u_data = df[df['User'] == s_user]
        st.dataframe(u_data, use_container_width=True)

elif menu == "📝 Formulir Company Asset":
    st.title("📝 Formulir Company Asset")
    if not df.empty:
        s_sn = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
        row = df[df['Serial Number'] == s_sn].iloc[0]
        st.info("Preview Formulir:")
        st.text(f"User: {row.get('User')}\nSN: {row.get('Serial Number')}")
    else:
        st.warning("Data kosong.")

else:
    st.write("Silakan pilih menu di sidebar.")

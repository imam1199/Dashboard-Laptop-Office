import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

# Konfigurasi
GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

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
    payload = {"message": "Update Dashboard", "content": encoded_content, "sha": sha if sha else None}
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

if 'df' not in st.session_state: st.session_state.df = load_data()
df = st.session_state.df

# SIDEBAR MENU
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log", "📝 Formulir Company Asset"
])

# LOGIKA MENU (Harus berurutan biar dashboard muncul)
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    # ... (isi dengan kode dashboard lo yang lama) ...
    st.dataframe(df, use_container_width=True)

elif menu == "👥 User Directory":
    st.title("👥 User Directory")
    # ... (isi dengan kode user directory lo) ...
    st.write("User Directory Content")

elif menu == "➕ Tambah Laptop":
    st.title("➕ Tambah Laptop")
    # ... (isi dengan form tambah lo) ...

elif menu == "✏️ Edit Data":
    st.title("✏️ Edit Data")
    # ... (isi dengan edit form lo) ...

elif menu == "❌ Hapus Laptop":
    st.title("❌ Hapus Laptop")
    # ... (isi dengan hapus form lo) ...

elif menu == "📝 Cetak BAST":
    st.title("📝 Cetak BAST")
    # ... (isi dengan BAST lo) ...

elif menu == "📋 Audit Log":
    st.title("📋 Audit Log")
    # ... (isi dengan log lo) ...

elif menu == "📝 Formulir Company Asset":
    st.title("📝 Formulir Company Asset")
    s_sn = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
    row = df[df['Serial Number'] == s_sn].iloc[0]
    st.text_area("Preview:", value=f"User: {row.get('User')}\nSN: {s_sn}", height=300)

else:
    st.write("Menu tidak ditemukan.")

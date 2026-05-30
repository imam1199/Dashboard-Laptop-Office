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
        "message": f"Update Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content, "sha": sha if sha else None
    }
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
    status_counts = df['Status'].value_counts()
    
    # Metrik
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total", len(df))
    c2.metric("🟢 Tersedia", status_counts.get('Tersedia', 0))
    c3.metric("🔵 Di Pakai", status_counts.get('Di Pakai', 0))
    c4.metric("🟡 Perbaikan", status_counts.get('Perlu Perbaikan', 0))
    c5.metric("🔴 Rusak", status_counts.get('Rusak', 0))
    
    st.markdown("---")
    st.dataframe(df, use_container_width=True)
    
    # CHART DI BAWAH
    st.markdown("---")
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        st.subheader("🔹 Distribusi Status")
        fig_pie = px.pie(status_counts.reset_index(), values='count', names='Status', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_ch2:
        st.subheader("🔹 Top 5 Model Laptop")
        top_model = df['Model'].value_counts().head(5).reset_index()
        fig_bar = px.bar(top_model, x='Model', y='count', color='Model')
        st.plotly_chart(fig_bar, use_container_width=True)

# ... (Menu lainnya tetap sama)
elif menu == "👥 User Directory":
    st.title("👥 User Directory")
    s_user = st.selectbox("Pilih User:", sorted(df['User'].unique()))
    st.dataframe(df[df['User'] == s_user], use_container_width=True)

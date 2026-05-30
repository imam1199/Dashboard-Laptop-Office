import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"

# --- CONFIG & LOAD DATA ---
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
if 'audit_log' not in st.session_state: st.session_state.audit_log = []
df = st.session_state.df

def add_log(action, detail):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_log.insert(0, f"⏱️ [{ts}] - {action}: {detail}")

# --- SIDEBAR ---
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", "👥 User Directory", "➕ Tambah Laptop", 
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log"
])

# --- LOGIKA APLIKASI ---
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    status_counts = df['Status'].value_counts()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total", len(df))
    c2.metric("🟢 Tersedia", status_counts.get('Tersedia', 0))
    c3.metric("🔵 Di Pakai", status_counts.get('Di Pakai', 0))
    c4.metric("🟡 Perbaikan", status_counts.get('Perlu Perbaikan', 0))
    c5.metric("🔴 Rusak", status_counts.get('Rusak', 0))
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔹 Distribusi Status")
        fig_pie = px.pie(status_counts.reset_index(), values='count', names='Status', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.subheader("🔹 Top 5 Model Laptop")
        top_model = df['Model'].value_counts().head(5).reset_index()
        fig_bar = px.bar(top_model, x='Model', y='count', color='Model')
        st.plotly_chart(fig_bar, use_container_width=True)

elif menu == "👥 User Directory":
    st.title("👥 User Directory")
    users = sorted([u for u in df['User'].unique() if str(u).strip()])
    s_user = st.selectbox("Pilih User:", users)
    st.dataframe(df[df['User'] == s_user], use_container_width=True)

elif menu == "➕ Tambah Laptop":
    st.title("➕ Tambah Laptop Baru")
    with st.form("f_add"):
        m = st.text_input("Model"); sn = st.text_input("SN")
        bo = st.text_input("BU Owner"); bu = st.text_input("BU User")
        jt = st.text_input("Job Title"); us = st.text_input("User")
        stt = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"])
        tb = st.number_input("Tahun Beli", 2015, 2030, 2026); nt = st.text_area("Notes")
        if st.form_submit_button("Simpan"):
            nr = {"Model": m, "Serial Number": sn, "Bu Owner": bo, "Bu User": bu, "Job Title": jt, "User": us, "Status": stt, "Tahun Beli": tb, "Notes": nt}
            up_df = pd.concat([df, pd.DataFrame([nr])], ignore_index=True)
            if save_to_github(up_df): st.session_state.df = up_df; add_log("TAMBAH", sn); st.success("Tersimpan!"); st.rerun()

elif menu == "✏️ Edit Data":
    st.title("✏️ Edit Data Laptop")
    s_sn = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
    idx = df[df['Serial Number'] == s_sn].index[0]
    row = df.loc[idx]
    with st.form("f_ed"):
        em = st.text_input("Model", value=row.get('Model', ''))
        ebo = st.text_input("BU Owner", value=row.get('Bu Owner', ''))
        ebu = st.text_input("BU User", value=row.get('Bu User', ''))
        est = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"], index=["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"].index(row.get('Status', 'Tersedia')))
        if st.form_submit_button("Simpan Perubahan"):
            up_df = df.copy()
            up_df.at[idx, 'Model'] = em; up_df.at[idx, 'Bu Owner'] = ebo; up_df.at[idx, 'Bu User'] = ebu; up_df.at[idx, 'Status'] = est
            if save_to_github(up_df): st.session_state.df = up_df; add_log("EDIT", s_sn); st.success("Terupdate!"); st.rerun()

elif menu == "❌ Hapus Laptop":
    st.title("❌ Hapus Laptop")
    s_del = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
    if st.button("Ya, Hapus Permanen"):
        up_df = df.drop(df[df['Serial Number'] == s_del].index[0]).reset_index(drop=True)
        if save_to_github(up_df): st.session_state.df = up_df; add_log("HAPUS", s_del); st.rerun()

elif menu == "📝 Cetak BAST":
    st.title("📝 Dokumen BAST")
    p_sn = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
    li = df[df['Serial Number'] == p_sn].iloc[0]
    st.text_area("Pratinjau BAST", f"BAST untuk {li.get('User')}\nModel: {li.get('Model')}\nSN: {li.get('Serial Number')}", height=300)

elif menu == "📋 Audit Log":
    st.title("📋 Audit Log")
    for log in st.session_state.audit_log: st.write(log)

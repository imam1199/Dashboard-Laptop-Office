import streamlit as st
import pandas as pd
import requests
import base64
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

# --- CUSTOM CSS UNTUK TAMPILAN LEBIH RAPI ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {font-size: 24px;}
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

# ... (Fungsi load_data, save_to_github tetap sama seperti sebelumnya) ...

# --- SIDEBAR ---
with st.sidebar:
    st.title("💻 IT Asset Control")
    menu = st.radio("Navigasi:", ["Dashboard", "User Directory", "Tambah Data", "Edit/Hapus", "Audit Log"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Dashboard IT Asset")
    
    # 1. METRIK (Dibuat lebih proporsional)
    status_counts = st.session_state.df['Status'].value_counts()
    cols = st.columns(5)
    cols[0].metric("Total", len(st.session_state.df))
    cols[1].metric("Tersedia", status_counts.get('Tersedia', 0))
    cols[2].metric("Dipakai", status_counts.get('Di Pakai', 0))
    cols[3].metric("Perbaikan", status_counts.get('Perlu Perbaikan', 0))
    cols[4].metric("Rusak", status_counts.get('Rusak', 0))
    
    st.divider()

    # 2. SEARCH BAR & TABEL
    search = st.text_input("🔍 Cari Laptop (Masukkan kata kunci: User/SN/Model):")
    
    df_show = st.session_state.df
    if search:
        mask = df_show.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        df_show = df_show[mask]
    
    st.dataframe(df_show, use_container_width=True, height=400)
    
    # 3. EXPORT
    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Laporan (CSV)", csv, "data_aset_umara.csv", "text/csv")

# ... (bagian menu lainnya menyesuaikan dengan struktur di atas) ...

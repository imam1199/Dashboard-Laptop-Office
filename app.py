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
    "✏️ Edit Data", "❌ Hapus Laptop", "📝 Cetak BAST", "📋 Audit Log"
])

# 1. DASHBOARD & ANALYTICS
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    total_laptop = len(df)
    status_counts = df['Status'].value_counts() if 'Status' in df.columns else pd.Series()
    def get_count(name): return sum([v for k, v in status_counts.items() if name.lower() in k.lower()])
    
    dipakai, tersedia, perbaikan, rusak = get_count('Pakai'), get_count('Tersedia'), get_count('Perbaikan'), get_count('Rusak')
    df['Umur'] = datetime.now().year - df['Tahun Beli'].astype(int, errors='ignore')
    perlu_ganti = len(df[df['Umur'] >= 3])
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📦 Total", total_laptop)
    c2.metric("🟢 Tersedia", tersedia)
    c3.metric("🔵 Di Pakai", dipakai)
    c4.metric("🟡 Perbaikan", perbaikan)
    c5.metric("🔴 Rusak", rusak)
    c6.metric("⚠️ Perlu Ganti", perlu_ganti)
    
    st.markdown("---")
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        bo_opts = ["Semua"] + sorted(list(df['Bu Owner'].unique())) if 'Bu Owner' in df.columns else ["Semua"]
        s_bo = st.selectbox("Filter BU Owner:", bo_opts)
    with f2:
        s_st = st.selectbox("Filter Status:", ["Semua", "Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"])
    with f3:
        search = st.text_input("Cari (Model/SN/User):")
        
    d_df = df.copy()
    if s_bo != "Semua": d_df = d_df[d_df['Bu Owner'] == s_bo]
    if s_st != "Semua": d_df = d_df[d_df['Status'].str.contains(s_st, case=False, na=False)]
    if search: d_df = d_df[d_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
    if len(d_df) > 0:
        n_df = d_df.copy()
        n_df.insert(0, "No", range(1, len(n_df) + 1))
    else:
        n_df = d_df

    st.dataframe(n_df, use_container_width=True, hide_index=True)
    st.download_button("📥 Download Excel (CSV)", d_df.to_csv(index=False, sep=";").encode('utf-8'), "laporan.csv", "text/csv")
        
    st.markdown("---")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("##### 🔹 Distribusi Status (Pie Chart)")
        fig_p = px.pie(pd.DataFrame({'Status': ['Tersedia', 'Di Pakai', 'Perbaikan', 'Rusak'], 'Jumlah': [tersedia, dipakai, perbaikan, rusak]}), values='Jumlah', names='Status', hole=0.4)
        st.plotly_chart(fig_p, use_container_width=True)
    with ch2:
        st.markdown("##### 🔹 Top 5 Model Laptop")
        if 'Model' in df.columns and len(df) > 0:
            m_c = df['Model'].value_counts().head(5).reset_index()
            m_c.columns = ['Model', 'Total']
            st.plotly_chart(px.bar(m_c, x='Model', y='Total', color='Model'), use_container_width=True)

# 2. USER DIRECTORY (Tampilan Sejajar)
elif menu == "👥 User Directory":
    st.title("👥 User Directory & Histori")
    if 'User' in df.columns and len(df) > 0:
        list_users = sorted([u for u in df['User'].unique() if u.strip() != ""])
        if list_users:
            s_user = st.selectbox("🎯 Pilih Nama Karyawan:", list_users)
            u_data = df[df['User'] == s_user]
            
            st.markdown("---")
            # Kotak Sejajar menggunakan metric
            p1, p2, p3 = st.columns(3)
            p1.metric(label="👤 Nama Karyawan", value=s_user)
            p2.metric(label="💼 Jabatan", value=u_data.iloc[0].get('Job Title', '-'))
            p3.metric(label="💻 Aset Pegang", value=f"{len(u_data)} Unit")
            st.markdown("---")
                
            st.dataframe(u_data[['Model', 'Serial Number', 'Bu Owner', 'Status', 'Notes', 'Tahun Beli']], use_container_width=True, hide_index=True)
    else: st.warning("Data kosong.")

# 3. TAMBAH LAPTOP
elif menu == "➕ Tambah Laptop":
    st.title("➕ Tambah Laptop Baru")
    with st.form("f_add"):
        m = st.text_input("Model")
        sn = st.text_input("SN (Wajib Unik)")
        bo = st.text_input("BU Owner")
        bu = st.text_input("BU User")
        jt = st.text_input("Job Title")
        us = st.text_input("User")
        stt = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"])
        tb = st.number_input("Tahun Beli", 2015, 2030, 2026)
        nt = st.text_area("Notes")
        if st.form_submit_button("Simpan"):
            if not sn: st.error("SN wajib diisi!")
            elif sn.strip() in df['Serial Number'].values: st.error("SN sudah terdaftar!")
            else:
                nr = {"Model": m.strip(), "Serial Number": sn.strip(), "Bu Owner": bo.strip(), "Bu User": bu.strip(), "Job Title": jt.strip(), "User": us.strip(), "Status": stt, "Tahun Beli": tb, "Notes": nt}
                up_df = pd.concat([df, pd.DataFrame([nr])], ignore_index=True)
                if save_to_github(up_df):
                    st.session_state.df = up_df
                    add_log("TAMBAH", f"{m.strip()} ({sn.strip()})")
                    st.success("Tersimpan!")
                    st.rerun()

# 4. EDIT DATA
elif menu == "✏️ Edit Data":
    st.title("✏️ Edit Data Laptop")
    if len(df) == 0: st.warning("Data kosong.")
    else:
        s_sn = st.selectbox("Pilih SN:", df['Serial Number'].tolist())
        idx = df[df['Serial Number'] == s_sn].index[0]
        row = df.loc[idx]
        with st.form("f_ed"):
            em = st.text_input("Model", value=row.get('Model', ''))
            ebo = st.text_input("BU Owner", value=row.get('Bu Owner', ''))
            ebu = st.text_input("BU User", value=row.get('Bu User', ''))
            ejt = st.text_input("Job Title", value=row.get('Job Title', ''))
            eu = st.text_input("User", value=row.get('User', ''))
            est = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"], index=["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"].index(row.get('Status', 'Tersedia')))
            ent = st.text_area("Notes", value=row.get('Notes', ''))
            if st.form_submit_button("Simpan Perubahan"):
                up_df = df.copy()
                up_df.at[idx, 'Model'], up_df.at[idx, 'Bu Owner'], up_df.at[idx, 'Bu User'] = em.strip(), ebo.strip(), ebu.strip()
                up_df.at[idx, 'Job Title'], up_df.at[idx, 'User'], up_df.at[idx, 'Status'], up_df.at[idx, 'Notes'] = ejt.strip(), eu.strip(), est, ent
                if save_to_github(up_df):
                    st.session_state.df = up_df
                    add_log("EDIT", f"SN {s_sn}")
                    st.success("Terupdate!")
                    st.rerun()

# 5. HAPUS LAPTOP
elif menu == "❌ Hapus Laptop":
    st.title("❌ Hapus Laptop")
    if len(df) == 0: st.warning("Data kosong.")
    else:
        s_del = st.selectbox("Pilih SN Dihapus:", df['Serial Number'].tolist())
        if st.button("Ya, Hapus Permanen"):
            idx = df[df['Serial Number'] == s_del].index[0]
            up_df = df.drop(idx).reset_index(drop=True)
            if save_to_github(up_df):
                st.session_state.df = up_df
                add_log("HAPUS", s_del)
                st.success("Terhapus!")
                st.rerun()

# 6. CETAK BAST
elif menu == "📝 Cetak BAST":
    st.title("📝 Dokumen BAST")
    if len(df) == 0: st.warning("Data kosong.")
    else:
        p_sn = st.selectbox("Pilih SN untuk BAST:", df['Serial Number'].tolist())
        li = df[df['Serial Number'] == p_sn].iloc[0]
        text = f"""========================================================================
                  BERITA ACARA SERAH TERIMA ASET IT - UMARA GROUP
========================================================================
Hari / Tanggal : {datetime.now().strftime('%A, %d %B %Y')}
Pihak I (IT)   : IT Support Specialist Umara Group
Pihak II (User): {li.get('User', '-')} ({li.get('Bu User', '-')})

Detail Aset:
- Model Laptop : {li.get('Model', '-')}
- Serial Number: {li.get('Serial Number', '-')}
- Status / Note: {li.get('Status', '-')} / {li.get('Notes', '-')}

Jakarta, {datetime.now().strftime('%d %B %Y')}
Yang Menyerahkan,          Yang Menerima,

( ________________ )      ( ________________ )"""
        st.text_area("Pratinjau Surat BAST", value=text, height=300)
        st.download_button("🖨️ Download BAST (.txt)", text, f"BAST_{li.get('User','User')}.txt")

# 7. AUDIT LOG
elif menu == "📋 Audit Log":
    st.title("📋 Audit Log")
    if not st.session_state.audit_log: st.info("Belum ada aktivitas.")
    else:
        for log in st.session_state.audit_log: st.write(log)

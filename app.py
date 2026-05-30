import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

# Alamat repository sesuai dengan GitHub kamu
GITHUB_REPO = "imam1199/Dashboard-laptop-Office"  
FILE_PATH = "laporan_laptop_terbaru.csv"

# Ambil token keamanan dari Streamlit Secrets
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    GITHUB_TOKEN = None

# Fungsi untuk membaca data awal dengan pembersihan total
def load_data():
    try:
        df = pd.read_csv(FILE_PATH, sep=";").fillna("")
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.title()
        
        # Sikat spasi gaib di isi kolom krusial
        for col in ['Status', 'Model', 'Serial Number', 'Bu Owner', 'Bu User']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                
        # FITUR 1: Tambah data umur depresiasi bayangan jika belum ada kolom tahun beli
        # (Kita asumsikan default pembelian atau input manual ke depan)
        if 'Tahun Beli' not in df.columns:
            df['Tahun Beli'] = 2023 # Default tahun buat laptop lama
            
        return df
    except:
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Notes", "Tahun Beli"])

# Fungsi Otomatis untuk Save Data Kembali ke GitHub CSV
def save_to_github(dataframe):
    if not GITHUB_TOKEN:
        st.error("Gagal menyimpan ke cloud: GITHUB_TOKEN belum dipasang di Secrets!")
        return False
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha", "") if res.status_code == 200 else ""
        
    csv_content = dataframe.to_csv(index=False, sep=";")
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": f"Update data laptop via Dashboard IT Asset - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content,
        "sha": sha if sha else None
    }
    
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

# Inisialisasi data ke dalam session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

df = st.session_state.df

# Tambahkan log bawaan biar gak kosong pas di-refresh
def add_log(action, detail):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_log.insert(0, f"⏱️ [{timestamp}] - {action}: {detail}")

# Menu Navigasi di Sidebar
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", [
    "📊 Dashboard & Analytics", 
    "➕ Tambah Laptop", 
    "✏️ Edit / Update Data", 
    "❌ Hapus Laptop", 
    "📝 Cetak Surat BAST", 
    "📋 Audit Log Perubahan"
])

# 1. MENU DASHBOARD & ANALYTICS
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    st.write("Sistem Monitoring, Analisis, dan Manajemen Inventaris Laptop secara Real-Time.")
    
    # Ringkasan Angka Utama
    st.markdown("### 📈 Ringkasan Status Laptop")
    total_laptop = len(df)
    
    status_counts = df['Status'].value_counts() if 'Status' in df.columns else pd.Series()
    def get_count(name): return sum([v for k, v in status_counts.items() if name.lower() in k.lower()])
    
    dipakai, tersedia, perbaikan, rusak = get_count('Pakai'), get_count('Tersedia'), get_count('Perbaikan'), get_count('Rusak')
    
    # HITUNG DEPRESIASI UMUR LAPTOP (Asumsi masa pakai ideal = 3 tahun)
    tahun_sekarang = datetime.now().year
    df['Umur Aset (Tahun)'] = tahun_sekarang - df['Tahun Beli'].astype(int, errors='ignore')
    perlu_ganti = len(df[df['Umur Aset (Tahun)'] >= 3])
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📦 Total Laptop", total_laptop)
    col2.metric("🟢 Tersedia", tersedia)
    col3.metric("🔵 Di Pakai", dipakai)
    col4.metric("🟡 Perbaikan", perbaikan)
    col5.metric("🔴 Rusak", rusak)
    col6.metric("⚠️ Perlu Ganti Baru", perlu_ganti, help="Laptop berumur >= 3 tahun (Waktunya Peremajaan Aset)")
    
    st.markdown("---")
    
    # FITUR FILTER CEPAT BERDASARKAN BU
    st.subheader("🔍 Cari & Filter Data")
    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    
    with f_col1:
        bu_owner_opts = ["Semua"] + sorted(list(df['Bu Owner'].unique())) if 'Bu Owner' in df.columns else ["Semua"]
        selected_bu_owner = st.selectbox("Filter BU Owner:", bu_owner_opts)
    with f_col2:
        status_opts = ["Semua", "Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"]
        selected_status = st.selectbox("Filter Status Aset:", status_opts)
    with f_col3:
        search = st.text_input("Pencarian Fleksibel (Ketik Model/SN/User):")
        
    # Proses filtering data
    display_df = df.copy()
    if selected_bu_owner != "Semua":
        display_df = display_df[display_df['Bu Owner'] == selected_bu_owner]
    if selected_status != "Semua":
        display_df = display_df[display_df['Status'].str.contains(selected_status, case=False, na=False)]
    if search:
        display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
    # Tampilkan kolom nomor urut (1, 2, 3...)
    if len(display_df) > 0:
        numbered_df = display_df.copy()
        numbered_df.insert(0, "No", range(1, len(numbered_df) + 1))
    else:
        numbered_df = display_df

    st.dataframe(
        numbered_df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "No": st.column_config.NumberColumn("No", width="small"),
            "Notes": st.column_config.TextColumn("Notes", width="large"),
            "Tahun Beli": st.column_config.NumberColumn("Tahun Beli", format="%d")
        }
    )
    
    # Tombol Download Data
    csv_to_download = display_df.to_csv(index=False, sep=";").encode('utf-8')
    st.download_button(
        label="📥 Download Hasil Filter ke Excel (CSV)", data=csv_to_download,
        file_name="laporan_it_asset_umara.csv", mime="text/csv"
    )
        
    st.markdown("---")
    
    # FITUR GRAFIK PIE & BAR BERDAMPINGAN (PLOTLY INTERAKTIF)
    st.subheader("📊 Visualisasi Analytics Interaktif")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("##### 🔹 Persentase Distribusi Status (Pie Chart)")
        status_pie = pd.DataFrame({'Status Aset': ['Tersedia', 'Di Pakai', 'Perlu Perbaikan', 'Rusak'], 'Jumlah': [tersedia, dipakai, perbaikan, rusak]})
        fig_pie = px.pie(status_pie, values='Jumlah', names='Status Aset', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with chart_col2:
        st.markdown("##### 🔹 Top 5 Model Laptop Terbanyak di Kantor")
        if 'Model' in df.columns and len(df) > 0:
            model_counts = df['Model'].value_counts().head(5).reset_index()
            model_counts.columns = ['Model Laptop', 'Total']
            fig_bar = px.bar(model_counts, x='Model Laptop', y='Total', color='Model Laptop', color_discrete_sequence=px.colors.qualitative.Safe)
            fig_bar.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=300)
            st.plotly_chart(fig_bar, use_container_width=True)

# 2. MENU TAMBAH LAPTOP
elif menu == "➕ Tambah Laptop":
    st.title("➕ Tambah Laptop Baru")
    with st.form("form_tambah"):
        model = st.text_input("Model Laptop")
        sn = st.text_input("Serial Number (Wajib Unik)")
        bu_owner = st.text_input("BU Owner")
        bu_user = st.text_input("BU User")
        job_title = st.text_input("Job Title")
        user = st.text_input("Nama User")
        status = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"])
        thn_beli = st.number_input("Tahun Pembelian", min_value=2015, max_value=2030, value=2026)
        notes = st.text_area("Notes / Catatan")
        
        submit = st.form_submit_button("Simpan Data Baru")
        if submit:
            if not sn: st.error("Serial Number wajib diisi!")
            elif sn.strip() in df['Serial Number'].values: st.error("Serial Number sudah terdaftar!")
            else:
                new_row = {col: "" for col in df.columns}
                new_row['Model'], new_row['Serial Number'] = model.strip(), sn.strip()
                new_row['Bu Owner'], new_row['Bu User'] = bu_owner.strip(), bu_user.strip()
                new_row['Job Title'], new_row['User'], new_row['Status'] = job_title, user, status
                new_row['Tahun Beli'], new_row['Notes'] = thn_beli, notes
                
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                if save_to_github(updated_df):
                    st.session_state.df = updated_df
                    add_log("TAMBAH LAPTOP", f"Menambahkan laptop {model.strip()} dengan SN {sn.strip()}")
                    st.success("Berhasil disimpan permanen ke Cloud!")
                    st.rerun()

# 3. MENU EDIT / UPDATE DATA
elif menu == "✏️ Edit / Update Data":
    st.title("✏️ Edit & Update Data Laptop")
    if len(df) == 0: st.warning("Belum ada data laptop.")
    else:
        list_sn = df['Serial Number'].tolist()
        selected_sn = st.selectbox("Pilih Serial Number Laptop:", list_sn)
        idx = df[df['Serial Number'] == selected_sn].index[0]
        data_laptop = df.loc[idx]
        
        with st.form("form_edit"):
            edit_model = st.text_input("Model Laptop", value=data_laptop.get('Model', ''))
            edit_bu_owner = st.text_input("BU Owner", value=data_laptop.get('Bu Owner', ''))
            edit_bu_user = st.text_input("BU User", value=data_laptop.get('Bu User', ''))
            edit_user = st.text_input("Nama User", value=data_laptop.get('User', ''))
            edit_status = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"], index=["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"].index(data_laptop.get('Status', 'Tersedia')))
            edit_notes = st.text_area("Notes / Catatan", value=data_laptop.get('Notes', ''))
            
            save_changes = st.form_submit_button("Simpan Perubahan")
            if save_changes:
                updated_df = df.copy()
                updated_df.at[idx, 'Model'], updated_df.at[idx, 'Status'] = edit_model.strip(), edit_status
                updated_df.at[idx, 'Bu Owner'], updated_df.at[idx, 'Bu User'] = edit_bu_owner, edit_bu_user
                updated_df.at[idx, 'User'], updated_df.at[idx, 'Notes'] = edit_user, edit_notes
                
                if save_to_github(updated_df):
                    st.session_state.df = updated_df
                    add_log("EDIT DATA", f"Mengubah data laptop SN {selected_sn} (Status baru: {edit_status})")
                    st.success("Perubahan berhasil dikirim ke Cloud!")
                    st.rerun()

# 4. MENU HAPUS LAPTOP
elif menu == "❌ Hapus Laptop":
    st.title("❌ Hapus Laptop dari Inventaris")
    if len(df) == 0: st.warning("Belum ada data.")
    else:
        selected_sn_hapus = st.selectbox("Pilih Serial Number yang Mau Dihapus:", df['Serial Number'].tolist())
        idx_hapus = df[df['Serial Number'] == selected_sn_hapus].index[0]
        st.warning(f"Yakin ingin menghapus permanen Laptop SN {selected_sn_hapus}?")
        
        if st.button("Ya, Hapus Permanen"):
            mdl = df.loc[idx_hapus, 'Model']
            updated_df = df.drop(idx_hapus).reset_index(drop=True)
            if save_to_github(updated_df):
                st.session_state.df = updated_df
                add_log("HAPUS LAPTOP", f"Menghapus laptop {mdl} dengan SN {selected_sn_hapus}")
                st.success("Data berhasil dihapus dari Cloud!")
                st.rerun()

# 5. FITUR PREMIUM: SURAT BAST (BERITA ACARA SERAH TERIMA) OTOMATIS
elif menu == "📝 Cetak Surat BAST":
    st.title("📝 Dokumen Berita Acara Serah Terima (BAST)")
    st.write("Generate template surat serah terima aset IT Umara Group secara otomatis.")
    
    if len(df) == 0: st.warning("Data laptop kosong.")
    else:
        pilih_sn = st.selectbox("Pilih Serial Number Laptop untuk BAST:", df['Serial Number'].tolist())
        laptop_info = df[df['Serial Number'] == pilih_sn].iloc[0]
        
        st.markdown("### 📄 Draft Surat Serah Terima Aset")
        
        # Susunan Teks Surat BAST Resmi
        bast_text = f"""
        ========================================================================
                          BERITA ACARA SERAH TERIMA ASET IT
                                  UMARA GROUP
        ========================================================================
        Pada hari ini, {datetime.now().strftime('%A, %d %B %Y')}, kami yang bertandatangan di bawah ini:
        
        Pihak I (Yang Menyerahkan): IT Support Specialist Umara Group
        Pihak II (Yang Menerima)  : {laptop_info.get('User', '...................')} 
        Divisi/BU                 : {laptop_info.get('Bu User', '...................')}
        
        Pihak I menyerahkan fasilitas kantor berupa aset laptop kepada Pihak II, dengan rincian berikut:
        - Merk / Model Laptop   : {laptop_info.get('Model', '-')}
        - Nomor Serial (SN)     : {laptop_info.get('Serial Number', '-')}
        - Status Aset Saat Ini  : {laptop_info.get('Status', '-')}
        - Catatan Tambahan      : {laptop_info.get('Notes', '-')}
        
        Syarat & Ketentuan Penggunaan:
        1. Pihak II wajib menjaga, merawat, dan bertanggungjawab penuh atas aset tersebut.
        2. Jika terjadi kerusakan akibat kelalaian pribadi, Pihak II wajib melapor ke divisi IT.
        3. Aset harus dikembalikan ke IT apabila karyawan yang bersangkutan mengundurkan diri.
        
        Demikian Berita Acara ini dibuat dengan sebenar-benarnya untuk digunakan sebagaimana mestinya.
        
        Jakarta, {datetime.now().strftime('%d %B %Y')}
        
           Yang Menyerahkan,                          Yang Menerima,
        
        
        ( ____________________ )                  ( ____________________ )
               Pihak I                                    Pihak II
        """
        
        st.text_area("Pratinjau Surat BAST (Bisa di-copy langsung)", value=bast_text, height=450)
        st.download_button(label="🖨️ Download Surat BAST (.txt)", data=bast_text, file_name=f"BAST_{laptop_info.get('User','User')}.txt")

# 6. FITUR PREMIUM: AUDIT LOG RIWAYAT PERUBAHAN
elif menu == "📋 Audit Log Perubahan":
    st.title("📋 Audit Log Riwayat Aktivitas Dashboard")
    st.write("Memantau setiap riwayat aksi tambah, edit, dan hapus yang dilakukan pada dashboard IT Asset.")
    
    if not st.session_state.audit_log:
        st.info("Belum ada riwayat aktivitas pada sesi ini. Log akan tercatat otomatis saat kamu mengubah data.")
    else:
        for log in st.session_state.audit_log:
            st.write(log)

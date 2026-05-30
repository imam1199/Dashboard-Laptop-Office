import streamlit as st
import pandas as pd

# 1. MENGGANTI NAMA DI TAB BROWSER
st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

# Fungsi untuk membaca data awal dari GitHub CSV
def load_data():
    try:
        df = pd.read_csv("laporan_laptop_terbaru.csv", sep=";").fillna("")
        df.columns = df.columns.str.strip()
        if 'Status' in df.columns:
            df['Status'] = df['Status'].str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Notes"])

# Inisialisasi data ke dalam session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# Menu Navigasi di Sidebar
st.sidebar.title("💻 IT Asset Management")
menu = st.sidebar.radio("Pilih Menu:", ["📊 Dashboard & Analytics", "➕ Tambah Laptop", "✏️ Edit / Update Data", "❌ Hapus Laptop"])

# 1. MENU DASHBOARD & ANALYTICS
if menu == "📊 Dashboard & Analytics":
    # 2. MENGGANTI JUDUL UTAMA DI HALAMAN DEPAN
    st.title("📊 Dashboard IT Asset Umara Group")
    st.write("Kelola, pantau, dan analisis grafik inventaris laptop Umara Group secara real-time.")
    
    st.markdown("### 📈 Ringkasan Status Laptop")
    
    # Menghitung jumlah berdasarkan status secara dinamis
    total_laptop = len(df)
    
    status_counts = df['Status'].value_counts() if 'Status' in df.columns else pd.Series()
    
    def get_count(status_name):
        return sum([val for idx, val in status_counts.items() if status_name.lower() in idx.lower()])

    dipakai = get_count('Pakai')
    tersedia = get_count('Tersedia')
    perbaikan = get_count('Perbaikan')
    rusak = get_count('Rusak')
    
    # Menampilkan 5 Kotak Metrik di Atas
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📦 Total Laptop", total_laptop)
    col2.metric("🟢 Tersedia", tersedia)
    col3.metric("🔵 Di Pakai", dipakai)
    col4.metric("🟡 Perlu Perbaikan", perbaikan)
    col5.metric("🔴 Rusak", rusak)
    
    st.markdown("---")
    
    # SEKSI TABEL DATA
    st.subheader("🔍 Cari & Detail Data Laptop")
    search = st.text_input("Masukkan Model, Serial Number, atau Nama User:")
    
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        st.dataframe(df[mask], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
        
    st.markdown("---")
    
    # SEKSI CHART VISUALISASI DI BAWAH
    st.subheader("📊 Grafik Distribusi Status Laptop")
    
    chart_data = pd.DataFrame({
        'Status': ['Tersedia', 'Di Pakai', 'Perlu Perbaikan', 'Rusak'],
        'Jumlah Laptop': [tersedia, dipakai, perbaikan, rusak]
    })
    
    st.bar_chart(data=chart_data, x='Status', y='Jumlah Laptop', use_container_width=True)

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
        notes = st.text_area("Notes / Catatan")
        
        submit = st.form_submit_button("Simpan Data Baru")
        if submit:
            if not sn:
                st.error("Serial Number tidak boleh kosong!")
            elif sn in df['Serial Number'].values:
                st.error("Serial Number sudah terdaftar!")
            else:
                new_row = {col: "" for col in df.columns}
                new_row['Model'] = model
                new_row['Serial Number'] = sn
                new_row['Bu Owner'] = bu_owner
                new_row['Bu User'] = bu_user
                new_row['Job Title'] = job_title
                new_row['User'] = user
                new_row['Status'] = status
                new_row['Notes'] = notes
                
                st.session_state.df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Laptop {model} berhasil ditambahkan!")
                st.rerun()

# 3. MENU EDIT / UPDATE DATA
elif menu == "✏️ Edit / Update Data":
    st.title("✏️ Edit & Update Data Laptop")
    
    if len(df) == 0:
        st.warning("Belum ada data laptop yang bisa diedit.")
    else:
        list_sn = df['Serial Number'].tolist()
        selected_sn = st.selectbox("Pilih Serial Number Laptop:", list_sn)
        
        idx = df[df['Serial Number'] == selected_sn].index[0]
        data_laptop = df.loc[idx]
        
        st.markdown("### Ubah Form di Bawah Ini:")
        with st.form("form_edit"):
            edit_model = st.text_input("Model Laptop", value=data_laptop.get('Model', ''))
            edit_bu_owner = st.text_input("BU Owner", value=data_laptop.get('Bu Owner', ''))
            edit_bu_user = st.text_input("BU User", value=data_laptop.get('Bu User', ''))
            edit_job_title = st.text_input("Job Title", value=data_laptop.get('Job Title', ''))
            edit_user = st.text_input("Nama User", value=data_laptop.get('User', ''))
            
            current_status = data_laptop.get('Status', 'Tersedia')
            status_options = ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"]
            default_status_idx = status_options.index(current_status) if current_status in status_options else 0
            edit_status = st.selectbox("Status", status_options, index=default_status_idx)
            
            edit_notes = st.text_area("Notes / Catatan", value=data_laptop.get('Notes', ''))
            
            save_changes = st.form_submit_button("Simpan Perubahan Data")
            if save_changes:
                st.session_state.df.at[idx, 'Model'] = edit_model
                st.session_state.df.at[idx, 'Bu Owner'] = edit_bu_owner
                st.session_state.df.at[idx, 'Bu User'] = edit_bu_user
                st.session_state.df.at[idx, 'Job Title'] = edit_job_title
                st.session_state.df.at[idx, 'User'] = edit_user
                st.session_state.df.at[idx, 'Status'] = edit_status
                st.session_state.df.at[idx, 'Notes'] = edit_notes

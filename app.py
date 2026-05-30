import streamlit as st
import pandas as pd
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Office Laptop Dashboard", layout="wide")

CSV_FILE = "laporan_laptop_terbaru.csv"

# Fungsi untuk memuat data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE).fillna("")
    else:
        # Jika file tidak ada, buat template baru
        columns = ["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Handover Date", "Return Date", "Status", "Notes"]
        return pd.DataFrame(columns=columns)

# Fungsi untuk menyimpan data
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Inisialisasi data di session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("💻 Laptop Management")
menu = st.sidebar.radio("Pilih Menu:", ["Dashboard & View", "Tambah Laptop", "Edit / Hapus Laptop"])

# --- MENU 1: DASHBOARD & VIEW ---
if menu == "Dashboard & View":
    st.title("📊 Office Laptop Dashboard")
    st.write("Kelola dan pantau inventaris laptop kantor dengan mudah.")
    
    # Metrik Ringkas
    total_laptop = len(df)
    di_pakai = len(df[df['Status'].str.lower() == 'di pakai'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Laptop", total_laptop)
    col2.metric("Laptop Di Pakai", di_pakai)
    col3.metric("Model Terbanyak", df['Model'].value_counts().index[0] if not df.empty else "-")
    
    st.markdown("---")
    
    # Fitur Pencarian
    st.subheader("🔍 Cari Data Laptop")
    search_query = st.text_input("Masukkan Model, Serial Number, atau Nama User:")
    
    filtered_df = df.copy()
    if search_query:
        filtered_df = df[
            df['Model'].astype(str).str.contains(search_query, case=False) |
            df['Serial Number'].astype(str).str.contains(search_query, case=False) |
            df['User'].astype(str).str.contains(search_query, case=False)
        ]
        
    st.dataframe(filtered_df, use_container_width=True)

# --- MENU 2: TAMBAH LAPTOP ---
elif menu == "Tambah Laptop":
    st.title("➕ Tambah Laptop Baru")
    
    with st.form("form_tambah"):
        col1, col2 = st.columns(2)
        with col1:
            model = st.text_input("Model Laptop")
            sn = st.text_input("Serial Number (Harus Unik)")
            bu_owner = st.text_input("Bu Owner")
            bu_user = st.text_input("Bu User")
            job_title = st.text_input("Job Title")
        with col2:
            user = st.text_input("Nama User")
            handover = st.text_input("Handover Date (YYYY-MM-DD)")
            return_date = st.text_input("Return Date (YYYY-MM-DD)")
            status = st.selectbox("Status", ["Di Pakai", "Available", "Rusak", "Returned"])
            notes = st.text_area("Notes")
            
        submit = st.form_submit_button("Simpan Data")
        
        if submit:
            if not sn or not model:
                st.error("Model dan Serial Number wajib diisi!")
            elif sn in df['Serial Number'].values:
                st.error(f"Serial Number {sn} sudah terdaftar!")
            else:
                new_data = {
                    "Model": model, "Serial Number": sn, "Bu Owner": bu_owner,
                    "Bu User": bu_user, "Job Title": job_title, "User": user,
                    "Handover Date": handover, "Return Date": return_date,
                    "Status": status, "Notes": notes
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df)
                st.session_state.df = df
                st.success("Data laptop berhasil ditambahkan!")
                st.balloons()

# --- MENU 3: EDIT / HAPUS LAPTOP ---
elif menu == "Edit / Hapus Laptop":
    st.title("⚙️ Edit atau Hapus Data Laptop")
    
    if df.empty:
        st.warning("Belum ada data yang bisa diedit.")
    else:
        # Pilih berdasarkan SN karena SN itu unik
        sn_list = df['Serial Number'].tolist()
        selected_sn = st.selectbox("Pilih Serial Number Laptop yang akan diubah:", sn_list)
        
        # Ambil data laptop yang dipilih
        laptop_idx = df[df['Serial Number'] == selected_sn].index[0]
        row = df.loc[laptop_idx]
        
        st.markdown("### Update Data")
        with st.form("form_edit"):
            col1, col2 = st.columns(2)
            with col1:
                model = st.text_input("Model Laptop", value=row['Model'])
                bu_owner = st.text_input("Bu Owner", value=row['Bu Owner'])
                bu_user = st.text_input("Bu User", value=row['Bu User'])
                job_title = st.text_input("Job Title", value=row['Job Title'])
            with col2:
                user = st.text_input("Nama User", value=row['User'])
                handover = st.text_input("Handover Date", value=row['Handover Date'])
                return_date = st.text_input("Return Date", value=row['Return Date'])
                # Menyesuaikan index selectbox status
                status_options = ["Di Pakai", "Available", "Rusak", "Returned"]
                current_status = row['Status'] if row['Status'] in status_options else "Di Pakai"
                status = st.selectbox("Status", status_options, index=status_options.index(current_status))
                notes = st.text_area("Notes", value=row['Notes'])
                
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                update_btn = st.form_submit_button("🔄 Update Data")
            with col_btn2:
                delete_btn = st.form_submit_button("🚨 HAPUS LAPTOP INI", type="primary")
                
            if update_btn:
                df.loc[laptop_idx] = [model, selected_sn, bu_owner, bu_user, job_title, user, handover, return_date, status, notes]
                save_data(df)
                st.session_state.df = df
                st.success("Data sukses di-update!")
                
            if delete_btn:
                df = df.drop(laptop_idx).reset_index(drop=True)
                save_data(df)
                st.session_state.df = df
                st.success("Data laptop berhasil dihapus dari sistem!")
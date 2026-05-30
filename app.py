import streamlit as st
import pandas as pd

st.set_page_config(page_title="Laptop Management", layout="wide")

# Fungsi untuk membaca data dengan pembatas titik koma (;)
def load_data():
    # Membaca file dan membersihkan spasi tak terlihat di nama kolom
    df = pd.read_csv("laporan_laptop_terbaru.csv", sep=";").fillna("")
    df.columns = df.columns.str.strip()
    return df

# Inisialisasi data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.sidebar.title("💻 Laptop Management")
menu = st.sidebar.radio("Pilih Menu:", ["Dashboard & View", "Tambah Laptop"])

if menu == "Dashboard & View":
    st.title("📊 Office Laptop Dashboard")
    st.write("Kelola dan pantau inventaris laptop kantor dengan mudah.")
    
    # Metrik Dashboard
    total_laptop = len(df)
    
    # Cek kolom status dengan aman
    if 'Status' in df.columns:
        dipakai = len(df[df['Status'].str.contains('Pakai', case=False, na=False)])
    else:
        dipakai = 0
        
    col1, col2 = st.columns(2)
    col1.metric("Total Laptop", total_laptop)
    col2.metric("Laptop Di Pakai", dipakai)
    
    st.markdown("---")
    st.subheader("🔍 Cari Data Laptop")
    search = st.text_input("Masukkan Model, Serial Number, atau Nama User:")
    
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        st.dataframe(df[mask], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "Tambah Laptop":
    st.title("➕ Tambah Laptop Baru")
    with st.form("form_tambah"):
        model = st.text_input("Model Laptop")
        sn = st.text_input("Serial Number")
        bu_owner = st.text_input("BU Owner")
        status = st.selectbox("Status", ["Tersedia", "Di Pakai", "Perlu Perbaikan"])
        
        submit = st.form_submit_button("Simpan Data")
        if submit:
            new_row = {col: "" for col in df.columns}
            new_row['Model'] = model
            new_row['Serial Number'] = sn
            new_row['Bu Owner'] = bu_owner
            new_row['Status'] = status
            
            new_data = pd.DataFrame([new_row])
            st.session_state.df = pd.concat([df, new_data], ignore_index=True)
            st.success("Data berhasil ditambahkan di dashboard!")

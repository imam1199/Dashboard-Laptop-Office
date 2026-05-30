import streamlit as st
import pandas as pd
import requests
import base64

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
        
        # Bersihkan spasi gaib di nama kolom
        df.columns = df.columns.str.strip()
        # Paksa semua nama kolom berformat Title Case
        df.columns = df.columns.str.title()
        
        # Bersihkan spasi di isi data kolom penting
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip()
        if 'Model' in df.columns:
            df['Model'] = df['Model'].astype(str).str.strip()
        if 'Serial Number' in df.columns:
            df['Serial Number'] = df['Serial Number'].astype(str).str.strip()
            
        return df
    except:
        return pd.DataFrame(columns=["Model", "Serial Number", "Bu Owner", "Bu User", "Job Title", "User", "Status", "Notes"])

# Fungsi Otomatis untuk Save Data Kembali ke GitHub CSV
def save_to_github(dataframe):
    if not GITHUB_TOKEN:
        st.error("Gagal menyimpan ke cloud: GITHUB_TOKEN belum dipasang di Secrets!")
        return False
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Ambil SHA file lama (wajib untuk update file di GitHub API)
    res = requests.get(url, headers=headers)
    sha = ""
    if res.status_code == 200:
        sha = res.json().get("sha", "")
        
    # Konversi dataframe ke format string CSV dengan pemisah titik koma (;)
    csv_content = dataframe.to_csv(index=False, sep=";")
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": "Update data laptop via Dashboard IT Asset Umara Group",
        "content": encoded_content,
        "sha": sha if sha else None
    }
    
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return True
    else:
        st.error(f"Gagal push ke GitHub (Error {response.status_code}): {response.text}")
        return False

# Inisialisasi data ke dalam session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# Menu Navigasi di Sidebar
st.sidebar.title("💻 IT Asset Management")
menu = st.sidebar.radio("Pilih Menu:", ["📊 Dashboard & Analytics", "➕ Tambah Laptop", "✏️ Edit / Update Data", "❌ Hapus Laptop"])

# 1. MENU DASHBOARD & ANALYTICS
if menu == "📊 Dashboard & Analytics":
    st.title("📊 Dashboard IT Asset Umara Group")
    st.write("Kelola, pantau, dan analisis grafik inventaris laptop Umara Group secara real-time.")
    
    st.markdown("### 📈 Ringkasan Status Laptop")
    
    total_laptop = len(df)
    status_counts = df['Status'].value_counts() if 'Status' in df.columns else pd.Series()
    
    def get_count(status_name):
        return sum([val for idx, val in status_counts.items() if status_name.lower() in idx.lower()])

    dipakai = get_count('Pakai')
    tersedia = get_count('Tersedia')
    perbaikan = get_count('Perbaikan')
    rusak = get_count('Rusak')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📦 Total Laptop", total_laptop)
    col2.metric("🟢 Tersedia", tersedia)
    col3.metric("🔵 Di Pakai", dipakai)
    col4.metric("🟡 Perlu Perbaikan", perbaikan)
    col5.metric("🔴 Rusak", rusak)
    
    st.markdown("---")
    
    st.subheader("🔍 Cari & Detail Data Laptop")
    search = st.text_input("Masukkan Model, Serial Number, atau Nama User:")
    
    # Filter data berdasarkan pencarian
    display_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
    
    # FITUR BARU: Membuat nomor urut otomatis (1, 2, 3...) di sebelah kiri kolom Model
    if len(display_df) > 0:
        # Duplikat dataframe biar gak merusak data asli
        numbered_df = display_df.copy()
        # Sisipkan kolom "No" di urutan paling pertama (indeks 0)
        numbered_df.insert(0, "No", range(1, len(numbered_df) + 1))
    else:
        numbered_df = display_df

    # Tampilkan dataframe yang sudah diberi nomor urut
    st.dataframe(
        numbered_df, 
        use_container_width=True,
        hide_index=True,  # Menyembunyikan indeks bawaan angka 0 Streamlit
        column_config={
            "No": st.column_config.NumberColumn("No", width="small"),
            "Notes": st.column_config.TextColumn("Notes", width="large"),
            "Model": st.column_config.TextColumn("Model", width="medium"),
            "Serial Number": st.column_config.TextColumn("Serial Number", width="medium")
        }
    )
    
    # Tombol Download CSV
    csv_to_download = display_df.to_csv(index=False, sep=";").encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV (Excel Format)",
        data=csv_to_download,
        file_name="laporan_laptop_terbaru_downloaded.csv",
        mime="text/csv",
        help="Klik untuk mengunduh data yang tampil di tabel atas dalam format CSV/Excel"
    )
        
    st.markdown("---")
    st.subheader("📊 Analytics Visualisasi Aset")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("##### 🔹 Distribusi Berdasarkan Status")
        status_chart_data = pd.DataFrame({'Status': ['Tersedia', 'Di Pakai', 'Perlu Perbaikan', 'Rusak'], 'Jumlah': [tersedia, dipakai, perbaikan, rusak]})
        st.bar_chart(data=status_chart_data, x='Status', y='Jumlah', use_container_width=True)
        
    with chart_col2:
        st.markdown("##### 🔹 Top 5 Model Laptop Terbanyak")
        if 'Model' in df.columns and len(df) > 0:
            model_counts = df['Model'].value_counts().head(5).reset_index()
            model_counts.columns = ['Model Laptop', 'Jumlah']
            st.bar_chart(data=model_counts, x='Model Laptop', y='Jumlah', use_container_width=True)

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
            elif sn.strip() in df['Serial Number'].values:
                st.error("Serial Number sudah terdaftar!")
            else:
                new_row = {col: "" for col in df.columns}
                new_row['Model'] = model.strip()
                new_row['Serial Number'] = sn.strip()
                new_row['Bu Owner'] = bu_owner
                new_row['Bu User'] = bu_user
                new_row['Job Title'] = job_title
                new_row['User'] = user
                new_row['Status'] = status
                new_row['Notes'] = notes
                
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                with st.spinner("Menyimpan data baru ke cloud GitHub..."):
                    if save_to_github(updated_df):
                        st.session_state.df = updated_df
                        st.success(f"Laptop {model} berhasil disimpan permanen ke GitHub cloud!")
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
        
        with st.form("form_edit"):
            edit_model = st.text_input("Model Laptop", value=data_laptop.get('Model', ''))
            edit_bu_owner = st.text_input("BU Owner", value=data_laptop.get('Bu Owner', ''))
            edit_bu_user = st.text_input("

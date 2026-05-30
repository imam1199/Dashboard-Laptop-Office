# 2. USER DIRECTORY (Tampilan lebih minimalis)
elif menu == "👥 User Directory":
    st.title("👥 User Directory & Histori")
    if 'User' in df.columns and len(df) > 0:
        list_users = sorted([u for u in df['User'].unique() if u.strip() != ""])
        if list_users:
            s_user = st.selectbox("🎯 Pilih Nama Karyawan:", list_users)
            u_data = df[df['User'] == s_user]
            
            st.markdown("---")
            # Kotak Sejajar dengan ukuran teks yang lebih kecil/proporsional
            p1, p2, p3 = st.columns(3)
            
            with p1:
                st.caption("Nama Karyawan")
                st.write(f"##### {s_user}")
            with p2:
                st.caption("Jabatan / Divisi")
                st.write(f"##### {u_data.iloc[0].get('Job Title', '-')}")
            with p3:
                st.caption("Total Aset")
                st.write(f"##### {len(u_data)} Unit")
            
            st.markdown("---")
            st.dataframe(u_data[['Model', 'Serial Number', 'Bu Owner', 'Status', 'Notes', 'Tahun Beli']], use_container_width=True, hide_index=True)
    else: st.warning("Data kosong.")

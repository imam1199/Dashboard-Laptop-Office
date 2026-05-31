import streamlit as st
import pandas as pd
import requests
import base64
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard IT Asset Umara Group", layout="wide")

GITHUB_REPO = "imam1199/Dashboard-laptop-Office"
FILE_PATH = "laporan_laptop_terbaru.csv"
LOG_PATH = "audit_log.csv"
BU_OPTIONS = ["UNB", "UCR", "RNB", "LBI", "SMI", "UMK"]
STATUS_OPTIONS = ["Tersedia", "Di Pakai", "Perlu Perbaikan", "Rusak"]

# --- LOAD DATA ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    GITHUB_TOKEN = None

def load_data(path):
    try:
        df = pd.read_csv(path, sep=";").fillna("")
        df.columns = df.columns.str.strip().str.title()
        return df
    except:
        return pd.DataFrame()

def save_to_github(dataframe, path):
    if not GITHUB_TOKEN: return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha", "") if res.status_code == 200 else ""
    csv_content = dataframe.to_csv(index=False, sep=";")
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    payload = {"message": "Update Data", "content": encoded_content, "sha": sha if sha else None}
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

if 'df' not in st.session_state: st.session_state.df = load_data(FILE_PATH)
if 'audit_df' not in st.session_state: st.session_state.audit_df = load_data(LOG_PATH)

def add_log(action, detail):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{"Timestamp": ts, "Action": action, "Detail": detail}])
    updated_logs = pd.concat([new_log, st.session_state.audit_df], ignore_index=True)
    if save_to_github(updated_logs, LOG_PATH): st.session_state.audit_df = updated_logs

# --- UI ---
st.sidebar.title("💻 IT Asset Umara Group")
menu = st.sidebar.radio("Pilih Menu:", ["📊 Dashboard", "➕ Tambah", "✏️ Edit", "❌ Hapus", "📋 Log"])

if menu == "📊 Dashboard":
    st.title("📊 Dashboard IT Asset")
    if not st.session_state.df.empty:
        st.dataframe(st.session_state.df, use_container_width=True)
    else:
        st.write("Data kosong.")

elif menu == "➕ Tambah":
    with st.form("f_add"):
        m = st.text_input("Model")
        sn = st.text_input("SN")
        stt = st.selectbox("Status", STATUS_OPTIONS)
        if st.form_submit_button("Simpan"):
            nr = {"Model": m, "Serial Number": sn, "Status": stt}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([nr])], ignore_index=True)
            if save_to_github(st.session_state.df, FILE_PATH): st.rerun()

elif menu == "✏️ Edit":
    if not st.session_state.df.empty:
        s_sn = st.selectbox("Pilih SN:", st.session_state.df['Serial Number'].tolist())
        idx = st.session_state.df[st.session_state.df['Serial Number'] == s_sn].index[0]
        row = st.session_state.df.loc[idx]
        with st.form("f_ed"):
            em = st.text_input("Model", value=row.get('Model', ''))
            est = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row.get('Status', 'Tersedia')) if row.get('Status') in STATUS_OPTIONS else 0)
            if st.form_submit_button("Update"):
                st.session_state.df.at[idx, 'Model'] = em
                st.session_state.df.at[idx, 'Status'] = est
                if save_to_github(st.session_state.df, FILE_PATH): st.rerun()

elif menu == "📋 Log":
    st.dataframe(st.session_state.audit_df)

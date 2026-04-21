import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Konfigurasi Zona Waktu WITA
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="Converter Laporan VCare", layout="wide")

st.title("📊 VCare Excel to Report Converter")

# --- Bagian Filter & Download ---
st.sidebar.header("Pengaturan Data")

# Pilihan Tanggal (Default hari ini WITA)
selected_date = st.sidebar.date_input("Pilih Tanggal Laporan", now_wita)
date_str = selected_date.strftime('%d-%b-%Y')

# Konstruksi URL berdasarkan input
download_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"

st.sidebar.markdown(f"[🔗 Klik untuk Download File VCare]({download_url})")
st.sidebar.info("Catatan: Pastikan Anda sudah login ke VCare di browser ini sebelum klik link di atas.")

# --- Bagian Upload ---
uploaded_file = st.file_uploader("Upload file Excel yang sudah didownload", type=["xlsx", "xls"])

if uploaded_file:
    # Membaca Data
    df = pd.read_excel(uploaded_file)
    
    # Logika Pemrosesan (Asumsi kolom bernama 'SAE' dan 'Status' atau sejenisnya)
    # Anda mungkin perlu menyesuaikan nama kolom sesuai isi file Excel asli
    if 'SAE' in df.columns:
        # Menghitung progress per SAE
        report_df = df.groupby('SAE').size().reset_index(name='Progres PM')
        
        # Total baris
        total_pm = report_df['Progres PM'].sum()
        
        # Menampilkan Tabel ala Laporan
        st.subheader(f"Rekap Progres PM - {date_str}")
        
        # Styling Tabel
        def highlight_zero(val):
            color = '#f1948a' if val == 0 else 'white'
            return f'background-color: {color}'

        # Menambahkan baris Total di akhir
        # (Untuk tampilan web, kita gunakan dataframe styling)
        st.table(report_df.style.applymap(highlight_zero, subset=['Progres PM']))
        
        # Ringkasan Target
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total PM Saat Ini", total_pm)
        with col2:
            st.metric("Minimal Target", "30", delta=int(total_pm) - 30)
            
    else:
        st.error("Kolom 'SAE' tidak ditemukan dalam file. Pastikan file benar.")

else:
    st.write("Silakan download file dari VCare menggunakan link di samping, lalu upload ke sini.")

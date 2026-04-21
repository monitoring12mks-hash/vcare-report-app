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
st.sidebar.info("Catatan: Pastikan Anda sudah login ke VCare di browser sebelum mengunduh.")

# --- Bagian Upload ---
uploaded_file = st.file_uploader("Upload file Excel yang sudah didownload", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Membaca Data
        df = pd.read_excel(uploaded_file)
        
        # Membersihkan spasi pada nama kolom jika ada
        df.columns = df.columns.str.strip()

        # Menggunakan kolom 'Engineer' sesuai struktur file Anda
        target_column = 'Engineer'

        if target_column in df.columns:
            # Menghitung progress per Engineer
            # Menggunakan value_counts agar mendapatkan daftar semua nama dan jumlah barisnya
            report_df = df[target_column].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM'] # Menamai kolom hasil agar sesuai gambar
            
            # Mengurutkan berdasarkan nama secara alfabetis
            report_df = report_df.sort_values(by='SAE')
            
            # Total baris
            total_pm = report_df['Progres PM'].sum()
            
            # Menampilkan Tabel ala Laporan
            st.subheader(f"Rekap Progres PM - {date_str}")
            
            # Styling Tabel: Warna merah untuk progres 0
            def highlight_zero(val):
                color = '#f1948a' if val == 0 else 'white'
                return f'background-color: {color}'

            # Menampilkan tabel
           # Styling Tabel: Warna merah untuk progres 0
            def highlight_zero(val):
                color = '#f1948a' if val == 0 else ''
                return f'background-color: {color}'

            # Menggunakan .map() untuk Pandas versi terbaru, atau .applymap() untuk versi lama
            if hasattr(report_df.style, 'map'):
                styled_df = report_df.style.map(highlight_zero, subset=['Progres PM'])
            else:
                styled_df = report_df.style.applymap(highlight_zero, subset=['Progres PM'])

            # Menampilkan tabel
            st.table(styled_df)
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")

else:
    st.info("Silakan download file dari VCare terlebih dahulu, lalu upload di sini untuk membuat laporan.")

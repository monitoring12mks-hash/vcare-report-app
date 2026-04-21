import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI WAKTU & HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="Converter Laporan VCare", layout="centered")

# Custom CSS untuk mempercantik tampilan
st.markdown("""
<style>
    .stTitle {
        color: #1E3A8A;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
    }
    /* Style untuk Header Tabel */
    thead th {
        background-color: #1E3A8A !important;
        color: white !important;
        font-weight: bold !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 VCare Excel to Report Converter")

# 2. SIDEBAR (FILTER & DOWNLOAD)
st.sidebar.header("Pengaturan Data")
selected_date = st.sidebar.date_input("Pilih Tanggal Laporan", now_wita)
date_str = selected_date.strftime('%d-%b-%Y')

download_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"

st.sidebar.markdown(f"**🔗 [Klik Download File VCare]({download_url})**")
st.sidebar.info("Pastikan Anda sudah login ke VCare sebelum mengunduh.")
st.sidebar.markdown("---")
st.sidebar.write("Zona Waktu: **WITA (Makassar)**")

# 3. PROSES FILE
uploaded_file = st.file_uploader("Upload file Excel yang sudah didownload", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Membaca data
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip() # Bersihkan spasi di nama kolom

        target_column = 'Engineer'

        if target_column in df.columns:
            # Hitung Progres per Engineer
            report_df = df[target_column].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM']
            report_df = report_df.sort_values(by='SAE')

            # Statistik untuk threshold warna
            max_val = report_df['Progres PM'].max()
            total_pm = report_df['Progres PM'].sum()

            st.markdown(f"### Rekap Progres PM - <span style='color:#1E3A8A;'>{date_str}</span>", unsafe_allow_html=True)

            # Fungsi Styling Baris
            def style_row(row):
                val = row['Progres PM']
                bg_color = ''
                text_color = 'black'
                font_weight = 'normal'
                
                if val == 0:
                    bg_color = '#f1948a' # Merah
                    text_color = 'white'
                    font_weight = 'bold'
                elif val == max_val and val > 0:
                    bg_color = '#2ecc71' # Hijau
                    text_color = 'white'
                    font_weight = 'bold'
                elif val <= 2 and val > 0:
                    bg_color = '#fff3cd' # Kuning
                
                return [f'background-color: {bg_color}; color: {text_color}; font-weight: {font_weight}'] * len(row)

            # Terapkan Style
            styled_df = report_df.style.apply(style_row, axis=1)

            # PROTEKSI ERROR: Hilangkan Index (Nomor Urut)
            if hasattr(styled_df, 'hide'):
                styled_df.hide() # Versi Pandas Baru
            else:
                styled_df.hide_index() # Versi Pandas Lama

            # Tampilkan Tabel
            st.table(styled_df)

            # 4. SUMMARY METRICS
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("✅ Total PM Berhasil", total_pm)
            with c2:
                target = 30
                selisih = int(total_pm) - target
                st.metric("🎯 Minimal Target", target, delta=selisih)

            # Legend / Keterangan
            st.info(f"**Ringkasan:** Performa tertinggi hari ini dicapai oleh **{report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]}** dengan {max_val} PM.")

        else:
            st.error(f"Kolom '{target_column}' tidak ditemukan. Kolom di file Anda: {list(df.columns)}")

    except Exception as e:
        st.error(f"Error membaca file: {e}")
else:
    st.info("Silakan unggah file Excel untuk melihat laporan.")

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Konfigurasi Zona Waktu WITA
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

# Set konfigurasi halaman, gunakan layout 'centered' agar lebih fokus pada tabel
st.set_page_config(page_title="Converter Laporan VCare", layout="centered")

st.markdown("""
<style>
    /* Mengubah font header halaman agar lebih 'eye-catching' */
    .stTitle {
        color: #1E3A8A; /* Biru tua */
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 VCare Excel to Report Converter")

# --- Bagian Filter & Download (Sidebar) ---
st.sidebar.header("Pengaturan Data")

# Pilihan Tanggal (Default hari ini WITA)
selected_date = st.sidebar.date_input("Pilih Tanggal Laporan", now_wita)
date_str = selected_date.strftime('%d-%b-%Y')

# Konstruksi URL berdasarkan input
download_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"

st.sidebar.markdown(f"**🔗 [Klik untuk Download File VCare]({download_url})**")
st.sidebar.info("Catatan: Pastikan Anda sudah login ke VCare di browser sebelum mengunduh.")

st.sidebar.markdown("---")
st.sidebar.markdown("© Team Visionet - WITA")

# --- Bagian Upload ---
uploaded_file = st.file_uploader("Upload file Excel yang sudah didownload", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Membaca Data
        # Sesuaikan 'skiprows' jika file Excel asli memiliki baris kosong di atas header
        df = pd.read_excel(uploaded_file, skiprows=0) 
        
        # Membersihkan spasi pada nama kolom
        df.columns = df.columns.str.strip()

        # Menggunakan kolom 'Engineer' sesuai struktur file VCare
        target_column = 'Engineer'

        if target_column in df.columns:
            # Menghitung progress per Engineer
            report_df = df[target_column].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM'] # Judul kolom sesuai gambar
            
            # Total baris
            total_pm = report_df['Progres PM'].sum()
            
            # Subheader tanggal
            st.markdown(f"### Rekap Progres PM - <span style='color:#1E3A8A; font-weight:bold;'>{date_str}</span>", unsafe_allow_html=True)

            # --- Bagian Styling Tabel Eye Catching ---
            
            # Hitung statistik untuk threshold warna
            df_pm = report_df['Progres PM']
            max_val = df_pm.max()
            min_val = df_pm.min()
            
            # Fungsi untuk memberi warna baris berdasarkan nilai Progres PM
            def style_row(row):
                color = ''
                font_weight = 'normal'
                text_color = 'black'
                
                val = row['Progres PM']
                
                if val == 0:
                    color = '#f1948a'  # Merah (sangat kritis)
                    text_color = 'white'
                    font_weight = 'bold'
                elif val == max_val and val > 0:
                    color = '#2ecc71'  # Hijau (performa terbaik)
                    text_color = 'white'
                    font_weight = 'bold'
                elif val <= 2 and val > 0:
                     color = '#fff3cd' # Kuning lembut (perlu perhatian)
                
                return [f'background-color: {color}; color: {text_color}; font-weight: {font_weight}'] * len(row)

            # Menerapkan styling baris
            if hasattr(report_df.style, 'map'):
                 # Pandas terbaru menggunakan .map untuk styling sel, 
                 # namun untuk styling baris kita gunakan .apply(..., axis=1)
                 # Karena kita ingin warna per baris, kita gunakan .apply
                styled_df = report_df.style.apply(style_row, axis=1)
            else:
                 # Pandas lama
                styled_df = report_df.style.apply(style_row, axis=1)

            # Menghilangkan nomor urut (index) dan menerapkan CSS header
            styled_df.hide_index()
            
            # CSS kustom untuk header tabel dan total
            table_css = """
            <style>
                thead th {
                    background-color: #1E3A8A !important; /* Header biru tua */
                    color: white !important;
                    font-weight: bold !important;
                    text-align: left !important;
                }
                .total-pm-row {
                    background-color: #E0E7FF;
                    font-weight: bold;
                    font-size: 1.1em;
                }
            </style>
            """
            st.markdown(table_css, unsafe_allow_html=True)

            # Menampilkan tabel
            st.table(styled_df)
            
            # --- Bagian Ringkasan dan Kaki ---
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="✅ Total PM Saat Ini", value=total_pm)
                
            with col2:
                target_min = 30
                selisih = int(total_pm) - target_min
                st.metric(label="🎯 Minimal Target", value=target_min, delta=selisih)
            
            # Baris total informatif di luar tabel
            st.markdown(f"""
            <div style="background-color: #E0E7FF; border-left: 5px solid #1E3A8A; padding: 15px; border-radius: 5px; margin-top: 10px;">
                <strong>Performa Kecil-Kecil:</strong><br>
                <span style="color: #2ecc71; font-weight:bold;">● {report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]} ({max_val} PM)</span> (Performa Terbaik)<br>
                <span style="color: #f1948a; font-weight:bold;">● Baris Merah</span> (Kritis - 0 PM)
            </div>
            """, unsafe_allow_html=True)
                
        else:
            st.error(f"Kolom '{target_column}' tidak ditemukan dalam file. Kolom yang tersedia: {', '.join(df.columns)}")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
        st.warning("Pastikan Anda mendownload file Excel dari link di sidebar.")

else:
    st.info("👋 Selamat datang! Silakan download file dari VCare terlebih dahulu, lalu upload di sini untuk membuat laporan.")

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN & WAKTU
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

# Layout 'centered' agar lebih fokus di layar HP
st.set_page_config(page_title="VCare Report Mobile", layout="centered")

# Custom CSS untuk tampilan Mobile-Friendly & Screenshot-Ready
st.markdown("""
<style>
    /* Mengatur padding agar pas di layar HP */
    .main .block-container {
        padding: 1rem 0.5rem;
    }
    
    .stTitle {
        color: #1E3A8A;
        font-size: 1.4rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Styling Tabel khusus agar index/nomor urut hilang dan font pas */
    table {
        width: 100% !important;
        border-collapse: collapse;
        font-size: 0.8rem; /* Font diperkecil sedikit agar tidak terpotong di HP */
        font-family: sans-serif;
    }

    thead th {
        background-color: #1E3A8A !important;
        color: white !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 8px 4px !important;
    }

    td {
        padding: 6px 4px !important;
        text-align: center !important;
        border-bottom: 1px solid #eeeeee;
    }

    /* Menghilangkan margin berlebih pada box metrik */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 VCare Mobile Report")

# 2. SIDEBAR
st.sidebar.header("Opsi")
selected_date = st.sidebar.date_input("Pilih Tanggal", now_wita)
date_str = selected_date.strftime('%d-%b-%Y')

download_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
st.sidebar.markdown(f"**[🔗 Download File VCare]({download_url})**")

# 3. PROSES FILE
uploaded_file = st.file_uploader("Upload Excel VCare", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        target_col = 'Engineer'
        if target_col in df.columns:
            # Olah Data
            report_df = df[target_col].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM']
            report_df = report_df.sort_values(by='SAE')

            max_val = report_df['Progres PM'].max()
            total_pm = report_df['Progres PM'].sum()

            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:5px;'>Rekap PM: {date_str}</p>", unsafe_allow_html=True)

            # Fungsi Styling
            def style_row(row):
                val = row['Progres PM']
                bg, txt, weight = '', 'black', 'normal'
                
                if val == 0:
                    bg, txt, weight = '#f1948a', 'white', 'bold' # Merah
                elif val == max_val and val > 0:
                    bg, txt, weight = '#2ecc71', 'white', 'bold' # Hijau
                elif 0 < val <= 2:
                    bg = '#fff3cd' # Kuning
                
                return [f'background-color: {bg}; color: {txt}; font-weight: {weight}'] * len(row)

            # Terapkan Styling
            styled_df = report_df.style.apply(style_row, axis=1)
            
            # PROTEKSI: Sembunyikan index di objek styler
            if hasattr(styled_df, 'hide'):
                styled_df.hide()
            else:
                styled_df.hide_index()

            # RENDER TOTAL: Paksa index=False dalam konversi HTML
            st.write(styled_df.to_html(index=False), unsafe_allow_html=True)

            # 4. METRIK RINGKASAN
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total PM", total_pm)
            with c2:
                target = 30
                diff = int(total_pm) - target
                st.metric("Target", target, delta=f"{diff}")

            st.success(f"🏆 **Terbaik:** {report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]} ({max_val} PM)")

        else:
            st.error(f"Kolom '{target_col}' tidak ditemukan!")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan upload file Excel.")

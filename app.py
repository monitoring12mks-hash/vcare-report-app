import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Dashboard", layout="centered")

# CSS UNTUK TAMPILAN PREMIUM & SEIMBANG
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #f1f5f9; }

    /* Container Utama agar Lebar Tabel & Metrik SAMA */
    .report-container {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin: 0 auto;
        max-width: 450px; /* Lebar optimal untuk screenshot HP */
    }

    .report-title {
        color: #1e3a8a;
        font-size: 1.3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 15px;
        line-height: 1.2;
    }

    /* Tabel Styling - Dipaksa Lebar 100% */
    .report-table {
        width: 100% !important;
        border-collapse: collapse;
        margin-bottom: 0px;
        border-radius: 8px 8px 0 0;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    .report-table thead th {
        background: #1e3a8a !important;
        color: white !important;
        padding: 12px 5px !important;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    .report-table td {
        padding: 10px 5px !important;
        font-size: 0.85rem;
        border-bottom: 1px solid #f1f5f9 !important;
        text-align: center;
    }

    /* Metrik Styling - Dibuat menyatu di bawah tabel */
    .metric-section {
        display: flex;
        width: 100%;
        background-color: #1e3a8a;
        border-radius: 0 0 8px 8px;
        margin-bottom: 15px;
    }
    .metric-box {
        flex: 1;
        padding: 15px 5px;
        text-align: center;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .metric-box:last-child { border-right: none; }
    .metric-label { font-size: 0.65rem; color: #bfdbfe; text-transform: uppercase; margin-bottom: 4px; }
    .metric-value { font-size: 1.4rem; font-weight: 800; color: white; }

    /* Badge MVP */
    .mvp-badge {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #15803d;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# HEADER UI
st.markdown('<h1 style="text-align:center; color:#1e3a8a; font-size:1.5rem;">VCare Analytics</h1>', unsafe_allow_html=True)

# KONTROL INPUT
with st.expander("⚙️ Pengaturan Laporan", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        selected_date = st.date_input("Tanggal", now_wita)
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        date_str = selected_date.strftime('%d-%b-%Y')
        dl_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
        st.link_button("🔗 Link Excel", dl_url, use_container_width=True)
    uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "xls"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        target_col = 'Engineer'

        if target_col in df.columns:
            # 1. Processing Data
            report_df = df[target_col].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM']
            report_df = report_df.sort_values(by='SAE')

            # 2. Cari 3 Terendah (Nilai Terkecil)
            # Menghilangkan nilai 0 dari pencarian 3 terendah agar tidak tumpang tindih dengan warna merah
            bottom_3_values = report_df[report_df['Progres PM'] > 0]['Progres PM'].nsmallest(3).unique()

            max_val = report_df['Progres PM'].max()
            total_pm = report_df['Progres PM'].sum()
            best_name = report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]

            # 3. Fungsi Styling Baris
            def style_row(row):
                val = row['Progres PM']
                bg, txt, weight = '', 'black', 'normal'
                
                if val == 0:
                    bg, txt, weight = '#fff1f2', '#be123c', 'bold' # MERAH (Kritis)
                elif val == max_val and val > 0:
                    bg, txt, weight = '#f0fdf4', '#15803d', 'bold' # HIJAU (Terbaik)
                elif val in bottom_3_values:
                    bg, txt, weight = '#ffedd5', '#9a3412', 'bold' # ORANYE (3 Terendah)
                
                return [f'background-color: {bg}; color: {txt}; font-weight: {weight}; border-bottom: 1px solid #f1f5f9;'] * len(row)

            styled_df = report_df.style.apply(style_row, axis=1)
            if hasattr(styled_df, 'hide'): styled_df.hide()
            else: styled_df.hide_index()

            # --- RENDER DISPLAY ---
            st.markdown('<div class="report-container">', unsafe_allow_html=True)
            
            st.markdown(f'<div class="report-title">REKAP PROGRES PM<br><span style="font-size:0.9rem; font-weight:normal; color:#64748b;">{date_str}</span></div>', unsafe_allow_html=True)
            
            # Tabel
            st.write(styled_df.to_html(index=False, classes='report-table'), unsafe_allow_html=True)

            # Metrik di bawah tabel (Lebar SAMA dengan tabel)
            st.markdown(f"""
                <div class="metric-section">
                    <div class="metric-box">
                        <div class="metric-label">Total Progress</div>
                        <div class="metric-value">{total_pm}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Minimal Target</div>
                        <div class="metric-value">30</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # MVP Badge
            st.markdown(f"""
                <div class="mvp-badge">
                    🏆 MVP: {best_name} ({max_val} PM)
                </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.error(f"Kolom '{target_col}' tidak ditemukan.")
    except Exception as e:
        st.error(f"Kesalahan: {e}")

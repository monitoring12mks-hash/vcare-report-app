import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Analytics Pro", layout="centered")

# CSS UNTUK KESEIMBANGAN LAYOUT & MENGHILANGKAN MENU GITHUB/SHARE
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #f4f7f9;
    }

    /* Pembungkus Utama agar Screenshot Seimbang */
    .screenshot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0 auto;
        max-width: 500px; /* Membatasi lebar agar proporsional di HP */
    }

    .main-title {
        color: #1e3a8a;
        font-size: 1.4rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Tabel Styling */
    .report-table {
        width: 100% !important;
        border-collapse: collapse;
        margin-bottom: 20px;
        border-radius: 10px;
        overflow: hidden;
    }
    .report-table thead th {
        background: #1e3a8a !important;
        color: white !important;
        padding: 10px 5px !important;
        font-size: 0.75rem;
    }
    .report-table td {
        padding: 8px 5px !important;
        font-size: 0.85rem;
        border-bottom: 1px solid #f1f5f9 !important;
        text-align: center;
    }

    /* Metrik Styling agar Sejajar */
    .metric-wrapper {
        display: flex;
        justify-content: space-around;
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
    }
    .metric-item {
        text-align: center;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1e293b;
    }

    /* MVP Badge Styling */
    .mvp-badge {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #15803d;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# HEADER FORM (Hanya muncul sebelum upload)
if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file is None:
    st.markdown('<h1 class="main-title">VCare Analytics</h1>', unsafe_allow_html=True)
    selected_date = st.date_input("Pilih Tanggal", now_wita)
    date_str = selected_date.strftime('%d-%b-%Y')
    st.link_button("📥 Download Excel VCare", f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}", use_container_width=True)

uploaded_file = st.file_uploader("Upload File", type=["xlsx", "xls"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        target_col = 'Engineer'

        if target_col in df.columns:
            report_df = df[target_col].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM']
            report_df = report_df.sort_values(by='SAE')

            max_val = report_df['Progres PM'].max()
            total_pm = report_df['Progres PM'].sum()
            best_name = report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]

            # FUNGSI STYLING BARIS
            def style_row(row):
                val = row['Progres PM']
                if val == 0: return ['background-color: #fff1f2; color: #be123c; font-weight: bold;'] * len(row)
                elif val == max_val and val > 0: return ['background-color: #f0fdf4; color: #15803d; font-weight: bold;'] * len(row)
                elif 0 < val <= 2: return ['background-color: #fffbeb; color: #b45309;'] * len(row)
                return [''] * len(row)

            styled_df = report_df.style.apply(style_row, axis=1)
            if hasattr(styled_df, 'hide'): styled_df.hide()
            else: styled_df.hide_index()

            # --- RENDER DASHBOARD DALAM SATU BOX ---
            st.markdown('<div class="screenshot-container">', unsafe_allow_html=True)
            
            st.markdown(f'<div class="main-title">Rekap PM: {uploaded_file.name[:11]}</div>', unsafe_allow_html=True)
            
            # Tabel
            st.write(styled_df.to_html(index=False, classes='report-table'), unsafe_allow_html=True)

            # Metrik Custom (Sejajar)
            st.markdown(f"""
                <div class="metric-wrapper">
                    <div class="metric-item">
                        <div class="metric-label">Total Progress</div>
                        <div class="metric-value">{total_pm}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Minimal Target</div>
                        <div class="metric-value">30</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Selisih</div>
                        <div class="metric-value" style="color: {'#15803d' if total_pm >= 30 else '#be123c'}">
                            {'+' if total_pm >= 30 else ''}{total_pm - 30}
                        </div>
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
        st.error(f"Error: {e}")

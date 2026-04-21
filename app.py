import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Analytics Pro", layout="centered")

# CSS UNTUK KESEIMBANGAN TOTAL (LEBAR SERAGAM)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #f1f5f9; }

    /* Kontainer Utama */
    .report-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin: 0 auto;
        max-width: 450px; /* Lebar pas untuk layar HP */
    }

    .report-title {
        color: #1e3a8a;
        font-size: 1.3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 15px;
    }

    /* TABEL: Paksa Lebar 100% */
    .report-table {
        width: 100% !important;
        border-collapse: collapse;
        border: 1px solid #e2e8f0;
        border-radius: 10px 10px 0 0;
        overflow: hidden;
    }
    .report-table thead th {
        background: #1e3a8a !important;
        color: white !important;
        padding: 12px 5px !important;
        font-size: 0.75rem;
    }
    .report-table td {
        padding: 10px 5px !important;
        font-size: 0.85rem;
        border-bottom: 1px solid #f1f5f9 !important;
        text-align: center;
    }

    /* METRIK: Paksa Lebar 100% Sejajar dengan Tabel */
    .metric-section {
        display: flex;
        width: 100%;
        background-color: #1e3a8a;
        border-radius: 0 0 10px 10px; /* Melengkung di bawah saja */
        margin-bottom: 15px;
        box-sizing: border-box;
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

    /* MVP: Paksa Lebar 100% */
    .mvp-badge {
        width: 100%;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #15803d;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 0.85rem;
        box-sizing: border-box; /* Agar padding tidak merusak lebar */
    }
</style>
""", unsafe_allow_html=True)

# UI INPUT (Di luar container screenshot)
st.markdown('<h2 style="text-align:center; color:#1e3a8a;">VCare Analytics</h2>', unsafe_allow_html=True)
with st.expander("⚙️ Kontrol Laporan", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        selected_date = st.date_input("Pilih Tanggal", now_wita)
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        date_str = selected_date.strftime('%d-%b-%Y')
        dl_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
        st.link_button("🔗 Link Excel", dl_url, use_container_width=True)
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

            # Logika 3 Terendah (selain 0)
            bottom_3_values = report_df[report_df['Progres PM'] > 0]['Progres PM'].nsmallest(3).unique()
            
            max_val = report_df['Progres PM'].max()
            total_pm = report_df['Progres PM'].sum()
            best_name = report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]

            def style_row(row):
                val = row['Progres PM']
                if val == 0: return ['background-color: #fff1f2; color: #be123c; font-weight: bold;'] * len(row)
                elif val == max_val and val > 0: return ['background-color: #f0fdf4; color: #15803d; font-weight: bold;'] * len(row)
                elif val in bottom_3_values: return ['background-color: #ffedd5; color: #9a3412; font-weight: bold;'] * len(row)
                return [''] * len(row)

            styled_df = report_df.style.apply(style_row, axis=1)
            if hasattr(styled_df, 'hide'): styled_df.hide()
            else: styled_df.hide_index()

            # --- START SCREENSHOT CONTAINER ---
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            
            st.markdown(f'<div class="report-title">REKAP PROGRES PM<br><span style="font-size:0.8rem; font-weight:normal; color:#64748b;">{date_str}</span></div>', unsafe_allow_html=True)
            
            # 1. TABEL
            st.write(styled_df.to_html(index=False, classes='report-table'), unsafe_allow_html=True)

            # 2. METRIK (MENYATU DENGAN TABEL)
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

            # 3. MVP BADGE
            st.markdown(f"""
                <div class="mvp-badge">
                    🏆 MVP: {best_name} ({max_val} PM)
                </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
            # --- END SCREENSHOT CONTAINER ---

        else:
            st.error(f"Kolom '{target_col}' tidak ditemukan.")
    except Exception as e:
        st.error(f"Error: {e}")

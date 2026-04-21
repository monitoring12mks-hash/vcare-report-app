import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. SETTING HALAMAN & WAKTU
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Analytics Pro", layout="centered")

# 2. CSS UNTUK MERENDER VISUAL & MENYEMBUNYIKAN MENU STREAMLIT
st.markdown("""
<style>
    /* Sembunyikan menu bawaan agar screenshot bersih */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .stApp { background-color: #f1f5f9; }

    /* Container Utama Dashboard */
    .report-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin: 0 auto;
        width: 100%;
        max-width: 450px;
        box-sizing: border-box;
    }

    /* Tabel: Lebar 100% Presisi */
    .report-table {
        width: 100% !important;
        border-collapse: collapse;
        border: 1px solid #e2e8f0;
        margin-bottom: 0 !important;
    }
    .report-table thead th {
        background: #1e3a8a !important;
        color: white !important;
        padding: 12px 5px !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        text-align: center;
    }
    .report-table td {
        padding: 10px 5px !important;
        font-size: 0.85rem;
        border-bottom: 1px solid #f1f5f9 !important;
        text-align: center;
    }

    /* Kotak Metrik Biru: Melekat di bawah tabel tanpa celah */
    .metric-container {
        display: flex;
        width: 100%;
        background-color: #1e3a8a;
        margin-top: -1px; 
        margin-bottom: 15px;
        border-radius: 0 0 10px 10px;
        overflow: hidden;
    }
    .metric-box {
        flex: 1;
        padding: 15px 5px;
        text-align: center;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .metric-box:last-child { border-right: none; }
    .metric-label { font-size: 0.6rem; color: #bfdbfe; text-transform: uppercase; margin-bottom: 2px; }
    .metric-value { font-size: 1.4rem; font-weight: 800; color: white; margin: 0; }

    /* Badge MVP: Hijau Cerah Sejajar */
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
        box-sizing: border-box;
    }
</style>
""", unsafe_allow_html=True)

# 3. AREA KONTROL (TETAP TERLIHAT)
st.markdown('<h2 style="text-align:center; color:#1e3a8a;">📊 VCare Analytics</h2>', unsafe_allow_html=True)

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        selected_date = st.date_input("Pilih Tanggal", now_wita)
    with c2:
        date_str = selected_date.strftime('%d-%b-%Y')
        dl_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("📥 Download Excel", dl_url, use_container_width=True)

    uploaded_file = st.file_uploader("Upload File Rekap", type=["xlsx", "xls"])

# 4. LOGIKA PENGOLAHAN DATA & RENDER VISUAL
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        if 'Engineer' in df.columns:
            # Kalkulasi
            report_df = df['Engineer'].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM']
            report_df = report_df.sort_values(by='SAE')

            total_pm = report_df['Progres PM'].sum()
            max_val = report_df['Progres PM'].max()
            best_name = report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]
            
            # Logika Warna 3 Terendah (selain nol)
            bottom_3_vals = report_df[report_df['Progres PM'] > 0]['Progres PM'].nsmallest(3).unique()

            # Buat baris tabel
            rows_html = ""
            for _, row in report_df.iterrows():
                val = row['Progres PM']
                row_style = ""
                if val == 0:
                    row_style = "background-color: #fff1f2; color: #be123c; font-weight: bold;"
                elif val == max_val and val > 0:
                    row_style = "background-color: #f0fdf4; color: #15803d; font-weight: bold;"
                elif val in bottom_3_vals:
                    row_style = "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
                
                rows_html += f'<tr style="{row_style}"><td>{row["SAE"]}</td><td>{val}</td></tr>'

            # GABUNG SEMUA KE DALAM SATU VARIABEL HTML
            dashboard_final = f"""
            <div class="report-card">
                <div style="text-align:center; color:#1e3a8a; font-weight:800; font-size:1.1rem; margin-bottom:15px;">
                    REKAP PROGRES PM<br>
                    <span style="font-size:0.8rem; font-weight:normal; color:#64748b;">{date_str}</span>
                </div>
                
                <table class="report-table">
                    <thead><tr><th>SAE</th><th>PROGRES PM</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                
                <div class="metric-container">
                    <div class="metric-box">
                        <div class="metric-label">Total Progress</div>
                        <p class="metric-value">{total_pm}</p>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Minimal Target</div>
                        <p class="metric-value">30</p>
                    </div>
                </div>
                
                <div class="mvp-badge">🏆 MVP: {best_name} ({max_val} PM)</div>
            </div>
            """
            
            # --- TAMPILKAN SEBAGAI VISUAL (MENGGUNAKAN UNSAFE_ALLOW_HTML) ---
            st.markdown(dashboard_final, unsafe_allow_html=True)

        else:
            st.error("Kolom 'Engineer' tidak ditemukan.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

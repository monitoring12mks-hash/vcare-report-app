import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. PENGATURAN HALAMAN
st.set_page_config(page_title="VCare Analytics", layout="centered")

# 2. CSS - UNTUK TAMPILAN VISUAL (INI WAJIB ADA)
st.markdown("""
<style>
    /* Sembunyikan menu bawaan agar screenshot bersih */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #f1f5f9; }

    /* Kotak Utama Dashboard */
    .report-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 0 auto;
        max-width: 450px;
        width: 100%;
        box-sizing: border-box;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Judul */
    .report-header {
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 20px;
    }

    /* Tabel - Lebar 100% */
    .report-table {
        width: 100% !important;
        border-collapse: collapse;
        border: 1px solid #e2e8f0;
    }
    .report-table thead th {
        background-color: #1e3a8a !important;
        color: white !important;
        padding: 12px 5px;
        font-size: 12px;
        text-transform: uppercase;
    }
    .report-table td {
        padding: 10px 5px;
        font-size: 14px;
        text-align: center;
        border-bottom: 1px solid #f1f5f9;
    }

    /* Kotak Metrik Biru - Lebar 100% Sejajar Tabel */
    .metric-row {
        display: flex;
        width: 100%;
        background-color: #1e3a8a;
        margin-top: 0;
        border-radius: 0 0 10px 10px;
        margin-bottom: 20px;
    }
    .metric-item {
        flex: 1;
        padding: 15px 5px;
        text-align: center;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .metric-item:last-child { border-right: none; }
    .metric-label { font-size: 10px; color: #bfdbfe; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 22px; font-weight: bold; color: white; margin: 0; }

    /* Badge MVP - Lebar 100% Sejajar Tabel */
    .mvp-badge {
        width: 100%;
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #15803d;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        box-sizing: border-box;
    }
</style>
""", unsafe_allow_html=True)

# 3. BAGIAN KONTROL (TANGGAL & LINK)
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.title("📊 VCare Analytics")

col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("Pilih Tanggal", now_wita)
with col2:
    date_str = selected_date.strftime('%d-%b-%Y')
    dl_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
    st.markdown(f'<br><a href="{dl_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:40px; border-radius:5px; background-color:#1e3a8a; color:white; border:none; cursor:pointer;">📥 Link Excel</button></a>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "xls"])

# 4. PENGOLAHAN DATA
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        if 'Engineer' in df.columns:
            # Perhitungan
            counts = df['Engineer'].value_counts().reset_index()
            counts.columns = ['SAE', 'Progres']
            counts = counts.sort_values(by='SAE')

            total_pm = counts['Progres'].sum()
            max_pm = counts['Progres'].max()
            mvp_name = counts.loc[counts['Progres'] == max_pm, 'SAE'].iloc[0]
            
            # Cari 3 terendah (di atas 0)
            bottom_3 = counts[counts['Progres'] > 0]['Progres'].nsmallest(3).unique()

            # Buat Baris Tabel
            rows = ""
            for _, row in counts.iterrows():
                val = row['Progres']
                color = ""
                if val == 0:
                    color = "background-color: #fff1f2; color: #be123c; font-weight: bold;"
                elif val == max_pm and val > 0:
                    color = "background-color: #f0fdf4; color: #15803d; font-weight: bold;"
                elif val in bottom_3:
                    color = "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
                
                rows += f'<tr style="{color}"><td>{row["SAE"]}</td><td>{val}</td></tr>'

            # --- CONSTRUCT DASHBOARD HTML ---
            dashboard_html = f"""
            <div class="report-card">
                <div class="report-header">
                    <b style="font-size: 18px;">REKAP PROGRES PM</b><br>
                    <small style="color: #64748b;">{date_str}</small>
                </div>

                <table class="report-table">
                    <thead>
                        <tr>
                            <th>SAE</th>
                            <th>PROGRES PM</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>

                <div class="metric-row">
                    <div class="metric-item">
                        <div class="metric-label">Total Progress</div>
                        <div class="metric-value">{total_pm}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Minimal Target</div>
                        <div class="metric-value">30</div>
                    </div>
                </div>

                <div class="mvp-badge">
                    🏆 MVP: {mvp_name} ({max_pm} PM)
                </div>
            </div>
            """
            
            # RENDER HASIL
            st.markdown(dashboard_html, unsafe_allow_html=True)
            
        else:
            st.error("Kolom 'Engineer' tidak ditemukan dalam file.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

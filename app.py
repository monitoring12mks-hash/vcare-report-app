import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="VCare Analytics", layout="centered")

# 2. CSS UNTUK MENYATUKAN SEMUA ELEMEN DALAM SATU TABEL
st.markdown("""
<style>
    /* Sembunyikan menu bawaan agar screenshot bersih */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #f1f5f9; }

    /* Container Utama */
    .screenshot-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 0 auto;
        max-width: 450px;
        width: 100%;
    }

    /* TABEL TUNGGAL */
    .unified-table {
        width: 100% !important;
        border-collapse: collapse;
        border: 1px solid #e2e8f0;
        table-layout: fixed; /* Mengunci lebar kolom agar stabil */
    }

    /* Header Tabel */
    .unified-table thead th {
        background-color: #1e3a8a !important;
        color: white !important;
        padding: 12px 5px;
        font-size: 12px;
        text-transform: uppercase;
        border: 1px solid #1e3a8a;
    }

    /* Baris Data */
    .unified-table td {
        padding: 10px 5px;
        font-size: 14px;
        text-align: center;
        border: 1px solid #f1f5f9;
    }

    /* BARIS METRIK (Total & Target) */
    .row-metrics {
        background-color: #1e3a8a;
        color: white;
    }
    .metric-inner-container {
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
    }
    .metric-item { text-align: center; flex: 1; }
    .m-label { font-size: 10px; color: #bfdbfe; text-transform: uppercase; margin-bottom: 3px; }
    .m-value { font-size: 22px; font-weight: bold; }

    /* BARIS MVP */
    .row-mvp {
        background-color: #f0fdf4;
        color: #15803d;
        font-weight: bold;
        border-top: 2px solid #bbf7d0 !important;
    }
    .mvp-content { padding: 15px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# 3. KONTROL INPUT
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.title("📊 VCare Analytics")
c1, c2 = st.columns(2)
with c1:
    selected_date = st.date_input("Tanggal", now_wita)
with c2:
    date_str = selected_date.strftime('%d-%b-%Y')
    dl_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
    st.markdown(f'<br><a href="{dl_url}" target="_blank"><button style="width:100%; height:40px; border-radius:5px; background-color:#1e3a8a; color:white; border:none; cursor:pointer;">📥 Link Excel</button></a>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload File Rekap", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        if 'Engineer' in df.columns:
            # Pengolahan Data
            counts = df['Engineer'].value_counts().reset_index()
            counts.columns = ['SAE', 'Progres']
            counts = counts.sort_values(by='SAE')

            total_pm = counts['Progres'].sum()
            max_pm = counts['Progres'].max()
            mvp_name = counts.loc[counts['Progres'] == max_pm, 'SAE'].iloc[0]
            bottom_3 = counts[counts['Progres'] > 0]['Progres'].nsmallest(3).unique()

            # Membuat Baris Data HTML
            rows_html = ""
            for _, row in counts.iterrows():
                val = row['Progres']
                style = ""
                if val == 0: style = "background-color: #fff1f2; color: #be123c; font-weight: bold;"
                elif val == max_pm and val > 0: style = "background-color: #f0fdf4; color: #15803d; font-weight: bold;"
                elif val in bottom_3: style = "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
                
                rows_html += f'<tr style="{style}"><td>{row["SAE"]}</td><td>{val}</td></tr>'

            # --- RENDER DASHBOARD (SEMUA DALAM SATU TABEL) ---
            dashboard_html = f"""
            <div class="screenshot-box">
                <div style="text-align:center; margin-bottom:15px;">
                    <b style="font-size:18px; color:#1e3a8a;">REKAP PROGRES PM</b><br>
                    <small style="color:#64748b;">{date_str}</small>
                </div>

                <table class="unified-table">
                    <thead>
                        <tr>
                            <th style="width: 70%;">SAE</th>
                            <th style="width: 30%;">PROGRES</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                        <tr class="row-metrics">
                            <td colspan="2">
                                <div class="metric-inner-container">
                                    <div class="metric-item">
                                        <div class="m-label">Total Progress</div>
                                        <div class="m-value">{total_pm}</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="m-label">Minimal Target</div>
                                        <div class="m-value">30</div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr class="row-mvp">
                            <td colspan="2">
                                <div class="mvp-content">
                                    🏆 MVP: {mvp_name} ({max_pm} PM)
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """
            
            # Eksekusi Visual HTML
            st.markdown(dashboard_html, unsafe_allow_html=True)
            
        else:
            st.error("Kolom 'Engineer' tidak ditemukan.")
    except Exception as e:
        st.error(f"Error: {e}")

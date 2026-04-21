import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI WAKTU & HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Analytics Pro", layout="centered")

# 2. CSS UNTUK MENGUNCI TAMPILAN (LEBAR SERAGAM)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #f1f5f9; }

    /* Container Utama */
    .report-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin: 0 auto;
        width: 100%;
        max-width: 420px; /* Pas untuk screenshot HP */
        box-sizing: border-box;
    }

    /* Tabel: Lebar 100% tanpa margin bawah */
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
    }
    .report-table td {
        padding: 10px 5px !important;
        font-size: 0.85rem;
        border-bottom: 1px solid #f1f5f9 !important;
        text-align: center;
    }

    /* Metrik Biru: Melekat di bawah tabel */
    .metric-container {
        display: flex;
        width: 100%;
        background-color: #1e3a8a;
        margin-bottom: 15px;
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

    /* Badge MVP: Lebar Sama dengan tabel */
    .mvp-badge {
        width: 100%;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #15803d;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 0.85rem;
        box-sizing: border-box;
    }
</style>
""", unsafe_allow_html=True)

# 3. LOGIKA DATA (CONTOH DARI GAMBAR ANDA)
data = {
    'SAE': ['Andi Imran', 'Andi Muhammad Shaleh', 'Didi Setiawan', 'M. Syahrial Saeni', 
            'Muh Faris Aprillah Ridwan', 'Muhammad Yadi Ahdiat Tauhid', 'Mus Muliadi', 'Suardi M', 'Zulfadly'],
    'Progres PM': [5, 3, 14, 9, 4, 2, 7, 4, 2]
}
df = pd.DataFrame(data)

# Hitung angka penting
total_pm = df['Progres PM'].sum()
max_val = df['Progres PM'].max()
best_name = df.loc[df['Progres PM'] == max_val, 'SAE'].iloc[0]
bottom_3 = df[df['Progres PM'] > 0]['Progres PM'].nsmallest(3).unique()

# 4. GENERATE BARIS TABEL HTML
rows_html = ""
for _, row in df.iterrows():
    val = row['Progres PM']
    style = ""
    if val == 0: style = "background-color: #fff1f2; color: #be123c; font-weight: bold;"
    elif val == max_val: style = "background-color: #f0fdf4; color: #15803d; font-weight: bold;"
    elif val in bottom_3: style = "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
    
    rows_html += f'<tr style="{style}"><td>{row["SAE"]}</td><td>{val}</td></tr>'

# 5. RENDER SEKALIGUS (INI KUNCINYA)
full_report_html = f"""
<div class="report-card">
    <div style="text-align:center; color:#1e3a8a; font-weight:800; font-size:1.2rem; margin-bottom:15px;">
        REKAP PROGRES PM<br>
        <span style="font-size:0.8rem; font-weight:normal; color:#64748b;">{now_wita.strftime('%d-%b-%Y')}</span>
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

# TAMPILKAN MENGGUNAKAN ST.MARKDOWN
st.markdown(full_report_html, unsafe_allow_html=True)

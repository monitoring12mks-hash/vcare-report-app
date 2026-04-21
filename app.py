import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="VCare Analytics", layout="centered")

# 2. CSS GLOBAL (hanya untuk elemen bawaan Streamlit, bukan untuk HTML custom)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #f1f5f9; }
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
    st.markdown(
        f'<br><a href="{dl_url}" target="_blank">'
        f'<button style="width:100%;height:40px;border-radius:5px;'
        f'background-color:#1e3a8a;color:white;border:none;cursor:pointer;">📥 Link Excel</button></a>',
        unsafe_allow_html=True
    )

uploaded_file = st.file_uploader("Upload File Rekap", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        if 'Engineer' in df.columns:
            # --- PENGOLAHAN DATA ---
            counts = df['Engineer'].value_counts().reset_index()
            counts.columns = ['SAE', 'Progres']
            counts = counts.sort_values(by='SAE').reset_index(drop=True)

            total_pm  = int(counts['Progres'].sum())
            max_pm    = int(counts['Progres'].max())
            mvp_name  = counts.loc[counts['Progres'] == max_pm, 'SAE'].iloc[0]
            bottom_3  = set(counts[counts['Progres'] > 0]['Progres'].nsmallest(3).unique())

            # --- BARIS DATA (semua inline style) ---
            rows_html = ""
            for _, row in counts.iterrows():
                val = int(row['Progres'])
                name = row['SAE']

                if val == 0:
                    row_style  = "background-color:#fff1f2;"
                    text_style = "color:#be123c;font-weight:bold;"
                elif val == max_pm:
                    row_style  = "background-color:#f0fdf4;"
                    text_style = "color:#15803d;font-weight:bold;"
                elif val in bottom_3:
                    row_style  = "background-color:#ffedd5;"
                    text_style = "color:#9a3412;font-weight:bold;"
                else:
                    row_style  = "background-color:#ffffff;"
                    text_style = "color:#1e293b;"

                rows_html += (
                    f'<tr style="{row_style}">'
                    f'<td style="padding:10px 8px;font-size:14px;text-align:left;'
                    f'border-bottom:1px solid #f1f5f9;{text_style}">{name}</td>'
                    f'<td style="padding:10px 8px;font-size:14px;text-align:center;'
                    f'border-bottom:1px solid #f1f5f9;{text_style}">{val}</td>'
                    f'</tr>'
                )

            # --- BARIS METRIK ---
            metrics_row = (
                '<tr style="background-color:#1e3a8a;">'
                '<td colspan="2" style="padding:0;">'
                '<div style="display:flex;justify-content:space-around;padding:15px 0;">'

                '<div style="text-align:center;flex:1;">'
                '<div style="font-size:10px;color:#bfdbfe;text-transform:uppercase;margin-bottom:4px;">Total Progress</div>'
                f'<div style="font-size:24px;font-weight:bold;color:white;">{total_pm}</div>'
                '</div>'

                '<div style="width:1px;background:#3b5fc0;margin:5px 0;"></div>'

                '<div style="text-align:center;flex:1;">'
                '<div style="font-size:10px;color:#bfdbfe;text-transform:uppercase;margin-bottom:4px;">Minimal Target</div>'
                '<div style="font-size:24px;font-weight:bold;color:white;">30</div>'
                '</div>'

                '</div>'
                '</td>'
                '</tr>'
            )

            # --- BARIS MVP ---
            mvp_row = (
                '<tr style="background-color:#f0fdf4;border-top:2px solid #bbf7d0;">'
                '<td colspan="2" style="padding:14px 16px;font-size:14px;'
                'font-weight:bold;color:#15803d;text-align:center;">'
                f'🏆 MVP: {mvp_name} ({max_pm} PM)'
                '</td>'
                '</tr>'
            )

            # --- RENDER DASHBOARD (semua inline, tidak bergantung CSS class) ---
            dashboard_html = f"""
            <div style="background-color:white;padding:20px;border-radius:15px;
                        box-shadow:0 4px 20px rgba(0,0,0,0.1);margin:0 auto;
                        max-width:450px;width:100%;font-family:sans-serif;">

                <div style="text-align:center;margin-bottom:15px;">
                    <b style="font-size:18px;color:#1e3a8a;">REKAP PROGRES PM</b><br>
                    <small style="color:#64748b;">{date_str}</small>
                </div>

                <table style="width:100%;border-collapse:collapse;
                              border:1px solid #e2e8f0;table-layout:fixed;">
                    <thead>
                        <tr>
                            <th style="background-color:#1e3a8a;color:white;
                                       padding:12px 8px;font-size:12px;
                                       text-transform:uppercase;border:1px solid #1e3a8a;
                                       width:70%;text-align:left;">SAE</th>
                            <th style="background-color:#1e3a8a;color:white;
                                       padding:12px 8px;font-size:12px;
                                       text-transform:uppercase;border:1px solid #1e3a8a;
                                       width:30%;text-align:center;">PROGRES</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                        {metrics_row}
                        {mvp_row}
                    </tbody>
                </table>
            </div>
            """

            st.markdown(dashboard_html, unsafe_allow_html=True)

        else:
            st.error("❌ Kolom 'Engineer' tidak ditemukan dalam file.")

    except Exception as e:
        st.error(f"Error membaca file: {e}")

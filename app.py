import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Analytics Pro", layout="centered")

# CSS UNTUK UI PREMIUM & MENGHILANGKAN ELEMENT GITHUB/SHARE
st.markdown("""
<style>
    /* Menghilangkan Menu Streamlit (Share, GitHub, dan Menu kanan atas) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Background & Container */
    .stApp {
        background-color: #f8fafc;
    }
    .main .block-container {
        padding: 1.5rem 1rem;
    }

    /* Judul & Sub-judul */
    .main-title {
        color: #1e3a8a;
        font-size: 1.6rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748b;
        text-align: center;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }

    /* Card Styling untuk Kontrol di Depan */
    .control-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }

    /* Tabel Dashboard Pro */
    .report-table {
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    .report-table thead th {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        padding: 12px 8px !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .report-table td {
        padding: 10px 8px !important;
        font-size: 0.85rem;
        border-bottom: 1px solid #f1f5f9 !important;
    }

    /* Download Button */
    .stDownloadButton button {
        width: 100%;
        border-radius: 10px;
        background-color: #1e3a8a;
        color: white;
        border: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<h1 class="main-title">VCare Analytics</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">WITA Timezone • {now_wita.strftime("%d %B %Y")}</p>', unsafe_allow_html=True)

# 2. AREA KONTROL (HALAMAN DEPAN)
with st.container():
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    
    col_date, col_btn = st.columns([1, 1])
    with col_date:
        selected_date = st.date_input("Pilih Tanggal", now_wita)
    with col_btn:
        date_str = selected_date.strftime('%d-%b-%Y')
        download_url = f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("📥 Link Download", download_url, use_container_width=True)
    
    uploaded_file = st.file_uploader("Upload Excel VCare", type=["xlsx", "xls"])
    st.markdown('</div>', unsafe_allow_html=True)

# 3. PROSES DATA & DISPLAY
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

            # Styling Baris
            def style_row(row):
                val = row['Progres PM']
                if val == 0:
                    return ['background-color: #fff1f2; color: #be123c; font-weight: bold;'] * len(row)
                elif val == max_val and val > 0:
                    return ['background-color: #f0fdf4; color: #15803d; font-weight: bold;'] * len(row)
                elif 0 < val <= 2:
                    return ['background-color: #fffbeb; color: #b45309;'] * len(row)
                return [''] * len(row)

            # Render Table
            styled_df = report_df.style.apply(style_row, axis=1)
            if hasattr(styled_df, 'hide'):
                styled_df.hide()
            else:
                styled_df.hide_index()

            st.write(styled_df.to_html(index=False, classes='report-table'), unsafe_allow_html=True)

            # METRIKS
            st.write("")
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Total PM", f"{total_pm}")
            with m2:
                target = 30
                diff = int(total_pm) - target
                st.metric("Target", target, delta=f"{diff}")

            # MVP BADGE
            best_name = report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]
            st.markdown(f"""
                <div style="background: #f0fdf4; border-radius: 10px; padding: 12px; border: 1px solid #bbf7d0; margin-top:10px; text-align:center;">
                    <span style="font-size: 1.2rem;">🏆</span> <b style="color:#15803d;">MVP: {best_name}</b> ({max_val} PM)
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error(f"Kolom '{target_col}' tidak ditemukan.")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Silakan unggah file Excel untuk melihat laporan.")

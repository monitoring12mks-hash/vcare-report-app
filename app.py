import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. KONFIGURASI HALAMAN
wita_tz = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.set_page_config(page_title="VCare Dashboard Pro", layout="centered")

# Custom CSS Premium Dashboard
st.markdown("""
<style>
    /* Background Utama */
    .main {
        background-color: #f4f7f9;
    }
    
    /* Container Styling */
    .stApp {
        max-width: 600px;
        margin: 0 auto;
    }

    /* Judul Modern */
    .main-title {
        color: #1E293B;
        font-size: 1.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    
    .sub-title {
        color: #64748B;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

    /* Tabel Premium */
    .report-table {
        width: 100%;
        background-color: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: none;
        margin-bottom: 1.5rem;
    }

    .report-table thead th {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        padding: 15px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
        border: none !important;
    }

    .report-table td {
        padding: 12px 15px !important;
        border-bottom: 1px solid #f1f5f9 !important;
        font-size: 0.9rem;
        color: #334155;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Status Badge Style */
    .best-performer {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 8px;
        color: #065f46;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">VCare Analytics</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">Performance Report: {now_wita.strftime("%d %B %Y")}</p>', unsafe_allow_html=True)

# 2. SIDEBAR
st.sidebar.header("Control Panel")
selected_date = st.sidebar.date_input("Filter Tanggal", now_wita)
date_str = selected_date.strftime('%d-%b-%Y')

# 3. PROSES FILE
uploaded_file = st.file_uploader("Drop Excel VCare di sini", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        target_col = 'Engineer'

        if target_col in df.columns:
            # Data Processing
            report_df = df[target_col].value_counts().reset_index()
            report_df.columns = ['SAE', 'Progres PM']
            report_df = report_df.sort_values(by='SAE')

            max_val = report_df['Progres PM'].max()
            total_pm = report_df['Progres PM'].sum()

            # Styling Function
            def style_row(row):
                val = row['Progres PM']
                styles = 'border-bottom: 1px solid #f1f5f9;'
                if val == 0:
                    return [f'background-color: #fff1f2; color: #be123c; font-weight: bold; {styles}'] * len(row)
                elif val == max_val and val > 0:
                    return [f'background-color: #f0fdf4; color: #15803d; font-weight: bold; {styles}'] * len(row)
                elif 0 < val <= 2:
                    return [f'background-color: #fffbeb; color: #b45309; {styles}'] * len(row)
                return [styles] * len(row)

            # Build Styled Dataframe
            styled_df = report_df.style.apply(style_row, axis=1)
            
            if hasattr(styled_df, 'hide'):
                styled_df.hide()
            else:
                styled_df.hide_index()

            # Render Tabel dengan Class HTML
            table_html = styled_df.to_html(index=False, classes='report-table')
            st.write(table_html, unsafe_allow_html=True)

            # Metrics
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Progress", f"{total_pm} PM")
            with c2:
                target = 30
                diff = int(total_pm) - target
                st.metric("Achievement", target, delta=f"{diff} vs Target")

            # Footer / Best Performer Badge
            best_name = report_df.loc[report_df['Progres PM'] == max_val, 'SAE'].iloc[0]
            st.markdown(f"""
                <div class="best-performer">
                    <span>🏆</span>
                    <span>MVP of the Day: <b>{best_name}</b> ({max_val} PM)</span>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error(f"Kolom '{target_col}' tidak ditemukan.")
    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
else:
    st.info("Menunggu unggahan file Excel...")

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import io
from PIL import Image, ImageDraw, ImageFont

# ── KONFIGURASI ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="VCare Analytics", layout="centered")
st.markdown("""
<style>
    #MainMenu {visibility:hidden;} header {visibility:hidden;} footer {visibility:hidden;}
    .stApp {background-color:#f1f5f9;}
</style>""", unsafe_allow_html=True)

# ── FONT ─────────────────────────────────────────────────────────────────────
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def fnt(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

# ── WARNA ────────────────────────────────────────────────────────────────────
C_NAVY    = (30,  58, 138)
C_WHITE   = (255, 255, 255)
C_LIGHT   = (241, 245, 249)
C_GREEN_B = (240, 253, 244)
C_GREEN_T = (21,  128, 61)
C_ORANGE_B= (255, 237, 213)
C_ORANGE_T= (154,  52, 18)
C_RED_B   = (255, 241, 242)
C_RED_T   = (190,  18, 60)
C_GRAY    = (100, 116, 139)
C_TEXT    = (30,  41, 59)
C_BORDER  = (226, 232, 240)
C_DIVIDER = (59,  95, 192)
C_GREENBR = (187, 247, 208)

def generate_image(counts, total_pm, max_pm, mvp_name, date_str):
    PADDING   = 24
    W         = 520
    ROW_H     = 44
    HEADER_H  = 52
    TITLE_H   = 70
    METRIC_H  = 80
    MVP_H     = 52

    n_rows    = len(counts)
    total_h   = PADDING + TITLE_H + HEADER_H + (ROW_H * n_rows) + METRIC_H + MVP_H + PADDING

    img  = Image.new("RGB", (W, total_h), C_LIGHT)
    draw = ImageDraw.Draw(img)

    # Card background
    card_x1, card_y1 = PADDING, PADDING
    card_x2, card_y2 = W - PADDING, total_h - PADDING
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2],
                           radius=16, fill=C_WHITE, outline=C_BORDER, width=1)

    y = PADDING + 16

    # JUDUL
    title = "REKAP PROGRES PM"
    tw = draw.textlength(title, font=fnt(17, bold=True))
    draw.text(((W - tw) / 2, y), title, font=fnt(17, bold=True), fill=C_NAVY)
    y += 28

    dw = draw.textlength(date_str, font=fnt(12))
    draw.text(((W - dw) / 2, y), date_str, font=fnt(12), fill=C_GRAY)
    y += 30

    # TABLE
    col1_x  = PADDING + 8
    col_w2  = int((W - PADDING * 2) * 0.28)
    tbl_x1  = PADDING
    tbl_x2  = W - PADDING

    # Header
    draw.rectangle([tbl_x1, y, tbl_x2, y + HEADER_H], fill=C_NAVY)
    draw.text((col1_x + 4, y + 16), "SAE", font=fnt(11, bold=True), fill=C_WHITE)
    ph = "PROGRES"
    pw = draw.textlength(ph, font=fnt(11, bold=True))
    draw.text((tbl_x2 - col_w2 + (col_w2 - pw) / 2, y + 16),
              ph, font=fnt(11, bold=True), fill=C_WHITE)
    y += HEADER_H

    # Bottom 3
    bottom_3 = set(counts[counts['Progres'] > 0]['Progres'].nsmallest(3).unique())

    # Baris data
    for i, (_, row) in enumerate(counts.iterrows()):
        val  = int(row['Progres'])
        name = str(row['SAE'])

        if val == 0:
            bg, tc = C_RED_B, C_RED_T
        elif val == max_pm and val > 0:
            bg, tc = C_GREEN_B, C_GREEN_T
        elif val in bottom_3:
            bg, tc = C_ORANGE_B, C_ORANGE_T
        else:
            bg, tc = C_WHITE, C_TEXT

        draw.rectangle([tbl_x1, y, tbl_x2, y + ROW_H], fill=bg)
        draw.line([(tbl_x1, y + ROW_H - 1), (tbl_x2, y + ROW_H - 1)],
                  fill=C_BORDER, width=1)

        is_bold = val == 0 or val == max_pm or val in bottom_3
        max_chars = 30
        display_name = name if len(name) <= max_chars else name[:max_chars - 1] + "..."
        draw.text((col1_x + 4, y + 13), display_name, font=fnt(13, bold=is_bold), fill=tc)

        vstr = str(val)
        vw   = draw.textlength(vstr, font=fnt(13, bold=is_bold))
        draw.text((tbl_x2 - col_w2 + (col_w2 - vw) / 2, y + 13),
                  vstr, font=fnt(13, bold=is_bold), fill=tc)
        y += ROW_H

    # BARIS METRIK
    draw.rectangle([tbl_x1, y, tbl_x2, y + METRIC_H], fill=C_NAVY)
    mid_x = tbl_x1 + (tbl_x2 - tbl_x1) // 2
    draw.line([(mid_x, y + 12), (mid_x, y + METRIC_H - 12)], fill=C_DIVIDER, width=1)

    left_cx  = tbl_x1 + (mid_x - tbl_x1) // 2
    right_cx = mid_x + (tbl_x2 - mid_x) // 2

    lbl1 = "TOTAL PROGRESS"
    lw1  = draw.textlength(lbl1, font=fnt(9))
    draw.text((left_cx - lw1 / 2, y + 10), lbl1, font=fnt(9), fill=(191, 219, 254))
    tv = str(total_pm)
    tw2 = draw.textlength(tv, font=fnt(26, bold=True))
    draw.text((left_cx - tw2 / 2, y + 26), tv, font=fnt(26, bold=True), fill=C_WHITE)

    lbl2 = "MINIMAL TARGET"
    lw2  = draw.textlength(lbl2, font=fnt(9))
    draw.text((right_cx - lw2 / 2, y + 10), lbl2, font=fnt(9), fill=(191, 219, 254))
    tgt  = "30"
    tw3  = draw.textlength(tgt, font=fnt(26, bold=True))
    draw.text((right_cx - tw3 / 2, y + 26), tgt, font=fnt(26, bold=True), fill=C_WHITE)
    y += METRIC_H

    # BARIS MVP
    draw.rectangle([tbl_x1, y, tbl_x2, y + MVP_H], fill=C_GREEN_B)
    draw.line([(tbl_x1, y), (tbl_x2, y)], fill=C_GREENBR, width=2)
    mvp_safe = f"MVP: {mvp_name} ({max_pm} PM)"
    mw = draw.textlength(mvp_safe, font=fnt(14, bold=True))
    # Bintang kiri
    star_w = draw.textlength("* ", font=fnt(14, bold=True))
    total_w = star_w + mw
    start_x = (W - total_w) / 2
    draw.text((start_x, y + 17), "* ", font=fnt(14, bold=True), fill=C_GREEN_T)
    draw.text((start_x + star_w, y + 17), mvp_safe, font=fnt(14, bold=True), fill=C_GREEN_T)

    return img


# ── UI ────────────────────────────────────────────────────────────────────────
wita_tz  = pytz.timezone('Asia/Makassar')
now_wita = datetime.now(wita_tz)

st.title("📊 VCare Analytics")

c1, c2 = st.columns(2)
with c1:
    selected_date = st.date_input("Tanggal", now_wita)
with c2:
    date_str = selected_date.strftime('%d-%b-%Y')
    dl_url = (
        f"https://vcare.visionet.co.id/JobHistory/DownloadJobHistory"
        f"?Type=1&WorkType=2&Account=All&Project=All&Date={date_str}"
    )
    st.markdown(
        f'<br><a href="{dl_url}" target="_blank">'
        f'<button style="width:100%;height:40px;border-radius:5px;'
        f'background-color:#1e3a8a;color:white;border:none;cursor:pointer;">'
        f'Download Excel</button></a>',
        unsafe_allow_html=True
    )

uploaded_file = st.file_uploader("Upload File Rekap", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        if 'Engineer' in df.columns:
            counts   = df['Engineer'].value_counts().reset_index()
            counts.columns = ['SAE', 'Progres']
            counts   = counts.sort_values(by='SAE').reset_index(drop=True)

            total_pm = int(counts['Progres'].sum())
            max_pm   = int(counts['Progres'].max())
            mvp_name = counts.loc[counts['Progres'] == max_pm, 'SAE'].iloc[0]

            img = generate_image(counts, total_pm, max_pm, mvp_name, date_str)

            st.image(img, use_container_width=True)

            buf = io.BytesIO()
            img.save(buf, format="PNG", dpi=(300, 300))
            buf.seek(0)

            st.download_button(
                label="📸 Download Gambar untuk WhatsApp",
                data=buf,
                file_name=f"rekap_pm_{date_str}.png",
                mime="image/png",
                use_container_width=True
            )

        else:
            st.error("Kolom 'Engineer' tidak ditemukan dalam file.")

    except Exception as e:
        st.error(f"Error: {e}")

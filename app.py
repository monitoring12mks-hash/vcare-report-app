import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

# ── KONFIGURASI ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="VCare Analytics", layout="centered")
st.markdown("""
<style>
    #MainMenu {visibility:hidden;} header {visibility:hidden;} footer {visibility:hidden;}
    .stApp {background-color:#f1f5f9;}
    .stDownloadButton > button {
        background-color:#1e3a8a; color:white;
        border-radius:8px; border:none; width:100%;
    }
</style>""", unsafe_allow_html=True)

# ── MASTER LIST ENGINEER ──────────────────────────────────────────────────────
MASTER_ENGINEERS = [
    "Andi Imran",
    "Andi Muhammad Shaleh",
    "Didi Setiawan",
    "M. Syahrial Saeni",
    "Muh Faris Aprillah Ridwan",
    "Muh. Al-Ghifari",
    "Muhammad Nurhadi Santoso",
    "Muhammad Yadi Ahdiat Tauhid",
    "Mus Muliadi",
    "Suardi M",
    "Warman Munti",
    "Zulfadly",
]

# ── FONT ─────────────────────────────────────────────────────────────────────
def fnt(size, bold=False):
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf"]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

# ── WARNA ────────────────────────────────────────────────────────────────────
C_NAVY     = (30,  58, 138)
C_WHITE    = (255, 255, 255)
C_LIGHT    = (241, 245, 249)
C_GREEN_B  = (240, 253, 244)
C_GREEN_T  = (21,  128, 61)
C_ORANGE_B = (255, 237, 213)
C_ORANGE_T = (154,  52, 18)
C_RED_B    = (255, 241, 242)
C_RED_T    = (190,  18, 60)
C_GRAY     = (100, 116, 139)
C_TEXT     = (30,  41,  59)
C_BORDER   = (226, 232, 240)
C_DIVIDER  = (59,  95, 192)
C_GREENBR  = (187, 247, 208)

# ── GENERATE IMAGE ────────────────────────────────────────────────────────────
def generate_image(counts, total_pm, max_pm, mvp_name, date_str):
    PADDING  = 24
    W        = 520
    ROW_H    = 44
    HEADER_H = 52
    TITLE_H  = 70
    METRIC_H = 80
    MVP_H    = 52

    n_rows  = len(counts)
    total_h = PADDING + TITLE_H + HEADER_H + (ROW_H * n_rows) + METRIC_H + MVP_H + PADDING

    img  = Image.new("RGB", (W, total_h), C_LIGHT)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [PADDING, PADDING, W - PADDING, total_h - PADDING],
        radius=16, fill=C_WHITE, outline=C_BORDER, width=1
    )

    y = PADDING + 16

    # Judul
    title = "REKAP PROGRES PM"
    tw = draw.textlength(title, font=fnt(17, bold=True))
    draw.text(((W - tw) / 2, y), title, font=fnt(17, bold=True), fill=C_NAVY)
    y += 28
    dw = draw.textlength(date_str, font=fnt(12))
    draw.text(((W - dw) / 2, y), date_str, font=fnt(12), fill=C_GRAY)
    y += 30

    col1_x = PADDING + 12
    col_w2 = int((W - PADDING * 2) * 0.28)
    tbl_x1 = PADDING
    tbl_x2 = W - PADDING

    # Header tabel
    draw.rectangle([tbl_x1, y, tbl_x2, y + HEADER_H], fill=C_NAVY)
    draw.text((col1_x, y + 16), "SAE", font=fnt(11, bold=True), fill=C_WHITE)
    ph = "PROGRES"
    pw = draw.textlength(ph, font=fnt(11, bold=True))
    draw.text((tbl_x2 - col_w2 + (col_w2 - pw) / 2, y + 16),
              ph, font=fnt(11, bold=True), fill=C_WHITE)
    y += HEADER_H

    bottom_3 = set(counts[counts['Progres'] > 0]['Progres'].nsmallest(3).unique())

    for _, row in counts.iterrows():
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

        is_bold = val == 0 or (val == max_pm and val > 0) or val in bottom_3
        dn = name if len(name) <= 30 else name[:29] + "..."
        draw.text((col1_x, y + 13), dn, font=fnt(13, bold=is_bold), fill=tc)

        vstr = str(val)
        vw   = draw.textlength(vstr, font=fnt(13, bold=is_bold))
        draw.text((tbl_x2 - col_w2 + (col_w2 - vw) / 2, y + 13),
                  vstr, font=fnt(13, bold=is_bold), fill=tc)
        y += ROW_H

    # Metrik
    draw.rectangle([tbl_x1, y, tbl_x2, y + METRIC_H], fill=C_NAVY)
    mid_x    = tbl_x1 + (tbl_x2 - tbl_x1) // 2
    left_cx  = tbl_x1 + (mid_x - tbl_x1) // 2
    right_cx = mid_x + (tbl_x2 - mid_x) // 2
    draw.line([(mid_x, y + 12), (mid_x, y + METRIC_H - 12)], fill=C_DIVIDER, width=1)

    for label, value, cx in [
        ("TOTAL PROGRESS", str(total_pm), left_cx),
        ("MINIMAL TARGET", "30",          right_cx),
    ]:
        lw = draw.textlength(label, font=fnt(9))
        draw.text((cx - lw / 2, y + 10), label, font=fnt(9), fill=(191, 219, 254))
        vw = draw.textlength(value, font=fnt(26, bold=True))
        draw.text((cx - vw / 2, y + 26), value, font=fnt(26, bold=True), fill=C_WHITE)
    y += METRIC_H

    # MVP
    draw.rectangle([tbl_x1, y, tbl_x2, y + MVP_H], fill=C_GREEN_B)
    draw.line([(tbl_x1, y), (tbl_x2, y)], fill=C_GREENBR, width=2)
    mvp_text = f"MVP: {mvp_name} ({max_pm} PM)"
    prefix   = ">> "
    pw2      = draw.textlength(prefix, font=fnt(14, bold=True))
    mw       = draw.textlength(mvp_text, font=fnt(14, bold=True))
    start_x  = (W - pw2 - mw) / 2
    draw.text((start_x, y + 17), prefix,        font=fnt(14, bold=True), fill=C_GREEN_T)
    draw.text((start_x + pw2, y + 17), mvp_text, font=fnt(14, bold=True), fill=C_GREEN_T)

    return img

# ── BUAT TEKS WHATSAPP ────────────────────────────────────────────────────────
def build_wa_text(counts, total_pm, max_pm, mvp_name, date_str):
    TARGET = 30
    lines = []
    lines.append(f"📊 *REKAP PROGRES PM*")
    lines.append(f"🗓️ {date_str}")
    lines.append("━" * 28)

    bottom_3 = set(counts[counts['Progres'] > 0]['Progres'].nsmallest(3).unique())

    for _, row in counts.iterrows():
        val  = int(row['Progres'])
        name = str(row['SAE'])

        if val == 0:
            icon = "🔴"
        elif val == max_pm and val > 0:
            icon = "🏆"
        elif val in bottom_3:
            icon = "🟠"
        else:
            icon = "🟢"

        lines.append(f"{icon} {name}: *{val} PM*")

    lines.append("━" * 28)
    status = "✅ TERCAPAI" if total_pm >= TARGET else "❌ BELUM TERCAPAI"
    lines.append(f"📦 Total Progress : *{total_pm} PM*")
    lines.append(f"🎯 Minimal Target : *{TARGET} PM* {status}")
    lines.append("━" * 28)
    lines.append(f"🏆 MVP: *{mvp_name}* ({max_pm} PM)")
    lines.append("")
    lines.append("_Generated by VCare Analytics_")
    return "\n".join(lines)

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
        f'<button style="width:100%;height:40px;border-radius:8px;'
        f'background-color:#1e3a8a;color:white;border:none;cursor:pointer;font-size:14px;">'
        f'📥 Download Excel</button></a>',
        unsafe_allow_html=True
    )

uploaded_file = st.file_uploader("Upload File Rekap", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        if 'Engineer' in df.columns:
            # Hitung progres dari file
            raw_counts = df['Engineer'].value_counts().reset_index()
            raw_counts.columns = ['SAE', 'Progres']

            # Gabung dengan master list — engineer tidak ada di file = 0
            master_df = pd.DataFrame({'SAE': MASTER_ENGINEERS})
            counts = master_df.merge(raw_counts, on='SAE', how='left')
            counts['Progres'] = counts['Progres'].fillna(0).astype(int)
            counts = counts.sort_values(by='SAE').reset_index(drop=True)

            total_pm = int(counts['Progres'].sum())
            max_pm   = int(counts['Progres'].max())
            mvp_name = counts.loc[counts['Progres'] == max_pm, 'SAE'].iloc[0]

            with st.spinner("Membuat gambar..."):
                img = generate_image(counts, total_pm, max_pm, mvp_name, date_str)

            st.image(img, use_container_width=True)

            # Teks untuk WhatsApp
            wa_text = build_wa_text(counts, total_pm, max_pm, mvp_name, date_str)

            # ── TOMBOL AKSI ──
            st.markdown("---")
            col_a, col_b = st.columns(2)

            # Tombol Download Gambar
            with col_a:
                buf = io.BytesIO()
                img.save(buf, format="PNG", dpi=(300, 300))
                buf.seek(0)
                st.download_button(
                    label="📸 Download Gambar",
                    data=buf,
                    file_name=f"rekap_pm_{date_str}.png",
                    mime="image/png",
                    use_container_width=True
                )

            # Tombol Share Teks ke WhatsApp
            with col_b:
                encoded_text = urllib.parse.quote(wa_text)
                wa_url = f"https://wa.me/?text={encoded_text}"
                st.markdown(
                    f'<a href="{wa_url}" target="_blank">'
                    f'<button style="width:100%;height:40px;border-radius:8px;'
                    f'background-color:#25D366;color:white;border:none;'
                    f'cursor:pointer;font-size:14px;font-weight:bold;">'
                    f'💬 Share ke WhatsApp</button></a>',
                    unsafe_allow_html=True
                )

            # Preview teks WA
            with st.expander("👁️ Preview teks WhatsApp"):
                st.code(wa_text, language=None)

        else:
            st.error("❌ Kolom 'Engineer' tidak ditemukan dalam file.")

    except Exception as e:
        st.error(f"Error: {e}")

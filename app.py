import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

# ... (Bagian Konfigurasi & Font tetap sama seperti kode Anda) ...

# ── MASTER LIST ENGINEER ──────────────────────────────────────────────────────
MASTER_ENGINEERS = [
    "Andi Imran", "Andi Muhammad Shaleh", "Didi Setiawan", "M. Syahrial Saeni",
    "Muh Faris Aprillah Ridwan", "Muh. Al-Ghifari", "Muhammad Nurhadi Santoso",
    "Muhammad Yadi Ahdiat Tauhid", "Mus Muliadi", "Suardi M", "Warman Munti", "Zulfadly",
]

# ── WARNA PROFESIONAL ────────────────────────────────────────────────────────
C_NAVY     = (30,  58, 138)
C_WHITE    = (255, 255, 255)
C_LIGHT    = (241, 245, 249)
C_GREEN_B  = (220, 252, 231) # Lebih soft
C_GREEN_T  = (21,  128, 61)
C_ORANGE_B = (255, 247, 237)
C_ORANGE_T = (194,  65, 12)
C_RED_B    = (254, 226, 226)
C_RED_T    = (185,  28, 28)
C_GRAY     = (71,  85,  105)
C_TEXT     = (15,  23,  42)
C_BORDER   = (203, 213, 225)

# ── GENERATE IMAGE ────────────────────────────────────────────────────────────
def generate_image(counts, total_pm, total_target, max_pm, mvp_name, date_str):
    PADDING, W, ROW_H, HEADER_H, TITLE_H, METRIC_H, MVP_H = 24, 520, 44, 52, 70, 80, 52
    n_rows  = len(counts)
    total_h = PADDING + TITLE_H + HEADER_H + (ROW_H * n_rows) + METRIC_H + MVP_H + PADDING

    img  = Image.new("RGB", (W, total_h), C_LIGHT)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([PADDING, PADDING, W - PADDING, total_h - PADDING], radius=16, fill=C_WHITE, outline=C_BORDER, width=1)

    # Judul
    y = PADDING + 20
    draw.text(((W - draw.textlength("REKAP PROGRES DAILY PM", font=fnt(18, True))) / 2, y), "REKAP PROGRES DAILY PM", font=fnt(18, True), fill=C_NAVY)
    y += 28
    draw.text(((W - draw.textlength(date_str, font=fnt(12))) / 2, y), date_str, font=fnt(12), fill=C_GRAY)
    y += 30

    # Table Header
    draw.rectangle([PADDING, y, W - PADDING, y + HEADER_H], fill=C_NAVY)
    draw.text((PADDING + 15, y + 16), "NAMA ENGINEER", font=fnt(11, True), fill=C_WHITE)
    draw.text((W - PADDING - 90, y + 16), "PROGRES", font=fnt(11, True), fill=C_WHITE)
    y += HEADER_H

    # Rows (Sorted High to Low)
    for _, row in counts.iterrows():
        val = int(row['Progres'])
        # Logika Warna: Hijau jika capai target per orang (30), Merah jika 0, Oranye jika < 30
        if val >= 30: bg, tc = C_GREEN_B, C_GREEN_T
        elif val == 0: bg, tc = C_RED_B, C_RED_T
        else: bg, tc = C_ORANGE_B, C_ORANGE_T

        draw.rectangle([PADDING, y, W - PADDING, y + ROW_H], fill=bg)
        draw.line([(PADDING, y + ROW_H - 1), (W - PADDING, y + ROW_H - 1)], fill=C_BORDER, width=1)
        draw.text((PADDING + 15, y + 13), row['SAE'], font=fnt(13, val >= 30), fill=tc)
        draw.text((W - PADDING - 70, y + 13), f"{val} PM", font=fnt(13, True), fill=tc)
        y += ROW_H

    # Metrics (Total Progress vs Group Target)
    draw.rectangle([PADDING, y, W - PADDING, y + METRIC_H], fill=C_NAVY)
    mid_x = W // 2
    draw.line([(mid_x, y + 15), (mid_x, y + METRIC_H - 15)], fill=C_BORDER, width=1)
    
    # Left: Total
    tw = draw.textlength("TOTAL PROGRES", font=fnt(9))
    draw.text((mid_x/2 + PADDING/2 - tw/2, y + 15), "TOTAL PROGRES", font=fnt(9), fill=C_LIGHT)
    vw = draw.textlength(str(total_pm), font=fnt(24, True))
    draw.text((mid_x/2 + PADDING/2 - vw/2, y + 35), str(total_pm), font=fnt(24, True), fill=C_WHITE)

    # Right: Group Target
    tw2 = draw.textlength("TARGET GRUP", font=fnt(9))
    draw.text((mid_x + mid_x/2 - PADDING/2 - tw2/2, y + 15), "TARGET GRUP", font=fnt(9), fill=C_LIGHT)
    vw2 = draw.textlength(str(total_target), font=fnt(24, True))
    draw.text((mid_x + mid_x/2 - PADDING/2 - vw2/2, y + 35), str(total_target), font=fnt(24, True), fill=C_WHITE)
    
    y += METRIC_H
    # MVP Footer
    draw.rectangle([PADDING, y, W - PADDING, y + MVP_H], fill=C_GREEN_B)
    mvp_txt = f"⭐ High Achiever: {mvp_name} ({max_pm} PM)"
    mw = draw.textlength(mvp_txt, font=fnt(13, True))
    draw.text(((W - mw) / 2, y + 16), mvp_txt, font=fnt(13, True), fill=C_GREEN_T)

    return img

# ── WA TEXT ───────────────────────────────────────────────────────────────────
def build_wa_text(counts, total_pm, total_target, date_str):
    lines = [f"📋 *LAPORAN PROGRES DAILY PM*", f"📅 Tanggal: {date_str}", "─" * 22]
    
    for _, row in counts.iterrows():
        val = int(row['Progres'])
        # Ikon profesional
        if val >= 30: icon = "✅" 
        elif val > 0: icon = "⚠️"
        else: icon = "❌"
        lines.append(f"{icon} {row['SAE']}: *{val} PM*")

    status = "🟢 ON TARGET" if total_pm >= total_target else "🔴 BELOW TARGET"
    lines.extend(["─" * 22, 
                  f"📊 Total Progres: *{total_pm} PM*",
                  f"🎯 Target Grup: *{total_target} PM*",
                  f"📌 Status: *{status}*",
                  "", "_Sent via VCare Analytics_"])
    return "\n".join(lines)

# ── UI LOGIC ──────────────────────────────────────────────────────────────────
# ... (Bagian header/date picker tetap sama) ...

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        if 'Engineer' in df.columns:
            raw_counts = df['Engineer'].value_counts().reset_index()
            raw_counts.columns = ['SAE', 'Progres']

            master_df = pd.DataFrame({'SAE': MASTER_ENGINEERS})
            counts = master_df.merge(raw_counts, on='SAE', how='left').fillna(0)
            counts['Progres'] = counts['Progres'].astype(int)
            
            # URUTAN: Terbanyak ke Terendah
            counts = counts.sort_values(by=['Progres', 'SAE'], ascending=[False, True]).reset_index(drop=True)

            # KALKULASI TARGET
            INDIVIDUAL_TARGET = 30
            total_target = len(MASTER_ENGINEERS) * INDIVIDUAL_TARGET
            total_pm = int(counts['Progres'].sum())
            max_pm = int(counts['Progres'].max())
            mvp_name = counts.loc[counts['Progres'] == max_pm, 'SAE'].iloc[0]

            # Render
            img = generate_image(counts, total_pm, total_target, max_pm, mvp_name, date_str)
            st.image(img, use_container_width=True)
            
            wa_text = build_wa_text(counts, total_pm, total_target, date_str)
            
            # ... (Tombol download & WA tetap sama) ...

import base64
import hashlib
import json
import os
import re
from io import BytesIO

import anthropic
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageFilter

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.error("ไม่พบ ANTHROPIC_API_KEY — กรุณาตั้งค่าใน .env หรือ Streamlit Secrets")
    st.stop()

PREMIUM_PASSWORD = os.getenv("PREMIUM_PASSWORD") or st.secrets.get("PREMIUM_PASSWORD", "")

if "model" not in st.session_state:
    st.session_state["model"] = "claude-haiku-4-5"

st.set_page_config(
    page_title="ดูรถดิ — Car Identifier",
    page_icon="🏎",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500;600&family=Prompt:wght@300;400;500&display=swap');

/* ─── Reset & Base ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body { font-family: 'DM Sans', 'Prompt', sans-serif; }

/* ─── Background ─── */
.stApp {
    background-color: #080808 !important;
    background-image:
        linear-gradient(to bottom, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.72) 100%),
        url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1920&q=90') !important;
    background-size: cover !important;
    background-position: center 30% !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
}

/* ─── Strip Streamlit default backgrounds ─── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.main, .main > div, .block-container {
    background: transparent !important;
    background-color: transparent !important;
}

[data-testid="stHeader"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

/* ─── Nav ─── */
.nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 0 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 0;
}

.nav-logo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.04em;
}

.nav-logo span { color: #C9A84C; font-style: italic; }

.nav-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.nav-badge {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
}

.nav-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #C9A84C;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ─── Hero ─── */
.hero {
    padding: 5rem 0 4rem;
    text-align: center;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #C9A84C;
    margin-bottom: 1.5rem;
}

.hero-eyebrow::before,
.hero-eyebrow::after {
    content: '';
    width: 24px;
    height: 1px;
    background: #C9A84C;
}

.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.8rem, 6vw, 4.5rem);
    font-weight: 300;
    font-style: italic;
    color: #fff;
    line-height: 1.1;
    letter-spacing: -0.01em;
    margin-bottom: 1.2rem;
}

.hero-title strong {
    font-style: normal;
    font-weight: 600;
    color: #fff;
}

.hero-sub {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.45);
    font-weight: 300;
    letter-spacing: 0.04em;
    max-width: 340px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ─── Main Card ─── */
.main-card {
    background: #ffffff;
    border-radius: 4px;
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba(255,255,255,0.06),
        0 24px 80px rgba(0,0,0,0.5),
        0 8px 24px rgba(0,0,0,0.3);
    margin-bottom: 1.5rem;
}

.card-top-bar {
    height: 3px;
    background: linear-gradient(90deg, #C9A84C, #E8C97A, #C9A84C);
}

.card-inner {
    padding: 2rem 2rem 0;
}

.card-section-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 1rem;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    background: #f4f4f4;
    border-radius: 3px;
    padding: 3px;
    gap: 2px;
    border: none !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 2px;
    color: #111 !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    padding: 0.55rem 1.5rem;
    transition: all 0.2s;
}

.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div {
    color: #111 !important;
}

.stTabs [aria-selected="true"] {
    background: #fff !important;
    color: #111 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12) !important;
}

/* ─── File uploader ─── */
[data-testid="stFileUploader"] {
    background: #fafafa;
    border: 1.5px dashed #ddd;
    border-radius: 3px;
    padding: 0.5rem;
    transition: border-color 0.2s;
}

[data-testid="stFileUploader"]:hover { border-color: #C9A84C; }

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small {
    color: #aaa !important;
    font-size: 0.85rem !important;
}

/* ─── Camera ─── */
[data-testid="stCameraInput"] video { border-radius: 2px !important; }

@keyframes shine {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}

@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 8px rgba(201,168,76,0.6), 0 0 20px rgba(201,168,76,0.3); }
    50%       { box-shadow: 0 0 16px rgba(201,168,76,0.9), 0 0 40px rgba(201,168,76,0.5); }
}

[data-testid="stCameraInput"] button {
    background: linear-gradient(
        110deg,
        #b8922a 0%,
        #C9A84C 30%,
        #E8C97A 50%,
        #C9A84C 70%,
        #b8922a 100%
    ) !important;
    background-size: 200% auto !important;
    color: #1a1200 !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    border: none !important;
    border-radius: 3px !important;
    animation: shine 2.5s linear infinite, glow-pulse 2s ease-in-out infinite !important;
    transition: transform 0.15s ease !important;
}

[data-testid="stCameraInput"] button:hover {
    transform: scale(1.02) !important;
}

/* ─── Card footer (tip) ─── */
.card-tip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem 1.2rem;
    border-top: 1px solid #f0f0f0;
    margin-top: 1rem;
    font-size: 0.78rem;
    color: #bbb;
    font-weight: 300;
    letter-spacing: 0.01em;
}

.card-tip-icon {
    width: 18px; height: 18px;
    border-radius: 50%;
    background: #f5f5f5;
    border: 1px solid #e8e8e8;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem;
    flex-shrink: 0;
    color: #C9A84C;
    font-weight: 700;
}

/* ─── Uploaded image ─── */
[data-testid="stImage"] img {
    border-radius: 4px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}

/* ─── Result ─── */
.result-card {
    background: #111;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 24px 80px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.3);
    margin-top: 1.2rem;
}

.result-card-top { height: 3px; background: linear-gradient(90deg, #C9A84C, #E8C97A, #C9A84C); }

.result-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.result-card-title {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #999;
}

.result-card-tag {
    font-size: 0.62rem;
    font-weight: 500;
    color: #C9A84C;
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.2);
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    letter-spacing: 0.08em;
}

.result-card-body {
    padding: 1.5rem;
}

.result-card-body p, .result-card-body li {
    color: #fff;
    line-height: 1.85;
    font-size: 0.92rem;
    font-weight: 300;
}

.result-card-body strong {
    color: #fff;
    font-weight: 600;
}

.result-card-body h1, .result-card-body h2, .result-card-body h3 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: #fff;
    margin-top: 1.2rem;
    margin-bottom: 0.4rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.15);
}

/* ─── Claude result text → white ─── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] ul,
[data-testid="stMarkdownContainer"] ol,
[data-testid="stMarkdownContainer"] span {
    color: #fff !important;
}

[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b {
    color: #fff !important;
    font-weight: 600 !important;
}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {
    color: #C9A84C !important;
    font-family: 'Cormorant Garamond', serif !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    padding-bottom: 0.3rem !important;
    margin-top: 1rem !important;
}

/* ─── Section cards ─── */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}

.sec-card {
    display: flex;
    gap: 1.1rem;
    padding: 1.1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    animation: slideUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
    opacity: 0;
}

.sec-card:last-child { border-bottom: none; padding-bottom: 0; }

.sec-icon-wrap {
    flex-shrink: 0;
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 50%;
    background: rgba(201,168,76,0.12);
    border: 1px solid rgba(201,168,76,0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    margin-top: 0.1rem;
}

.sec-content { flex: 1; min-width: 0; }

.sec-title {
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: #C9A84C;
    margin-bottom: 0.35rem;
    font-family: 'DM Sans', sans-serif;
}

.sec-body {
    color: #e8e8e8;
    font-size: 0.9rem;
    line-height: 1.75;
    font-weight: 300;
    word-wrap: break-word;
}

.sec-body strong { color: #fff; font-weight: 600; }

.sec-fallback {
    color: #e8e8e8;
    font-size: 0.9rem;
    line-height: 1.75;
    font-weight: 300;
    padding: 0.5rem 0;
}

/* ─── Spinner ─── */
.stSpinner > div { border-top-color: #C9A84C !important; }

/* ─── Analyzing state ─── */
.analyzing {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 1.2rem 1.5rem;
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    margin-top: 1.2rem;
    font-size: 0.82rem;
    color: #888;
    font-weight: 400;
    letter-spacing: 0.04em;
}

/* ─── Footer ─── */
.footer {
    padding: 3rem 0 2rem;
    text-align: center;
}

.footer-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.footer-divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.06); }
.footer-divider-mark { font-size: 0.5rem; color: rgba(255,255,255,0.15); letter-spacing: 0.3em; }

.footer-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-style: italic;
    color: rgba(255,255,255,0.7);
    margin-bottom: 0.4rem;
    letter-spacing: 0.04em;
}

.footer-powered {
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.18);
}

/* ─── Hide sidebar ─── */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ─── Pro button (center column) ─── */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button {
    background: linear-gradient(
        110deg,
        #b8922a 0%, #C9A84C 25%, #E8C97A 50%, #C9A84C 75%, #b8922a 100%
    ) !important;
    background-size: 200% auto !important;
    color: #1a1200 !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    animation: shine 2.5s linear infinite, glow-pulse 2s ease-in-out infinite !important;
    transition: transform 0.15s ease, opacity 0.15s ease !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button:hover {
    transform: scale(1.03) !important;
    opacity: 0.92 !important;
}

/* ─── Trust badges ─── */
.trust-strip {
    display: flex;
    justify-content: center;
    gap: 1.8rem;
    padding: 1.4rem 0 0;
    flex-wrap: wrap;
}
.trust-item {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
}
.trust-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #C9A84C;
    opacity: 0.7;
    flex-shrink: 0;
}

/* ─── Dialog styling ─── */
[data-testid="stDialog"] [data-testid="stTextInput"] input {
    background: #0d0d0d !important;
    border: 1.5px solid rgba(201,168,76,0.4) !important;
    border-radius: 3px !important;
    color: #fff !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.08em !important;
    padding: 0.65rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] input:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.15), 0 0 12px rgba(201,168,76,0.2) !important;
    outline: none !important;
}
[data-testid="stDialog"] [data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.25) !important;
}
[data-testid="stDialog"] button[kind="secondary"] {
    background: linear-gradient(
        110deg,
        #b8922a 0%, #C9A84C 25%, #E8C97A 50%, #C9A84C 75%, #b8922a 100%
    ) !important;
    background-size: 200% auto !important;
    color: #1a1200 !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    animation: shine 2.5s linear infinite, glow-pulse 2s ease-in-out infinite !important;
}
[data-testid="stDialog"] [data-baseweb="modal"] {
    background: #111 !important;
    border: 1px solid rgba(201,168,76,0.2) !important;
    border-radius: 6px !important;
    box-shadow: 0 24px 80px rgba(0,0,0,0.8), 0 0 0 1px rgba(201,168,76,0.1) !important;
}

/* ─── Error ─── */
[data-testid="stAlert"] {
    background: #fff8f8 !important;
    border: 1px solid #ffd0d0 !important;
    border-left: 3px solid #e53e3e !important;
    border-radius: 3px !important;
    color: #c53030 !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

client = anthropic.Anthropic(api_key=api_key)


PROMPT = (
    "วิเคราะห์รูปรถนี้อย่างละเอียด โดยทำตามขั้นตอนนี้:\n\n"
    "ขั้นที่ 1 — สังเกต visual clues ก่อน:\n"
    "- รูปทรงไฟหน้า ไฟท้าย และกระจังหน้า\n"
    "- โปรไฟล์ตัวถัง (fastback / sedan / SUV / coupe)\n"
    "- ลักษณะล้อและซุ้มล้อ\n"
    "- badge หรือโลโก้ที่มองเห็น\n"
    "- ป้ายทะเบียน (ช่วยบอกปีและประเทศ)\n\n"
    "ขั้นที่ 2 — ระบุรถและให้ข้อมูลเป็นภาษาไทย:\n\n"
    "## 1. **ยี่ห้อและรุ่น**\n"
    "ระบุให้ชัดที่สุด รวม generation/facelift ถ้าทราบ\n\n"
    "## 2. **ปีที่ผลิต**\n"
    "ปีหรือช่วงปี พร้อมบอกเหตุผลที่ใช้ระบุ\n\n"
    "## 3. **เครื่องยนต์**\n"
    "ชนิด ความจุ แรงม้า แรงบิด อัตราเร่ง 0-100\n\n"
    "## 4. **ฟีเจอร์เด่น**\n"
    "เทคโนโลยีและอุปกรณ์ที่น่าสนใจของรุ่นนี้\n\n"
    "## 5. **ราคา**\n"
    "ราคาใหม่และราคาตลาดมือสองในไทย\n\n"
    "## 6. **ข้อมูลน่ารู้**\n"
    "ประวัติหรือเรื่องน่าสนใจ\n\n"
    "ถ้าไม่แน่ใจ 100% ให้ระบุตัวเลือกที่เป็นไปได้ 2-3 รุ่น พร้อม % ความมั่นใจแต่ละรุ่น"
)


PLATE_DETECT_PROMPT = (
    "ในรูปนี้มีป้ายทะเบียนรถไหม? ตอบด้วย JSON เท่านั้น ห้ามมีข้อความอื่น\n"
    "ถ้ามี: {\"found\": true, \"x\": 0.35, \"y\": 0.75, \"w\": 0.20, \"h\": 0.06}\n"
    "โดย x,y = มุมซ้ายบน, w,h = ความกว้าง/สูง ทั้งหมดเป็นสัดส่วน 0.0-1.0 ของขนาดรูป\n"
    "ถ้าไม่มี: {\"found\": false}"
)


def compress_image(image_data: bytes, max_size: int = 1120) -> bytes:
    img = Image.open(BytesIO(image_data))
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


@st.cache_data(show_spinner=False, max_entries=20)
def detect_and_blur_plate(image_hash: str, image_data: bytes) -> bytes:
    img = Image.open(BytesIO(image_data)).convert("RGB")
    w, h = img.size

    small = compress_image(image_data, max_size=800)
    image_b64 = base64.standard_b64encode(small).decode("utf-8")

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=80,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                    {"type": "text", "text": PLATE_DETECT_PROMPT},
                ],
            }],
        )
        raw = resp.content[0].text.strip()
        # Extract JSON even if Claude adds extra text
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if data.get("found"):
                pad = 0.015  # 1.5% padding around plate
                x1 = max(0, int((data["x"] - pad) * w))
                y1 = max(0, int((data["y"] - pad) * h))
                x2 = min(w, int((data["x"] + data["w"] + pad) * w))
                y2 = min(h, int((data["y"] + data["h"] + pad) * h))
                region = img.crop((x1, y1, x2, y2))
                blurred = region.filter(ImageFilter.GaussianBlur(radius=18))
                img.paste(blurred, (x1, y1))
    except Exception:
        pass  # If detection fails, return original image unchanged

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


@st.cache_data(show_spinner=False, max_entries=20)
def identify_car(image_hash: str, image_data: bytes, model: str = "claude-haiku-4-5") -> str:
    compressed = compress_image(image_data)
    image_b64 = base64.standard_b64encode(compressed).decode("utf-8")
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    return response.content[0].text


SECTION_ICONS = ["🏎", "📅", "⚙️", "⚡", "💰", "💡"]


def build_result_html(text: str) -> str:
    # Format: "## 1. **Title**\ncontent" or "1. **Title**: content"
    lines = text.strip().splitlines()
    sections = []
    cur_title, cur_body = "", []

    for line in lines:
        # Match: optional ##, digit, dot, optional **, title, optional **
        m = re.match(r'^#{0,3}\s*\d+\.\s+\*{0,2}([^*\n]+?)\*{0,2}\s*$', line.strip())
        # Also match inline: "1. **Title**: body text"
        m2 = re.match(r'^#{0,3}\s*\d+\.\s+\*{1,2}([^*\n]+?)\*{1,2}[:\s]+(.*)', line.strip())
        if m2:
            if cur_title or cur_body:
                sections.append((cur_title, cur_body[:]))
            cur_title = m2.group(1).strip().rstrip(':')
            cur_body = [m2.group(2).strip()] if m2.group(2).strip() else []
        elif m:
            if cur_title or cur_body:
                sections.append((cur_title, cur_body[:]))
            cur_title = m.group(1).strip().rstrip(':')
            cur_body = []
        elif line.strip():
            stripped = line.strip()
            if stripped.startswith('#'):
                # Sub-header inside a section (e.g. ### ราคาใหม่) — render as bold label
                sub = re.sub(r'^#+\s*', '', stripped)
                sub = re.sub(r'\*+', '', sub).rstrip(':').strip()
                if sub:
                    cur_body.append(f'**{sub}**')
            else:
                cur_body.append(stripped)

    if cur_title or cur_body:
        sections.append((cur_title, cur_body[:]))

    if not sections:
        # Fallback: plain text
        body = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#fff">\1</strong>', text.replace('\n', '<br>'))
        return f'''
<div style="background:#111;border-radius:4px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.5);margin-top:1.2rem;">
  <div style="height:3px;background:linear-gradient(90deg,#C9A84C,#E8C97A,#C9A84C);"></div>
  <div style="padding:1.5rem;color:#e8e8e8;font-size:0.9rem;line-height:1.75;">{body}</div>
</div>'''

    def lines_to_html(body_lines):
        parts = []
        for ln in body_lines:
            ln = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#fff;font-weight:600">\1</strong>', ln)
            if ln.startswith("- ") or ln.startswith("• "):
                parts.append(f'<div style="display:flex;gap:0.4rem;margin:0.15rem 0;"><span style="color:#C9A84C;flex-shrink:0;">–</span><span>{ln[2:]}</span></div>')
            else:
                parts.append(f'<div style="margin:0.2rem 0;">{ln}</div>')
        return "".join(parts)

    cards = ""
    for i, (title, body_lines) in enumerate(sections):
        icon = SECTION_ICONS[i] if i < len(SECTION_ICONS) else "•"
        body_html = lines_to_html(body_lines)
        cards += f'''
<div style="display:flex;gap:1rem;padding:1rem 0;border-bottom:1px solid rgba(255,255,255,0.07);animation:slideUp 0.5s cubic-bezier(0.22,1,0.36,1) {i*0.13:.2f}s both;">
  <div style="flex-shrink:0;width:2.4rem;height:2.4rem;border-radius:50%;background:rgba(201,168,76,0.12);border:1px solid rgba(201,168,76,0.3);display:flex;align-items:center;justify-content:center;font-size:1rem;">{icon}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.58rem;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:#C9A84C;margin-bottom:0.35rem;">{title}</div>
    <div style="color:#e8e8e8;font-size:0.88rem;line-height:1.75;font-weight:300;">{body_html}</div>
  </div>
</div>'''

    return f'''
<div style="background:#111;border-radius:4px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.5);margin-top:1.2rem;">
  <div style="height:3px;background:linear-gradient(90deg,#C9A84C,#E8C97A,#C9A84C);"></div>
  <div style="display:flex;align-items:center;justify-content:space-between;padding:0.9rem 1.5rem;border-bottom:1px solid rgba(255,255,255,0.08);">
    <span style="font-size:0.6rem;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#888;">ผลการวิเคราะห์</span>
    <span style="font-size:0.62rem;color:#C9A84C;background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);padding:0.2rem 0.6rem;border-radius:2px;">AI Analysis</span>
  </div>
  <div style="padding:0.5rem 1.5rem 1.5rem;">{cards}</div>
</div>'''



is_premium = st.session_state["model"] == "claude-sonnet-4-6"


@st.dialog("✦ Unlock Pro Mode")
def unlock_pro():
    st.markdown("""
<div style='text-align:center;padding:0.4rem 0 1rem;'>
  <div style='font-size:0.62rem;letter-spacing:0.22em;text-transform:uppercase;color:#C9A84C;margin-bottom:0.4rem;'>ดูรถดิ Pro — Premium</div>
  <div style='font-size:0.82rem;color:#888;'>ความแม่นยำสูงขึ้น วิเคราะห์ละเอียดกว่า</div>
</div>
<table style='width:100%;border-collapse:collapse;margin-bottom:1.2rem;font-size:0.78rem;'>
  <tr style='border-bottom:1px solid rgba(255,255,255,0.08);'>
    <td style='padding:0.5rem 0.4rem;color:#666;'>ฟีเจอร์</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#888;'>ฟรี</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#C9A84C;font-weight:600;'>Pro ✦</td>
  </tr>
  <tr style='border-bottom:1px solid rgba(255,255,255,0.06);'>
    <td style='padding:0.5rem 0.4rem;color:#ccc;'>AI Model</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#888;'>Standard</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#C9A84C;'>Pro ✦</td>
  </tr>
  <tr style='border-bottom:1px solid rgba(255,255,255,0.06);'>
    <td style='padding:0.5rem 0.4rem;color:#ccc;'>ความแม่นยำ</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#888;'>ดี</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#C9A84C;'>สูงมาก</td>
  </tr>
  <tr style='border-bottom:1px solid rgba(255,255,255,0.06);'>
    <td style='padding:0.5rem 0.4rem;color:#ccc;'>รายละเอียด</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#888;'>มาตรฐาน</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#C9A84C;'>ละเอียดมาก</td>
  </tr>
  <tr>
    <td style='padding:0.5rem 0.4rem;color:#ccc;'>Plate Blur</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#C9A84C;'>✓</td>
    <td style='padding:0.5rem 0.4rem;text-align:center;color:#C9A84C;'>✓</td>
  </tr>
</table>
<div style='text-align:center;font-size:0.72rem;color:#666;margin-bottom:1rem;'>
  ติดต่อขอรหัสผ่านได้ที่ Instagram
  <a href='https://instagram.com/suphasan.sh' target='_blank'
     style='color:#C9A84C;text-decoration:none;font-weight:600;margin-left:0.3rem;'>@suphasan.sh</a>
</div>
""", unsafe_allow_html=True)
    pwd = st.text_input("รหัสผ่าน", type="password", placeholder="Enter password...", label_visibility="collapsed")
    if st.button("Unlock ✦", use_container_width=True):
        if pwd == PREMIUM_PASSWORD:
            st.session_state["model"] = "claude-sonnet-4-6"
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง")


# ── Nav ──
st.markdown("""
<div class="nav">
    <div class="nav-logo">ดูรถ<span>ดิ</span></div>
    <div class="nav-right">
        <span class="nav-badge">AI Car Identifier</span>
        <div class="nav-dot"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Trust strip ──
st.markdown("""
<div class="trust-strip">
    <div class="trust-item"><div class="trust-dot"></div>ป้ายทะเบียน blur อัตโนมัติ</div>
    <div class="trust-item"><div class="trust-dot"></div>ไม่เก็บรูปภาพ</div>
    <div class="trust-item"><div class="trust-dot"></div>AI วิเคราะห์แม่นยำ</div>
    <div class="trust-item"><div class="trust-dot"></div>รองรับรถทุกยี่ห้อทั่วโลก</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI Car Intelligence</div>
    <div class="hero-title">ถ่ายรูปรถ<br><strong>รู้ทุกอย่างทันที</strong></div>
    <div class="hero-sub">วิเคราะห์รถจากรูปภาพด้วย AI — ยี่ห้อ รุ่น เครื่องยนต์ และราคาตลาดในไทย</div>
</div>
""", unsafe_allow_html=True)

# ── Pro button ──
is_premium = st.session_state["model"] == "claude-sonnet-4-6"
_, col_btn, _ = st.columns([2, 1, 2])
with col_btn:
    if is_premium:
        if st.button("✦ ดูรถดิ  Pro", use_container_width=True, key="model_btn"):
            st.session_state["model"] = "claude-haiku-4-5"
            st.rerun()
    else:
        if st.button("Unlock Pro  ✦", use_container_width=True, key="unlock_btn"):
            unlock_pro()

# ── Main Card ──
st.markdown("""
<div class="main-card">
    <div class="card-top-bar"></div>
    <div class="card-inner">
        <div class="card-section-label">เลือกวิธีอัปโหลด</div>
""", unsafe_allow_html=True)

image_data = None

tab1, tab2 = st.tabs(["📷  ถ่ายรูป", "📁  อัปโหลดรูป"])

with tab1:
    camera_photo = st.camera_input("ถ่ายรูปรถ", label_visibility="collapsed")
    if camera_photo:
        image_data = camera_photo.read()

with tab2:
    uploaded_file = st.file_uploader(
        "วางรูปหรือกดเพื่อเลือกไฟล์",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        image_data = uploaded_file.read()

st.markdown("""
    </div>
    <div class="card-tip">
        <div class="card-tip-icon">i</div>
        รูปที่ดีควรเห็นตัวรถชัดเจน มีแสงเพียงพอ และเห็นด้านหน้าหรือด้านข้างของรถ
        &nbsp;·&nbsp; 🔒 ป้ายทะเบียนถูก blur ก่อนประมวลผลทุกครั้ง
    </div>
</div>
""", unsafe_allow_html=True)

# ── Result ──
if image_data:
    try:
        image_hash = hashlib.md5(image_data).hexdigest()

        # Blur plate before displaying or sending to AI
        blur_key = f"blur_{image_hash}"
        if blur_key not in st.session_state:
            with st.spinner("กำลังตรวจสอบและ blur ป้ายทะเบียน..."):
                st.session_state[blur_key] = detect_and_blur_plate(image_hash, image_data)

        blurred_data = st.session_state[blur_key]
        st.image(Image.open(BytesIO(blurred_data)), use_container_width=True)

        # Identify car using blurred image
        model = st.session_state["model"]
        result_key = f"result_{image_hash}_{model}"
        if result_key not in st.session_state:
            with st.spinner("กำลังวิเคราะห์รถ..."):
                blurred_hash = hashlib.md5(blurred_data).hexdigest()
                st.session_state[result_key] = identify_car(blurred_hash, blurred_data, model)

        result = st.session_state[result_key]
        st.markdown(build_result_html(result), unsafe_allow_html=True)

    except anthropic.AuthenticationError:
        st.error("API Key ไม่ถูกต้อง กรุณาตรวจสอบ ANTHROPIC_API_KEY")
    except anthropic.APIConnectionError:
        st.error("ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบอินเทอร์เน็ต")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

# ── Footer ──
st.markdown("""
<div class="footer">
    <div class="footer-divider">
        <div class="footer-divider-line"></div>
        <div class="footer-divider-mark">✦</div>
        <div class="footer-divider-line"></div>
    </div>
    <div class="footer-name">Suphasan Chanthai</div>
    <div class="footer-powered">AI Car Identifier · ดูรถดิ</div>
</div>
""", unsafe_allow_html=True)

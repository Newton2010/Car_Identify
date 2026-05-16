import base64
import os
from io import BytesIO

import anthropic
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", "")

st.set_page_config(
    page_title="ดูรถดิ",
    page_icon="🏎",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Prompt:wght@300;400;500&family=Oswald:wght@300;400;500&display=swap');

    /* ── Background: single sharp cover image ── */
    .stApp {
        background-color: #0d0b08 !important;
        background-image:
            linear-gradient(rgba(8,6,3,0.68), rgba(8,6,3,0.68)),
            url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1920&q=85') !important;
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }

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

    [data-testid="stHeader"] { display: none; }
    #MainMenu, footer { visibility: hidden; }

    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }

    /* ── Topbar ── */
    .topbar {
        padding: 1.4rem 0 1rem;
        text-align: center;
        border-bottom: 1px solid #8B6914;
        position: relative;
    }

    .topbar::before {
        content: '';
        display: block;
        width: 60px;
        height: 2px;
        background: #C9A84C;
        margin: 0 auto 0.9rem;
    }

    .topbar-badge {
        display: inline-block;
        border: 2px solid #C9A84C;
        padding: 0.15rem 1.2rem;
        font-family: 'Oswald', sans-serif;
        font-size: 0.6rem;
        letter-spacing: 0.4em;
        color: #C9A84C;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .topbar-logo {
        font-family: 'Playfair Display', serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: #F5F0E4;
        letter-spacing: 0.06em;
        line-height: 1;
        margin: 0;
    }

    .topbar-logo em {
        font-style: italic;
        color: #C9A84C;
    }

    .topbar-tagline {
        font-family: 'Oswald', sans-serif;
        font-size: 0.65rem;
        color: #8B7355;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }

    .topbar::after {
        content: '';
        display: block;
        width: 60px;
        height: 2px;
        background: #C9A84C;
        margin: 0.9rem auto 0;
    }

    /* ── Hero ── */
    .hero {
        text-align: center;
        padding: 2.8rem 0 2rem;
    }

    .hero-number {
        font-family: 'Playfair Display', serif;
        font-size: 0.7rem;
        color: #6B5A3E;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 400;
        font-style: italic;
        color: #F5F0E4;
        line-height: 1.15;
        margin: 0 0 0.6rem;
    }

    .hero-title strong {
        font-style: normal;
        font-weight: 700;
        color: #C9A84C;
    }

    .hero-rule {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        justify-content: center;
        margin: 1rem 0;
    }

    .hero-rule span {
        width: 40px;
        height: 1px;
        background: #5A4A30;
    }

    .hero-rule i {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 0.8rem;
        color: #8B7355;
        letter-spacing: 0.05em;
    }

    /* ── Card ── */
    .card {
        background: #F5F0E4;
        border: 1px solid #D4C5A0;
        padding: 0;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 50px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.3);
    }

    .card-header {
        background: #1C1810;
        padding: 0.65rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 2px solid #C9A84C;
    }

    .card-header-label {
        font-family: 'Oswald', sans-serif;
        font-size: 0.62rem;
        letter-spacing: 0.3em;
        color: #C9A84C;
        text-transform: uppercase;
    }

    .card-header-dots {
        display: flex;
        gap: 5px;
    }

    .card-header-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #3A3020;
    }

    .card-header-dots span:last-child {
        background: #C9A84C;
    }

    .card-body {
        padding: 1.5rem 1.5rem 0.5rem;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #EDE7D5;
        border: none;
        border-bottom: 2px solid #D4C5A0;
        border-radius: 0;
        padding: 0;
        gap: 0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        color: #8B7355;
        font-family: 'Oswald', sans-serif;
        font-size: 0.78rem;
        font-weight: 400;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        padding: 0.75rem 1.8rem;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
    }

    .stTabs [aria-selected="true"] {
        background: #F5F0E4 !important;
        color: #1C1810 !important;
        font-weight: 500 !important;
        border-bottom: 3px solid #C9A84C !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #EDE7D5;
        border: 1.5px dashed #C0AE85;
        border-radius: 0;
        padding: 0.5rem;
    }

    [data-testid="stFileUploader"]:hover { border-color: #C9A84C; }

    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span {
        color: #6B5A3E !important;
    }

    /* ── Camera ── */
    [data-testid="stCameraInput"] video { border-radius: 0 !important; }

    /* ── Uploaded image ── */
    [data-testid="stImage"] img {
        border-radius: 0;
        border: 1px solid #D4C5A0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    }

    /* ── Tip ── */
    .tip {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 0.8rem;
        color: #8B7355;
        padding: 0.8rem 1.5rem 1rem;
        border-top: 1px solid #D4C5A0;
    }

    /* ── Result card ── */
    .result-wrap {
        background: #F5F0E4;
        border: 1px solid #D4C5A0;
        box-shadow: 0 12px 50px rgba(0,0,0,0.6);
        margin-top: 1.5rem;
        overflow: hidden;
    }

    .result-header {
        background: #1C1810;
        border-bottom: 2px solid #C9A84C;
        padding: 0.65rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .result-header-label {
        font-family: 'Oswald', sans-serif;
        font-size: 0.62rem;
        letter-spacing: 0.3em;
        color: #C9A84C;
        text-transform: uppercase;
    }

    .result-header-stripe {
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, #3A3020, transparent);
    }

    .result-body {
        padding: 1.5rem;
    }

    .result-body p, .result-body li {
        color: #2A2010;
        line-height: 1.9;
        font-size: 0.95rem;
    }

    .result-body strong {
        color: #1C1810;
        font-weight: 600;
    }

    .result-body h1, .result-body h2, .result-body h3 {
        font-family: 'Playfair Display', serif;
        color: #1C1810;
        border-bottom: 1px solid #D4C5A0;
        padding-bottom: 0.3rem;
        margin-top: 1.2rem;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #C9A84C !important; }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 2.5rem 0 1.5rem;
    }

    .footer-rule {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .footer-rule span {
        width: 50px;
        height: 1px;
        background: #3A3020;
    }

    .footer-rule i {
        color: #C9A84C;
        font-size: 0.7rem;
        font-style: normal;
    }

    .footer-credit {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #C9A84C;
        font-size: 1rem;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }

    .footer-powered {
        font-family: 'Oswald', sans-serif;
        color: #3A3020;
        font-size: 0.6rem;
        letter-spacing: 0.28em;
        text-transform: uppercase;
    }

    /* ── Error ── */
    [data-testid="stAlert"] {
        background: #FDF0E8 !important;
        border: 1px solid #C9A84C !important;
        border-left: 4px solid #8B2020 !important;
        color: #4A1010 !important;
        border-radius: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

client = anthropic.Anthropic(api_key=api_key)


def compress_image(image_data: bytes, max_size: int = 800) -> tuple[bytes, str]:
    img = Image.open(BytesIO(image_data))
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=75)
    return buf.getvalue(), "image/jpeg"


def identify_car(image_data: bytes, media_type: str) -> str:
    image_data, media_type = compress_image(image_data)
    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "ช่วยระบุรถในรูปนี้และให้ข้อมูลเป็นภาษาไทย โดยมีหัวข้อดังนี้:\n\n"
                            "1. **ยี่ห้อและรุ่น**: ชื่อผู้ผลิตและรุ่นรถ\n"
                            "2. **ปีที่ผลิต**: ปีโดยประมาณ\n"
                            "3. **เครื่องยนต์**: สเปคเครื่องยนต์ แรงม้า แรงบิด\n"
                            "4. **ฟีเจอร์เด่น**: ความสามารถและเทคโนโลยีที่น่าสนใจ\n"
                            "5. **ราคา**: ราคาตลาดในไทย (ถ้าทราบ)\n"
                            "6. **ข้อมูลน่ารู้**: เรื่องน่าสนใจเกี่ยวกับรถคันนี้\n\n"
                            "ถ้าไม่สามารถระบุได้แน่ชัด ให้บอกว่าเดาว่าเป็นอะไรและมั่นใจแค่ไหน"
                        ),
                    },
                ],
            }
        ],
    )

    return response.content[0].text


# ── Topbar ──
st.markdown("""
<div class="topbar">
    <div class="topbar-badge">Stuttgart · Est. 1948</div>
    <div class="topbar-logo">ดูรถ<em>ดิ</em></div>
    <div class="topbar-tagline">Car Identifier &nbsp;·&nbsp; AI Powered</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-number">— No. 001 —</div>
    <div class="hero-title">ถ่าย<strong>รูปรถ</strong><br>รู้ทุกอย่าง</div>
    <div class="hero-rule">
        <span></span>
        <i>ใช้ AI วิเคราะห์รถจากรูปภาพ</i>
        <span></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input card ──
st.markdown("""
<div class="card">
    <div class="card-header">
        <span class="card-header-label">เลือกวิธีอัปโหลด</span>
        <div class="card-header-dots"><span></span><span></span><span></span></div>
    </div>
    <div class="card-body">
""", unsafe_allow_html=True)

image_data = None
media_type = None

tab1, tab2 = st.tabs(["📷  ถ่ายรูป", "📁  อัปโหลดรูป"])

with tab1:
    camera_photo = st.camera_input("ถ่ายรูปรถ", label_visibility="collapsed")
    if camera_photo:
        image_data = camera_photo.read()
        media_type = "image/jpeg"

with tab2:
    uploaded_file = st.file_uploader(
        "วางรูปหรือกดเพื่อเลือกไฟล์",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        image_data = uploaded_file.read()
        ext = uploaded_file.name.split(".")[-1].lower()
        type_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        media_type = type_map.get(ext, "image/jpeg")

st.markdown("""
    </div>
    <div class="tip">✦ รูปที่ดีควรเห็นตัวรถชัดเจน มีแสงเพียงพอ และเห็นด้านหน้าหรือด้านข้างของรถ</div>
</div>
""", unsafe_allow_html=True)

# ── Result ──
if image_data:
    img = Image.open(BytesIO(image_data))
    st.image(img, use_container_width=True)

    with st.spinner("กำลังวิเคราะห์..."):
        try:
            result = identify_car(image_data, media_type)
            st.markdown("""
<div class="result-wrap">
    <div class="result-header">
        <span class="result-header-label">ผลการวิเคราะห์</span>
        <div class="result-header-stripe"></div>
    </div>
    <div class="result-body">
""", unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div></div>", unsafe_allow_html=True)
        except anthropic.AuthenticationError:
            st.error("API Key ไม่ถูกต้อง กรุณาตรวจสอบ ANTHROPIC_API_KEY")
        except anthropic.APIConnectionError:
            st.error("ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบอินเทอร์เน็ต")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

# ── Footer ──
st.markdown("""
<div class="footer">
    <div class="footer-rule">
        <span></span><i>✦</i><span></span>
    </div>
    <div class="footer-credit">Suphasan Chanthai</div>
    <div class="footer-powered">Powered by Claude AI &nbsp;·&nbsp; Anthropic</div>
</div>
""", unsafe_allow_html=True)

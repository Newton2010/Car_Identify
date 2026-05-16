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
    color: #888;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    padding: 0.55rem 1.5rem;
    transition: all 0.2s;
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
    background: #fff;
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
    border-bottom: 1px solid #f0f0f0;
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
    color: #333;
    line-height: 1.85;
    font-size: 0.92rem;
    font-weight: 300;
}

.result-card-body strong {
    color: #111;
    font-weight: 600;
}

.result-card-body h1, .result-card-body h2, .result-card-body h3 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: #111;
    margin-top: 1.2rem;
    margin-bottom: 0.4rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #f0f0f0;
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


def compress_image(image_data: bytes, max_size: int = 900) -> tuple[bytes, str]:
    img = Image.open(BytesIO(image_data))
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=80)
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
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64},
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

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Powered by Claude AI</div>
    <div class="hero-title">ถ่ายรูปรถ<br><strong>รู้ทุกอย่างทันที</strong></div>
    <div class="hero-sub">วิเคราะห์รถจากรูปภาพด้วย AI — ยี่ห้อ รุ่น เครื่องยนต์ และราคาตลาดในไทย</div>
</div>
""", unsafe_allow_html=True)

# ── Main Card ──
st.markdown("""
<div class="main-card">
    <div class="card-top-bar"></div>
    <div class="card-inner">
        <div class="card-section-label">เลือกวิธีอัปโหลด</div>
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
    <div class="card-tip">
        <div class="card-tip-icon">i</div>
        รูปที่ดีควรเห็นตัวรถชัดเจน มีแสงเพียงพอ และเห็นด้านหน้าหรือด้านข้างของรถ
    </div>
</div>
""", unsafe_allow_html=True)

# ── Result ──
if image_data:
    img = Image.open(BytesIO(image_data))
    st.image(img, use_container_width=True)

    with st.spinner("กำลังวิเคราะห์รถ..."):
        try:
            result = identify_car(image_data, media_type)
            st.markdown("""
<div class="result-card">
    <div class="result-card-top"></div>
    <div class="result-card-header">
        <span class="result-card-title">ผลการวิเคราะห์</span>
        <span class="result-card-tag">AI Analysis</span>
    </div>
    <div class="result-card-body">
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
    <div class="footer-divider">
        <div class="footer-divider-line"></div>
        <div class="footer-divider-mark">✦</div>
        <div class="footer-divider-line"></div>
    </div>
    <div class="footer-name">Suphasan Chanthai</div>
    <div class="footer-powered">Powered by Claude AI · Anthropic</div>
</div>
""", unsafe_allow_html=True)

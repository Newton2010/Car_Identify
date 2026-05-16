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
    page_icon="🚗",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@200;300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }

    /* ── Background mosaic ── */
    .bg-mosaic {
        position: fixed;
        inset: 0;
        z-index: 0;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(3, 1fr);
        gap: 3px;
        pointer-events: none;
    }

    .bg-mosaic img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: brightness(0.28) saturate(0.7);
    }

    .bg-overlay {
        position: fixed;
        inset: 0;
        z-index: 1;
        background: radial-gradient(ellipse at center, rgba(10,10,10,0.55) 0%, rgba(10,10,10,0.88) 100%);
        pointer-events: none;
    }

    /* ── App shell ── */
    .stApp {
        background: transparent;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 2;
    }

    [data-testid="stHeader"] { display: none; }
    #MainMenu, footer { visibility: hidden; }

    /* ── Top bar ── */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.1rem 0 1.1rem;
        border-bottom: 1px solid rgba(255,255,255,0.12);
        margin-bottom: 0;
    }

    .topbar-logo {
        font-size: 1.3rem;
        font-weight: 600;
        color: #fff;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    .topbar-logo span { color: #D5001C; }

    .topbar-tag {
        font-size: 0.65rem;
        color: #888;
        letter-spacing: 0.22em;
        text-transform: uppercase;
    }

    /* ── Hero ── */
    .hero {
        padding: 3.5rem 0 2.5rem;
        text-align: center;
    }

    .hero-eyebrow {
        font-size: 0.68rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #D5001C;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 3.6rem;
        font-weight: 200;
        color: #fff;
        letter-spacing: 0.04em;
        line-height: 1.1;
        margin: 0 0 0.3rem;
    }

    .hero-title strong {
        font-weight: 700;
        color: #fff;
    }

    .hero-sub {
        color: #aaa;
        font-size: 0.9rem;
        font-weight: 300;
        letter-spacing: 0.05em;
        margin-top: 1rem;
    }

    /* ── Card ── */
    .card {
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-top: 3px solid #D5001C;
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        padding: 1.8rem;
        margin-bottom: 1.5rem;
    }

    .card-label {
        font-size: 0.65rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #ccc;
        margin-bottom: 1.2rem;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 0;
        padding: 3px;
        gap: 3px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        color: #ddd;
        font-family: 'Prompt', sans-serif;
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.1em;
        padding: 0.6rem 1.8rem;
    }

    .stTabs [aria-selected="true"] {
        background: #D5001C !important;
        color: #fff !important;
        font-weight: 500 !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.05);
        border: 1.5px dashed rgba(255,255,255,0.25);
        border-radius: 0;
        padding: 0.5rem;
        transition: border-color 0.2s;
    }

    [data-testid="stFileUploader"]:hover { border-color: #D5001C; }

    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span {
        color: #ccc !important;
    }

    /* ── Camera ── */
    [data-testid="stCameraInput"] video { border-radius: 0 !important; }

    /* ── Uploaded image ── */
    [data-testid="stImage"] img {
        border-radius: 0;
        border: 1px solid #2a2a2a;
    }

    /* ── Result ── */
    .result-wrap {
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-top: 3px solid #D5001C;
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        padding: 2rem;
        margin-top: 1.5rem;
    }

    .result-eyebrow {
        font-size: 0.65rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #D5001C;
        margin-bottom: 1.2rem;
    }

    .result-wrap p, .result-wrap li {
        color: #e0e0e0;
        line-height: 1.9;
        font-weight: 300;
    }

    .result-wrap strong { color: #fff; font-weight: 600; }

    .result-wrap h1, .result-wrap h2, .result-wrap h3 {
        color: #fff;
        font-weight: 500;
    }

    /* ── Tip ── */
    .tip {
        font-size: 0.78rem;
        color: #bbb;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        letter-spacing: 0.02em;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #D5001C !important; }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 2.5rem 0 1.5rem;
    }

    .footer-credit {
        color: #eee;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        margin-bottom: 0.4rem;
    }

    .footer-powered {
        color: #777;
        font-size: 0.65rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    /* ── Error ── */
    [data-testid="stAlert"] {
        background: rgba(213, 0, 28, 0.1) !important;
        border: 1px solid rgba(213, 0, 28, 0.3) !important;
        color: #ff6b6b !important;
        border-radius: 0 !important;
    }
</style>

<!-- Background mosaic of cars -->
<div class="bg-mosaic">
    <img src="https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1555353540-64580b51c258?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1542362567-b07e54358753?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1471479917193-f00955256257?w=600&q=60" />
    <img src="https://images.unsplash.com/photo-1580274455191-1c62238fa333?w=600&q=60" />
</div>
<div class="bg-overlay"></div>
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


# Top bar
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">ดูรถ<span>ดิ</span></div>
    <div class="topbar-tag">Car Identifier · AI Powered</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Identify Any Car Instantly</div>
    <div class="hero-title">ถ่าย<strong>รูปรถ</strong><br>รู้ทุกอย่าง</div>
    <div class="hero-sub">ใช้ AI วิเคราะห์รถจากรูปภาพ — ยี่ห้อ รุ่น เครื่องยนต์ และราคา</div>
</div>
""", unsafe_allow_html=True)

# Input card
st.markdown('<div class="card"><div class="card-label">เลือกวิธีอัปโหลด</div>', unsafe_allow_html=True)

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

st.markdown('<div class="tip">💡 รูปที่ดีควรเห็นตัวรถชัดเจน มีแสงเพียงพอ และเห็นด้านหน้าหรือด้านข้างของรถ</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Result
if image_data:
    img = Image.open(BytesIO(image_data))
    st.image(img, use_container_width=True)

    with st.spinner("กำลังวิเคราะห์..."):
        try:
            result = identify_car(image_data, media_type)
            st.markdown('<div class="result-wrap">', unsafe_allow_html=True)
            st.markdown('<div class="result-eyebrow">ผลการวิเคราะห์</div>', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
        except anthropic.AuthenticationError:
            st.error("API Key ไม่ถูกต้อง กรุณาตรวจสอบ ANTHROPIC_API_KEY")
        except anthropic.APIConnectionError:
            st.error("ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบอินเทอร์เน็ต")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

st.markdown("""
<div class="footer">
    <div class="footer-credit">Created by Suphasan Chanthai</div>
    <div class="footer-powered">Powered by Claude AI &nbsp;·&nbsp; Anthropic</div>
</div>
""", unsafe_allow_html=True)

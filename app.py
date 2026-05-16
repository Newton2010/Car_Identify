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
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }

    .stApp {
        background-color: #f5f5f0;
    }

    /* Top bar */
    .topbar {
        background: #fff;
        border-bottom: 3px solid #D5001C;
        padding: 1.2rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -1rem -1rem 0 -1rem;
    }

    .topbar-logo {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .topbar-logo span {
        color: #D5001C;
    }

    .topbar-tag {
        font-size: 0.7rem;
        color: #999;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* Hero */
    .hero {
        background: #fff;
        padding: 3rem 2rem 2.5rem;
        text-align: center;
        margin-bottom: 0;
        border-bottom: 1px solid #e8e8e8;
    }

    .hero-eyebrow {
        font-size: 0.72rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #D5001C;
        font-weight: 500;
        margin-bottom: 0.75rem;
    }

    .hero-title {
        font-size: 3.2rem;
        font-weight: 300;
        color: #1a1a1a;
        letter-spacing: 0.05em;
        line-height: 1.1;
        margin: 0;
    }

    .hero-title strong {
        font-weight: 600;
    }

    .hero-sub {
        color: #666;
        font-size: 0.95rem;
        margin-top: 1rem;
        font-weight: 300;
        letter-spacing: 0.02em;
    }

    /* Section */
    .section {
        background: #fff;
        border-radius: 0;
        padding: 2rem;
        margin-top: 1.5rem;
        border: 1px solid #e8e8e8;
    }

    .section-label {
        font-size: 0.68rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #999;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #f5f5f0;
        border-radius: 0;
        padding: 3px;
        gap: 3px;
        border: 1px solid #e0e0e0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        color: #666;
        font-family: 'Prompt', sans-serif;
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.08em;
        padding: 0.6rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background: #D5001C !important;
        color: #fff !important;
        font-weight: 500 !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #fafafa;
        border: 1.5px dashed #d0d0d0;
        border-radius: 0;
        padding: 0.5rem;
        transition: border-color 0.2s;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #D5001C;
    }

    /* Camera */
    [data-testid="stCameraInput"] video {
        border-radius: 0 !important;
    }

    /* Image */
    [data-testid="stImage"] img {
        border-radius: 0;
        border: 1px solid #e0e0e0;
    }

    /* Result */
    .result-wrap {
        background: #fff;
        border-top: 3px solid #D5001C;
        border-left: 1px solid #e8e8e8;
        border-right: 1px solid #e8e8e8;
        border-bottom: 1px solid #e8e8e8;
        padding: 2rem;
        margin-top: 1.5rem;
    }

    .result-eyebrow {
        font-size: 0.68rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #D5001C;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }

    .result-wrap p, .result-wrap li {
        color: #333;
        line-height: 1.9;
        font-weight: 300;
    }

    .result-wrap strong {
        color: #1a1a1a;
        font-weight: 600;
    }

    .result-wrap h1, .result-wrap h2, .result-wrap h3 {
        color: #1a1a1a;
        font-weight: 500;
    }

    /* Tip */
    .tip {
        font-size: 0.8rem;
        color: #999;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        letter-spacing: 0.02em;
    }

    /* Divider line */
    .rule {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 2rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #bbb;
        font-size: 0.72rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 2.5rem 0 1.5rem;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #D5001C !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
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

# Input section
st.markdown('<div class="section"><div class="section-label">เลือกวิธีอัปโหลด</div>', unsafe_allow_html=True)

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

st.markdown('<div class="footer">Powered by Claude AI &nbsp;·&nbsp; Anthropic</div>', unsafe_allow_html=True)

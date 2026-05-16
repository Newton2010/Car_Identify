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
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }

    .hero-icon {
        font-size: 4rem;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .hero-sub {
        color: #c0c0d0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1.5rem;
    }

    .result-card {
        background: rgba(247, 151, 30, 0.08);
        border: 1px solid rgba(247, 151, 30, 0.3);
        border-radius: 20px;
        padding: 1.5rem 1.5rem 1rem;
        margin-top: 1.5rem;
    }

    .result-title {
        color: #ffd200;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }

    .result-card p, .result-card li {
        color: #e0e0f0;
        line-height: 1.8;
    }

    .result-card strong {
        color: #ffd200;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #c0c0d0;
        font-family: 'Prompt', sans-serif;
        font-weight: 400;
        padding: 0.5rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #f7971e, #ffd200) !important;
        color: #1a1a2e !important;
        font-weight: 600 !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03);
        border: 2px dashed rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 1rem;
        transition: border-color 0.3s;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(247, 151, 30, 0.5);
    }

    /* Camera */
    [data-testid="stCameraInput"] {
        border-radius: 16px;
        overflow: hidden;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #ffd200 !important;
    }

    /* Image */
    [data-testid="stImage"] img {
        border-radius: 16px;
        border: 2px solid rgba(255,255,255,0.1);
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}

    .footer {
        text-align: center;
        color: rgba(255,255,255,0.3);
        font-size: 0.8rem;
        padding: 2rem 0 1rem;
    }

    .tip-box {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #ffd200;
        border-radius: 0 10px 10px 0;
        padding: 0.75rem 1rem;
        color: #c0c0d0;
        font-size: 0.88rem;
        margin-top: 1rem;
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


# Hero section
st.markdown("""
<div class="hero">
    <div class="hero-icon">🚗</div>
    <div class="hero-title">ดูรถดิ</div>
    <div class="hero-sub">ถ่ายรูปรถ แล้วเราจะบอกทุกอย่างเกี่ยวกับรถคันนั้น</div>
</div>
""", unsafe_allow_html=True)

# Upload section
st.markdown('<div class="card">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📁  อัปโหลดรูป", "📷  ถ่ายรูป"])

image_data = None
media_type = None

with tab1:
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

with tab2:
    camera_photo = st.camera_input("ถ่ายรูปรถ", label_visibility="collapsed")
    if camera_photo:
        image_data = camera_photo.read()
        media_type = "image/jpeg"

st.markdown("""
<div class="tip-box">
    💡 <strong>เทิป:</strong> รูปที่ดีควรเห็นตัวรถชัดเจน มีแสงเพียงพอ และเห็นด้านหน้าหรือด้านข้างของรถ
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Result section
if image_data:
    img = Image.open(BytesIO(image_data))
    st.image(img, use_container_width=True)

    with st.spinner("🔍 กำลังวิเคราะห์รถ..."):
        try:
            result = identify_car(image_data, media_type)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">📋 ผลการวิเคราะห์</div>', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
        except anthropic.AuthenticationError:
            st.error("❌ API Key ไม่ถูกต้อง กรุณาตรวจสอบ ANTHROPIC_API_KEY")
        except anthropic.APIConnectionError:
            st.error("❌ ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบอินเทอร์เน็ต")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")

st.markdown('<div class="footer">ขับเคลื่อนโดย Claude AI · Anthropic</div>', unsafe_allow_html=True)

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

st.title("🚗 ดูรถดิ")
st.markdown("##### ถ่ายหรืออัปโหลดรูปรถ แล้วเราจะบอกทุกอย่างเกี่ยวกับรถคันนั้น")

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


st.markdown("---")

tab1, tab2 = st.tabs(["📁 อัปโหลดรูป", "📷 ถ่ายรูป"])

image_data = None
media_type = None

with tab1:
    uploaded_file = st.file_uploader(
        "เลือกรูปรถที่ต้องการ",
        type=["jpg", "jpeg", "png", "webp"],
        help="อัปโหลดรูปรถที่ชัดเจน เห็นตัวรถเต็มคัน",
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

if image_data:
    st.markdown("### รูปรถของคุณ")
    img = Image.open(BytesIO(image_data))
    st.image(img, use_container_width=True)

    st.markdown("### ข้อมูลรถ")
    with st.spinner("กำลังวิเคราะห์รถ..."):
        try:
            result = identify_car(image_data, media_type)
            st.markdown(result)
        except anthropic.AuthenticationError:
            st.error("API Key ไม่ถูกต้อง กรุณาตรวจสอบ ANTHROPIC_API_KEY")
        except anthropic.APIConnectionError:
            st.error("ไม่สามารถเชื่อมต่อได้ กรุณาตรวจสอบอินเทอร์เน็ต")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

st.markdown("---")
st.caption("ขับเคลื่อนโดย Claude AI — Anthropic")

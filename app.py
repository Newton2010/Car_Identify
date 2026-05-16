import base64
import os
from io import BytesIO

import anthropic
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Support both local .env and Streamlit Cloud secrets
api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", "")

st.set_page_config(
    page_title="Car Identifier",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 Car Identifier")
st.markdown("Upload or take a photo of a car to identify it and get detailed information.")

client = anthropic.Anthropic(api_key=api_key)


def identify_car(image_data: bytes, media_type: str) -> str:
    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
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
                            "Please identify this car and provide detailed information about it. "
                            "Include the following in your response:\n\n"
                            "1. **Make & Model**: The manufacturer and model name\n"
                            "2. **Year**: Estimated year or year range if not exact\n"
                            "3. **Trim/Variant**: Specific trim level or variant if identifiable\n"
                            "4. **Engine & Performance**: Engine specs, horsepower, torque\n"
                            "5. **Key Features**: Notable features and technology\n"
                            "6. **Price Range**: Approximate original MSRP (new) and current market value\n"
                            "7. **Fun Facts**: Interesting facts or history about this car\n\n"
                            "If you cannot identify the exact car, describe what you can see "
                            "and give your best estimate with confidence level."
                        ),
                    },
                ],
            }
        ],
    )

    return response.content[0].text


tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Take Photo"])

image_data = None
media_type = None

with tab1:
    uploaded_file = st.file_uploader(
        "Choose a car image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload a clear photo of the car you want to identify.",
    )
    if uploaded_file:
        image_data = uploaded_file.read()
        ext = uploaded_file.name.split(".")[-1].lower()
        type_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        media_type = type_map.get(ext, "image/jpeg")

with tab2:
    camera_photo = st.camera_input("Take a photo of a car")
    if camera_photo:
        image_data = camera_photo.read()
        media_type = "image/jpeg"

if image_data:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Your Car Photo")
        img = Image.open(BytesIO(image_data))
        st.image(img, use_container_width=True)

    with col2:
        st.subheader("Car Details")
        with st.spinner("Identifying car..."):
            try:
                result = identify_car(image_data, media_type)
                st.markdown(result)
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your ANTHROPIC_API_KEY.")
            except anthropic.APIConnectionError:
                st.error("Connection error. Please check your internet connection.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.divider()
st.caption("Powered by Claude AI — Anthropic")


import streamlit as st
from PIL import Image, ImageEnhance, ImageOps

st.set_page_config(page_title="Flynexis AI Test Tool", page_icon="🚀", layout="centered")
st.title("Flynexis AI Edit Tool - Live Test 🚀")
st.write("यह एक टेस्ट टूल है जिससे आप चेक कर सकते हैं कि आपका सेटअप सही काम कर रहा है या नहीं।")

uploaded_file = st.file_uploader("टेस्ट करने के लिए एक फोटो अपलोड करें (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        st.image(image, use_container_width=True)
        
    st.subheader("AI Edit Options")
    edit_type = st.radio("कौन सा इफ़ेक्ट अप्लाई करना है?", ["Black & White (Grayscale)", "Boost Brightness (Light)", "Invert Colors"])
    
    if edit_type == "Black & White (Grayscale)":
        edited_image = ImageOps.grayscale(image)
    elif edit_type == "Boost Brightness (Light)":
        enhancer = ImageEnhance.Brightness(image)
        edited_image = enhancer.enhance(1.5)
    else:
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        edited_image = ImageOps.invert(image)
        
    with col2:
        st.subheader("Edited Image")
        st.image(edited_image, use_container_width=True)
        st.success("AI Edit सफलतापूर्वक अप्लाई हो गया है! 🎉")

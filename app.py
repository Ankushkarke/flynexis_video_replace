import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os

st.set_page_config(page_title="Flynexis Video Template Tool", page_icon="🎬", layout="centered")
st.title("Flynexis AI Video Template Editor 🎬")
st.write("यहाँ यूजर अपनी फोटो अपलोड करके पहले से बने वीडियो टेम्प्लेट में अपनी फोटो फिट कर सकता है।")

# 1. टेम्प्लेट वीडियो का पाथ (Path)
# ध्यान दें: आपको अपनी रिपोजिटरी में एक छोटा वीडियो 'template.mp4' नाम से अपलोड करना होगा
TEMPLATE_VIDEO = "template.mp4"

# चेक करना कि बैकएंड में टेम्प्लेट वीडियो मौजूद है या नहीं
if not os.path.exists(TEMPLATE_VIDEO):
    st.warning("कृपया पहले अपनी GitHub रिपोजिटरी में 'template.mp4' नाम का एक डिफॉल्ट वीडियो अपलोड करें।")
else:
    st.info("वीडियो टेम्प्लेट लोड हो गया है। नीचे अपनी फोटो अपलोड करें!")

    # 2. यूजर से फोटो अपलोड करवाना
    uploaded_image = st.file_uploader("वीडियो में अपनी फोटो जोड़ने के लिए अपलोड करें (JPG, PNG)", type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        # अपलोड की गई फोटो को सर्वर पर अस्थाई रूप से सेव करना
        with open("user_photo.jpg", "wb") as f:
            f.write(uploaded_image.getbuffer())
        
        st.success("आपकी फोटो लोड हो गई है। अब वीडियो रेंडर करने के लिए नीचे बटन दबाएं।")
        
        # 3. वीडियो रेंडर करने का बटन
        if st.button("🚀 Create My Custom Video (Render)"):
            with st.spinner("आपका वीडियो बैकएंड में रेंडर हो रहा है... कृपया 10-15 सेकंड रुकें।"):
                try:
                    # टेम्प्लेट वीडियो को लोड करना
                    video_clip = VideoFileClip(TEMPLATE_VIDEO)
                    video_duration = video_clip.duration # वीडियो की लंबाई जानना
                    
                    # यूजर की फोटो को वीडियो क्लिप में बदलना (पूरे वीडियो के समय के लिए)
                    # यहाँ हम फोटो का साइज छोटा करके वीडियो के ऊपर कोने में सेट कर रहे हैं (जैसे वाटरमार्क या फ्रेम)
                    image_clip = (ImageClip("user_photo.jpg")
                                  .set_duration(video_duration)
                                  .resize(width=200) # फोटो की चौड़ाई 200 पिक्सल सेट करना
                                  .set_position(("right", "top"))) # ऊपर दाईं तरफ सेट करना
                    
                    # दोनों को आपस में मर्ज (Combine) करना
                    final_video = CompositeVideoClip([video_clip, image_clip])
                    
                    # फाइनल वीडियो को सेव करना
                    output_filename = "output_processed.mp4"
                    final_video.write_videofile(output_filename, codec="libx264", audio_codec="aac")
                    
                    # फाइलों को बंद करना (ताकि मेमोरी खाली हो सके)
                    video_clip.close()
                    image_clip.close()
                    
                    st.success("🎉 आपका वीडियो सफलतापूर्वक रेंडर हो गया है!")
                    
                    # 4. यूजर को वीडियो डाउनलोड करने का ऑप्शन देना
                    with open(output_filename, "rb") as file:
                        st.download_button(
                            label="📥 Download Video",
                            data=file,
                            file_name="flynexis_edited_video.mp4",
                            mime="video/mp4"
                        )
                        
                except Exception as e:
                    st.error(f"रेंडरिंग में कोई दिक्कत आई: {e}")


import streamlit as st
from PIL import Image
import os

try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
except ModuleNotFoundError:
    from moviepy import VideoFileClip, ImageClip, concatenate_videoclips

st.set_page_config(page_title="Flynexis Fast Reel Cloner", page_icon="⚡", layout="centered")
st.title("Flynexis AI Reel Cloner (Fast Version) ⚡")
st.write("फ्री सर्वर के लिए विशेष रूप से ऑप्टिमाइज़्ड। बिना किसी खर्च के अपनी वीडियो तुरंत बनाएं।")

if 'video_ready' not in st.session_state:
    st.session_state.video_ready = False
    st.session_state.slots_data = []
    st.session_state.master_path = ""

# 1. ओरिजिनल वीडियो अपलोड
uploaded_master = st.file_uploader("1. ओरिजिनल वीडियो अपलोड करें (कृपया 5-10 सेकंड की छोटी वीडियो का उपयोग करें)", type=["mp4"])

if uploaded_master is not None and not st.session_state.video_ready:
    with st.spinner("वीडियो का स्ट्रक्चर तैयार हो रहा है..."):
        master_path = "user_style_fast.mp4"
        with open(master_path, "wb") as f:
            f.write(uploaded_master.read())
        
        st.session_state.master_path = master_path
        
        # फ्री सर्वर पर मेमोरी बचाने के लिए वीडियो को सीधे 3 बराबर भागों में बांटना (बिना भारी AI के)
        clip = VideoFileClip(master_path)
        total_duration = clip.duration
        clip.close()
        
        part_duration = total_duration / 3
        st.session_state.slots_data = [(i * part_duration, (i + 1) * part_duration) for i in range(3)]
        st.session_state.video_ready = True
        st.success(f"तैयार! यह वीडियो {total_duration:.1f} सेकंड की है। AI ने इसमें बदलने के लिए 3 बराबर स्लॉट्स बनाए हैं।")

# 2. यूजर की फोटो इनपुट
if st.session_state.video_ready:
    st.write("---")
    st.subheader("2. इन 3 स्लॉट्स के लिए अपनी 3 फोटोज अपलोड करें")
    
    cols = st.columns(3)
    user_photos = []
    for i in range(3):
        with cols[i]:
            st.write(f"स्लॉट {i+1}")
            img_file = st.file_uploader(f"फोटो {i+1}", type=["jpg", "png", "jpeg"], key=f"fast_img_{i}")
            user_photos.append(img_file)
            
    # 3. सुपरफास्ट रेंडरिंग प्रक्रिया
    st.write("---")
    if st.button("🎬 मेरी वीडियो तुरंत रेंडर करो"):
        if not all(user_photos):
            st.error("कृपया वीडियो बनाने के लिए तीनों स्लॉट्स में फोटो अपलोड करें!")
        else:
            with st.spinner("स्पीड मोड में वीडियो जनरेट हो रही है..."):
                try:
                    orig_clip = VideoFileClip(st.session_state.master_path)
                    new_clips = []
                    
                    # सर्वर की कैपेसिटी के हिसाब से टारगेट साइज (छोटा साइज = सुपरफास्ट स्पीड)
                    target_w = 480
                    target_h = int(orig_clip.h * (480 / orig_clip.w))
                    # सुनिश्चित करें कि हाइट 2 से डिवाइड हो सके (वीडियो कोडिंग के लिए ज़रूरी है)
                    if target_h % 2 != 0: target_h += 1 
                    
                    for idx, (start, end) in enumerate(st.session_state.slots_data):
                        dur = end - start
                        orig_sub = orig_clip.subclip(start, end)
                        
                        # फोटो प्रोसेस और रीसाइज करना
                        img = Image.open(user_photos[idx])
                        img_resized = img.resize((target_w, target_h))
                        img_path = f"fast_tmp_{idx}.png"
                        img_resized.save(img_path)
                        
                        # हल्का फोटो क्लिप बनाना
                        img_clip = ImageClip(img_path).set_duration(dur)
                        if orig_sub.audio is not None:
                            img_clip = img_clip.set_audio(orig_sub.audio)
                            
                        new_clips.append(img_clip)
                    
                    # फाइनल मर्ज
                    final_clip = concatenate_videoclips(new_clips, method="compose")
                    output_name = "fast_output.mp4"
                    
                    # सबसे ज़रूरी: FPS को कम (12) करना और 'ultrafast' प्रीसेट का उपयोग करना जिससे स्पीड 5 गुना बढ़ जाती है
                    final_clip.write_videofile(
                        output_name,
                        fps=12,
                        codec="libx264",
                        audio_codec="aac",
                        preset="ultrafast",
                        logger=None
                    )
                    
                    orig_clip.close()
                    final_clip.close()
                    
                    st.balloons()
                    st.success("आपकी वीडियो सफलतापूर्वक और तेजी से रेंडर हो गई है! 🎉")
                    
                    with open(output_name, 'rb') as vf:
                        v_bytes = vf.read()
                        st.video(v_bytes)
                        st.download_button(
                            label="📥 Download Fast Video",
                            data=v_bytes,
                            file_name="flynexis_fast_video.mp4",
                            mime="video/mp4"
                        )
                        
                except Exception as e:
                    st.error(f"एरर आया: {e}")
                    
    if st.button("🔄 रीसेट करें"):
        st.session_state.video_ready = False
        st.session_state.slots_data = []
        st.session_state.master_path = ""
        st.rerun()

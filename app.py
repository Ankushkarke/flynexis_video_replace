import streamlit as st
from PIL import Image
import os

# मूवीपाइ इम्पोर्ट को संभालना
try:
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
except ModuleNotFoundError:
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

from scenedetect import detect, ContentDetector

st.set_page_config(page_title="Flynexis Reel Template Cloner", page_icon="🔥", layout="centered")
st.title("Flynexis AI Reel Template Cloner 🔥")
st.write("इंस्टाग्राम या किसी भी वीडियो को यहाँ अपलोड करें, हमारा AI उसकी एडिटिंग स्टाइल (Cuts) को कॉपी करके आपकी फोटो से वैसी ही नई वीडियो बना देगा!")

# स्टेट मैनेजमेंट (डेटा सुरक्षित रखने के लिए)
if 'video_analyzed' not in st.session_state:
    st.session_state.video_analyzed = False
    st.session_state.cuts_timing = []
    st.session_state.master_video = ""

# स्टेप 1: ओरिजिनल रील्स/वीडियो अपलोड करना
uploaded_master = st.file_uploader("1. वो ओरिजिनल वीडियो अपलोड करें जिसकी तरह आप अपनी वीडियो बनाना चाहते हैं", type=["mp4", "mov", "avi"])

if uploaded_master is not None and not st.session_state.video_analyzed:
    with st.spinner("AI वीडियो के एडिटिंग पैटर्न्स और बीट्स को स्कैन कर रहा है..."):
        # ओरिजिनल वीडियो को सर्वर पर सेव करना
        master_path = "user_master_style.mp4"
        with open(master_path, "wb") as f:
            f.write(uploaded_master.read())
        
        st.session_state.master_video = master_path
        
        # AI Scene Detection की मदद से वीडियो के ट्रांजिशन पॉइंट्स (कट्स) ढूंढना
        scene_list = detect(master_path, ContentDetector(threshold=28.0))
        
        calculated_cuts = []
        for scene in scene_list:
            calculated_cuts.append((scene[0].get_seconds(), scene[1].get_seconds()))
        
        # अगर वीडियो बहुत सिंपल है और AI को कट्स नहीं मिले, तो ऑटोमैटिकली उसे 4 बराबर हिस्सों में बांट देना
        if len(calculated_cuts) == 0:
            clip = VideoFileClip(master_path)
            dur = clip.duration
            clip.close()
            step = dur / 4
            calculated_cuts = [(i*step, (i+1)*step) for i in range(4)]
            
        st.session_state.cuts_timing = calculated_cuts
        st.session_state.video_analyzed = True
        st.success(f"एनालिसिस पूरा हुआ! AI ने इस वीडियो स्टाइल में कुल {len(calculated_cuts)} कट्स/फोटोज के स्लॉट्स ढूंढे हैं।")

# स्टेप 2: यूजर से रिप्लेस करने के लिए फोटोज लेना
if st.session_state.video_analyzed:
    st.write("---")
    st.subheader("2. अब अपनी फोटोज अपलोड करें जो आप इस वीडियो स्टाइल में फिट करना चाहते हैं")
    
    slots_count = len(st.session_state.cuts_timing)
    user_photos = []
    
    # ग्रिड लेआउट में फोटो अपलोड करने के बॉक्स दिखाना
    cols = st.columns(min(slots_count, 4))
    for i in range(slots_count):
        col_idx = i % 4
        with cols[col_idx]:
            st.write(f"स्लॉट {i+1}")
            img_file = st.file_uploader(f"फोटो {i+1} चुनें", type=["jpg", "png", "jpeg"], key=f"photo_{i}")
            user_photos.append(img_file)
            
    # स्टेप 3: रेंडरिंग और वीडियो जेनरेशन
    st.write("---")
    if st.button("🎬 मेरी वीडियो तैयार करो (Render Video)"):
        # यह चेक करना कि यूजर ने सभी स्लॉट्स में फोटो अपलोड की है या नहीं
        if not all(user_photos):
            st.error("कृपया सभी स्लॉट्स में अपनी फोटो अपलोड करें ताकि वीडियो पूरी बन सके!")
        else:
            with st.spinner("AI आपकी फोटोज को ओरिजिनल वीडियो की टाइमिंग और बीट्स पर सिंक कर रहा है..."):
                try:
                    orig_clip = VideoFileClip(st.session_state.master_video)
                    new_video_parts = []
                    
                    # हर एक हिस्से में यूजर की फोटो को फिट करना
                    for idx, (start_time, end_time) in enumerate(st.session_state.cuts_timing):
                        duration = end_time - start_time
                        orig_sub = orig_clip.subclip(start_time, end_time)
                        
                        # फोटो को लोड और ओरिजिनल वीडियो के साइज में रीसाइज करना
                        img = Image.open(user_photos[idx])
                        img_path = f"temp_user_{idx}.png"
                        img_resized = img.resize((orig_clip.w, orig_clip.h))
                        img_resized.save(img_path)
                        
                        # फोटो क्लिप बनाकर ओरिजिनल वीडियो का म्यूजिक (ऑडियो) उसमें जोड़ना
                        img_clip = ImageClip(img_path).set_duration(duration)
                        if orig_sub.audio is not None:
                            img_clip = img_clip.set_audio(orig_sub.audio)
                            
                        new_video_parts.append(img_clip)
                        
                    # सभी फोटो क्लिप्स को जोड़कर फाइनल वीडियो बनाना
                    final_output_clip = concatenate_videoclips(new_video_parts, method="compose")
                    
                    output_file_name = "flynexis_replicated_reel.mp4"
                    final_output_clip.write_videofile(
                        output_file_name,
                        fps=15,
                        codec="libx264",
                        audio_codec="aac",
                        logger=None
                    )
                    
                    # मेमोरी खाली करना
                    orig_clip.close()
                    final_output_clip.close()
                    
                    st.balloons()
                    st.success("आपकी शानदार कस्टमाइज्ड वीडियो तैयार है! 🎉")
                    
                    # वीडियो प्ले करना और डाउनलोड बटन देना
                    with open(output_file_name, 'rb') as vf:
                        video_bytes = vf.read()
                        st.video(video_bytes)
                        st.download_button(
                            label="📥 Download My Video",
                            data=video_bytes,
                            file_name="my_cloned_reel.mp4",
                            mime="video/mp4"
                        )
                        
                except Exception as e:
                    st.error(f"वीडियो बनाने में कोई दिक्कत आई: {e}")
                    
    # रीसेट बटन
    if st.button("🔄 नया वीडियो अपलोड करें (Reset)"):
        st.session_state.video_analyzed = False
        st.session_state.cuts_timing = []
        st.session_state.master_video = ""
        st.rerun()

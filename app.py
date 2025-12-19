import streamlit as st
import cv2
import os
import time
import numpy as np
from PIL import Image

# --- CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP ---
st.set_page_config(page_title="Hệ thống Video Stream AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000000; color: #00ff00; font-family: 'Courier New', Courier, monospace; }
    .video-container { border: 2px solid #00ff00; border-radius: 10px; overflow: hidden; background: #050505; }
    .rec-label { color: red; font-weight: bold; animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    /* Giấu các nút mặc định */
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

STORAGE = "video_frames"
if not os.path.exists(STORAGE): os.makedirs(STORAGE)

# --- KHÓA BẢO MẬT ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔐 TRUY CẬP HỆ THỐNG</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Mật khẩu (1111):", type="password")
    if pwd == "1111":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- CHẾ ĐỘ HOẠT ĐỘNG ---
mode = st.sidebar.radio("CHẾ ĐỘ", ["🖥️ MÀN HÌNH GIÁM SÁT", "🎥 MÁY QUAY VIDEO"])

# --- MÁY QUAY (TỰ ĐỘNG QUAY KHÔNG CẦN BẤM) ---
if mode == "🎥 MÁY QUAY VIDEO":
    st.markdown("<h3>🎥 TRẠM PHÁT VIDEO TRỰC TUYẾN</h3>", unsafe_allow_html=True)
    cam_name = st.text_input("Tên Camera:", "CAM_MAIN")
    
    # Sử dụng HTML5 Video API để quay liên tục thay vì camera_input
    # Đây là kịch bản tự động quay mà không cần nút bấm
    st.markdown("---")
    st.info("Hệ thống đang sử dụng luồng Video Stream tốc độ cao.")

    # Widget Camera của Streamlit (Dùng bản ổn định nhất)
    img_data = st.camera_input("BẬT CAMERA ĐỂ BẮT ĐẦU STREAM", label_visibility="visible")

    if img_data:
        # Chuyển đổi và lưu ảnh tốc độ cao
        img = Image.open(img_data)
        img.save(f"{STORAGE}/{cam_name}.jpg", "JPEG", quality=40)
        
        st.markdown("<span class='rec-label'>● RECORDING VIDEO</span>", unsafe_allow_html=True)

        # SCRIPT TỰ ĐỘNG RE-CAPTURE (Tốc độ Video: 200ms)
        # Bấm chụp liên tục để tạo luồng Video 5-10 FPS
        st.components.v1.html(
            """
            <script>
            function startVideo() {
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.innerText.includes("Take Photo") || btn.innerText.includes("Chụp ảnh")) {
                        btn.click();
                        break;
                    }
                }
            }
            // Tốc độ cực nhanh để tạo cảm giác Video (200ms)
            setTimeout(startVideo, 200); 
            </script>
            """,
            height=0,
        )

# --- MÁY CHỦ (HIỂN THỊ VIDEO) ---
else:
    st.markdown("<h1>🖥️ TRUNG TÂM GIÁM SÁT VIDEO</h1>", unsafe_allow_html=True)
    
    refresh_rate = st.sidebar.slider("Độ mượt của Video", 0.05, 1.0, 0.1)
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            files = [f for f in os.listdir(STORAGE) if f.endswith(".jpg")]
            
            if not files:
                st.warning("📡 Đang tìm kiếm luồng video...")
            else:
                cols = st.columns(2)
                for idx, f_name in enumerate(files):
                    f_path = os.path.join(STORAGE, f_name)
                    
                    # Kiểm tra camera còn sống (trong 3 giây)
                    online = (time.time() - os.path.getmtime(f_path)) < 3
                    
                    with cols[idx % 2]:
                        st.markdown(f"**{f_name.replace('.jpg','')}** {'🔴 LIVE' if online else '⚪ OFFLINE'}")
                        if online:
                            # Hiển thị ảnh như một luồng Video
                            st.image(f_path, use_container_width=True)
                        else:
                            st.error("Mất kết nối video")
        
        time.sleep(refresh_rate)

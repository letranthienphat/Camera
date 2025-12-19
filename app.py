import streamlit as st
import cv2
import os
import time

# --- CẤU HÌNH GIAO DIỆN KHÔNG THỂ BỊ MẤT CỘT ---
st.set_page_config(page_title="Hệ thống Video 24/7", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ff00; }
    /* Cố định khu vực điều khiển */
    .control-panel {
        background: #111;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00ff00;
        margin-bottom: 20px;
    }
    .video-screen {
        border: 5px solid #222;
        border-radius: 15px;
        background: #000;
    }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- KHÓA BẢO MẬT ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("PASSWORD:", type="password")
    if pwd == "1111":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- GIAO DIỆN CHÍNH (KHÔNG DÙNG SIDEBAR ĐỂ TRÁNH MẤT CỘT) ---
st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
col_menu1, col_menu2 = st.columns(2)
with col_menu1:
    mode = st.radio("VAI TRÒ THIẾT BỊ:", ["🎥 MÁY QUAY (PHÁT)", "🖥️ MÁY CHỦ (XEM)"], horizontal=True)
with col_menu2:
    st.markdown(f"<p style='text-align:right;'>Hệ thống: <b>ONLINE</b><br>User: <b>Admin</b></p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- CHẾ ĐỘ MÁY QUAY VIDEO THỰC ---
if mode == "🎥 MÁY QUAY (PHÁT)":
    st.write("### 📸 LUỒNG VIDEO TRỰC TIẾP")
    
    # Sử dụng frame nén buffer để tạo luồng video
    ctx = st.camera_input("KÍCH HOẠT CAMERA") # Chỉ cần nhấn 1 lần duy nhất để cấp quyền

    if ctx:
        # Chuyển đổi sang định dạng video stream
        st.write("🔴 ĐANG QUAY VIDEO...")
        
        # Lưu vào file tạm thời dạng binary stream
        with open("stream_buffer.bin", "wb") as f:
            f.write(ctx.getbuffer())
        
        # SCRIPT TỰ ĐỘNG TRIGGER (Không cần người dùng bấm lại)
        st.components.v1.html(
            """
            <script>
            function autoVideo() {
                var btn = window.parent.document.querySelector('button[title="Take Photo"]');
                if(btn) { btn.click(); }
            }
            setInterval(autoVideo, 100); // Tốc độ cực cao để tạo video mượt
            </script>
            """,
            height=0
        )

# --- CHẾ ĐỘ MÁY CHỦ XEM VIDEO ---
else:
    st.write("### 🖥️ MÀN HÌNH THEO DÕI")
    placeholder = st.empty()
    
    while True:
        if os.path.exists("stream_buffer.bin"):
            with placeholder.container():
                st.markdown("<div class='video-screen'>", unsafe_allow_html=True)
                st.image("stream_buffer.bin", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        time.sleep(0.1) # Tốc độ xem 10 khung hình/giây

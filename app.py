import streamlit as st
import os
import time
import base64
from PIL import Image
from io import BytesIO

# --- CẤU HÌNH GIAO DIỆN DARK MODE ---
st.set_page_config(page_title="Hệ thống Camera AI", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-image: radial-gradient(circle, #1a1c24, #0e1117); }
    h1 { color: #00ffcc !important; text-shadow: 2px 2px 4px #000; }
    .stButton>button { width: 100%; border-radius: 20px; background: #00ffcc; color: black; font-weight: bold; }
    .status-live { color: #ff0000; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

STORAGE = "cctv_storage"
if not os.path.exists(STORAGE): os.makedirs(STORAGE)

# --- BẢO MẬT ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🛡️ SECURITY ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Mật khẩu hệ thống:", type="password", help="Nhập 1111")
        if st.button("XÁC NHẬN"):
            if pwd == "1111":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Mật khẩu không chính xác")
    st.stop()

# --- GIAO DIỆN ĐIỀU KHIỂN ---
role = st.sidebar.selectbox("VAI TRÒ THIẾT BỊ", ["🖥️ Trung tâm giám sát", "📷 Camera máy khách"])

# --- MÁY QUAY (TỰ ĐỘNG HOÀN TOÀN) ---
if role == "📷 Camera máy khách":
    st.markdown("<h1>📷 STATION: ONLINE</h1>", unsafe_allow_html=True)
    cam_name = st.text_input("🏷️ Tên Camera:", "CAM-01")
    
    # Khu vực camera ẩn
    img_data = st.camera_input("BẬT CAMERA (Hệ thống sẽ tự động quay ngầm)")

    if img_data:
        # Lưu ảnh
        img = Image.open(img_data)
        img.save(f"{STORAGE}/{cam_name}.jpg", quality=40)
        
        st.markdown(f"Đang truyền dữ liệu... <span class='status-live'>● LIVE</span>", unsafe_allow_html=True)

        # MÃ TỰ ĐỘNG QUAY (Tự động bấm nút sau 0.5 giây)
        # Đây là kỹ thuật 'Loop Injection' để giả lập quay video
        st.components.v1.html(
            """
            <script>
            function autoCapture() {
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.innerText.includes("Take Photo") || btn.innerText.includes("Chụp ảnh")) {
                        btn.click();
                    }
                });
            }
            // Tốc độ 800ms giúp giả lập video mà không treo máy cũ
            setTimeout(autoCapture, 800); 
            </script>
            """,
            height=0,
        )

# --- MÁY CHỦ (GIAO DIỆN ĐẸP) ---
else:
    st.markdown("<h1>🖥️ MONITOR CENTER</h1>", unsafe_allow_html=True)
    
    # Sidebar cài đặt
    grid_size = st.sidebar.slider("Số cột hiển thị", 1, 4, 2)
    refresh_speed = st.sidebar.slider("Độ trễ cập nhật (s)", 0.3, 2.0, 0.5)
    
    if st.sidebar.button("🗑️ Dọn dẹp bộ nhớ"):
        for f in os.listdir(STORAGE): os.remove(os.path.join(STORAGE, f))
        st.rerun()

    placeholder = st.empty()

    while True:
        with placeholder.container():
            files = [f for f in os.listdir(STORAGE) if f.endswith(".jpg")]
            
            if not files:
                st.info("🔌 Đang chờ kết nối từ các thiết bị ngoại vi...")
            else:
                cols = st.columns(grid_size)
                for idx, f_name in enumerate(files):
                    f_path = os.path.join(STORAGE, f_name)
                    
                    # Kiểm tra trạng thái camera (quá 10s là offline)
                    is_active = (time.time() - os.path.getmtime(f_path)) < 10
                    
                    with cols[idx % grid_size]:
                        st.markdown(f"**📍 {f_name.replace('.jpg','')}** " + 
                                    ("<span class='status-live'>● LIVE</span>" if is_active else "⚪ OFFLINE"), 
                                    unsafe_allow_html=True)
                        try:
                            # Đọc ảnh và hiển thị
                            st.image(f_path, use_container_width=True)
                        except: pass
        
        time.sleep(refresh_speed)

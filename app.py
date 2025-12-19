import streamlit as st
import os
import time
import base64
from PIL import Image
from io import BytesIO

# --- CẤU HÌNH ---
ST_DIR = "cctv_storage"
if not os.path.exists(ST_DIR):
    os.makedirs(ST_DIR)

st.set_page_config(page_title="CCTV Anti-Block", layout="wide")

# Mật khẩu bảo mật
if 'access' not in st.session_state:
    st.session_state.access = False

if not st.session_state.access:
    with st.container():
        pwd = st.text_input("Mật khẩu hệ thống:", type="password")
        if pwd == "1111":
            st.session_state.access = True
            st.rerun()
        st.stop()

# --- GIAO DIỆN ---
menu = st.sidebar.radio("CHẾ ĐỘ", ["MÁY CHỦ (XEM)", "MÁY KHÁCH (QUAY)"])

# --- MÁY KHÁCH: TỰ ĐỘNG BƠM ẢNH ---
if menu == "MÁY KHÁCH (QUAY)":
    st.header("📷 Trạm Phát Tín Hiệu")
    cam_name = st.text_input("Tên Camera:", "Camera_01")
    
    # Widget camera siêu ổn định
    img_data = st.camera_input("Bật Camera")

    if img_data:
        # Lưu ảnh vào bộ nhớ tạm của Server
        img = Image.open(img_data)
        img.save(f"{ST_DIR}/{cam_name}.jpg", quality=60)
        
        st.success(f"Đã gửi khung hình lúc: {time.strftime('%H:%M:%S')}")
        
        # SCRIPT TỰ ĐỘNG BẤM CHỤP LIÊN TỤC (Tốc độ 1.5 giây/hình)
        # Cách này bỏ qua WebRTC, dùng chính trình duyệt để gửi ảnh
        st.components.v1.html(
            """
            <script>
            setTimeout(function() {
                // Tìm nút "Take Photo" hoặc biểu tượng chụp ảnh
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.innerText.includes("Take Photo") || btn.innerText.includes("Chụp ảnh")) {
                        btn.click();
                    }
                });
            }, 1500); 
            </script>
            """,
            height=0,
        )

# --- MÁY CHỦ: HIỂN THỊ LƯỚI ---
else:
    st.header("🖥️ Trung Tâm Giám Sát")
    
    # Tốc độ làm tươi màn hình máy chủ
    speed = st.sidebar.slider("Tốc độ làm tươi (giây)", 0.5, 5.0, 1.0)
    
    placeholder = st.empty()

    while True:
        with placeholder.container():
            files = [f for f in os.listdir(ST_DIR) if f.endswith(".jpg")]
            
            if not files:
                st.info("Đang đợi tín hiệu từ camera...")
            else:
                # Tự động chia lưới (Grid)
                num_cams = len(files)
                cols_count = 2 if num_cams >= 2 else 1
                cols = st.columns(cols_count)
                
                for idx, f_name in enumerate(files):
                    f_path = os.path.join(ST_DIR, f_name)
                    
                    # Kiểm tra xem camera còn sống không (trong vòng 10 giây)
                    if time.time() - os.path.getmtime(f_path) < 10:
                        with cols[idx % cols_count]:
                            st.image(f_path, caption=f"LIVE: {f_name}", use_container_width=True)
                    else:
                        # Nếu camera mất kết nối, hiển thị thông báo xám
                        with cols[idx % cols_count]:
                            st.error(f"Mất kết nối: {f_name}")
                            
        time.sleep(speed)
        # Không cần st.rerun() để tránh giật lag, dùng placeholder là đủ.

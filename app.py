import streamlit as st
import os
import time
import glob
from PIL import Image
import math

# Cấu hình thư mục lưu trữ tạm
STREAM_DIR = "temp_streams"
if not os.path.exists(STREAM_DIR):
    os.makedirs(STREAM_DIR)

st.set_page_config(page_title="CCTV Siêu Nhẹ", layout="wide")

# Giao diện Sidebar
st.sidebar.title("Cấu hình")
mode = st.sidebar.radio("Chọn chế độ:", ["Máy Chủ (Xem)", "Máy Khách (Quay)"])

# --- CHẾ ĐỘ MÁY KHÁCH (Dành cho Android 4.4.4 / Máy yếu) ---
if mode == "Máy Khách (Quay)":
    st.header("📷 Trạm Phát Tín Hiệu")
    client_id = st.text_input("Đặt tên Camera (ví dụ: Cam_1)", "Cam_1")
    
    st.info("Hướng dẫn: Nhấn nút bên dưới để chụp và gửi ảnh. Máy cũ nên gửi ảnh thủ công để tránh treo trình duyệt.")
    
    # Sử dụng widget camera đơn giản nhất của Streamlit
    img_file = st.camera_input("Chụp ảnh")

    if img_file:
        img = Image.open(img_file)
        # Nén ảnh để truyền nhanh hơn trên mạng yếu
        save_path = os.path.join(STREAM_DIR, f"{client_id}.jpg")
        img.save(save_path, quality=50) 
        st.success(f"Đã gửi ảnh lúc: {time.strftime('%H:%M:%S')}")

# --- CHẾ ĐỘ MÁY CHỦ (Xem trên Máy tính/Windows) ---
elif mode == "Máy Chủ (Xem)":
    st.header("🖥️ Trung Tâm Giám Sát")
    
    # Tốc độ làm tươi
    refresh = st.sidebar.slider("Tốc độ cập nhật (giây)", 1, 10, 2)
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            image_files = glob.glob(os.path.join(STREAM_DIR, "*.jpg"))
            
            if not image_files:
                st.warning("Đang chờ tín hiệu từ máy khách...")
            else:
                num_cams = len(image_files)
                cols_num = 2 if num_cams > 1 else 1
                cols = st.columns(cols_num)
                
                for idx, img_path in enumerate(image_files):
                    # Kiểm tra xem file có bị 'nguội' không (quá 1 phút không cập nhật)
                    if time.time() - os.path.getmtime(img_path) > 60:
                        continue
                        
                    with cols[idx % cols_num]:
                        st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
        
        time.sleep(refresh)
        st.rerun() # Lệnh này giúp máy chủ tự làm mới màn hìn

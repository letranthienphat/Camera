import streamlit as st
import cv2
import numpy as np
import os
import time
import glob
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av
import math

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Hệ Thống CCTV AI", layout="wide", page_icon="📹")

# Thư mục dùng để giả lập đường truyền (Lưu frame hình ảnh tạm thời)
# Lưu ý: Trên Streamlit Cloud, thư mục này là tạm thời và có thể bị reset khi deploy lại.
STREAM_DIR = "temp_streams"

if not os.path.exists(STREAM_DIR):
    os.makedirs(STREAM_DIR)

# --- PHẦN XỬ LÝ VIDEO (CLIENT) ---
class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.client_id = str(int(time.time())) # Tạo ID đơn giản dựa trên thời gian

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Xử lý ảnh (nếu cần): Ví dụ thêm timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(img, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Lưu khung hình vào folder chung để Server đọc
        # Kỹ thuật này gọi là "Frame Broadcasting" qua file system
        file_path = os.path.join(STREAM_DIR, f"cam_{self.client_id}.jpg")
        
        # Ghi đè file ảnh cũ để tiết kiệm dung lượng và cập nhật ảnh mới nhất
        cv2.imwrite(file_path, img)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- GIAO DIỆN NGƯỜI DÙNG ---

st.title("📹 Hệ Thống Giám Sát Tập Trung (CCTV)")
st.markdown("---")

# Sidebar để chọn chế độ
mode = st.sidebar.selectbox("Chọn vai trò thiết bị:", ["🖥️ Máy Chủ (Monitor)", "📷 Máy Khách (Camera)"])

# --- LOGIC MÁY KHÁCH (CAMERA) ---
if mode == "📷 Máy Khách (Camera)":
    st.header("Giao diện Camera Giám Sát")
    st.info("Đang gửi dữ liệu về máy chủ... Vui lòng giữ tab này mở.")
    
    # Thiết lập Client ID cho phiên này
    if 'client_id' not in st.session_state:
        st.session_state.client_id = str(int(time.time()))
    
    st.write(f"ID Thiết bị: {st.session_state.client_id}")

    # Khởi tạo WebRTC streamer
    ctx = webrtc_streamer(
        key="cctv-sender",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if ctx.state.playing:
        st.success("Tín hiệu đang được truyền đi ✅")
    else:
        st.warning("Vui lòng cấp quyền camera và nhấn Start để bắt đầu truyền.")

# --- LOGIC MÁY CHỦ (MONITOR) ---
elif mode == "🖥️ Máy Chủ (Monitor)":
    st.header("Trung Tâm Điều Hành")
    
    # Nút làm mới (thực tế Streamlit sẽ tự rerun, nhưng ta tạo placeholder để loop)
    placeholder = st.empty()
    
    # Slider điều chỉnh tốc độ cập nhật
    refresh_rate = st.sidebar.slider("Tốc độ cập nhật (giây)", 0.1, 2.0, 0.5)
    
    st.sidebar.markdown("---")
    st.sidebar.write("Trạng thái: Đang quét tín hiệu...")

    # Vòng lặp vô hạn để cập nhật hình ảnh (giả lập real-time)
    while True:
        # 1. Quét tất cả các file ảnh trong thư mục stream
        image_files = glob.glob(os.path.join(STREAM_DIR, "*.jpg"))
        
        # Lọc bỏ các file quá cũ (ví dụ: máy khách đã tắt quá 10 giây)
        current_time = time.time()
        active_cams = []
        
        for img_file in image_files:
            # Kiểm tra thời gian sửa đổi file
            mod_time = os.path.getmtime(img_file)
            if current_time - mod_time < 10: # Nếu ảnh được cập nhật trong 10s gần đây
                active_cams.append(img_file)
            else:
                # Xóa file rác (camera đã ngắt kết nối)
                try:
                    os.remove(img_file)
                except:
                    pass
        
        num_cams = len(active_cams)
        
        with placeholder.container():
            if num_cams == 0:
                st.warning("Chưa có Camera nào kết nối. Hãy mở tab khác và chọn chế độ 'Máy Khách'.")
            else:
                st.success(f"Đang kết nối: {num_cams} camera")
                
                # Tính toán lưới (Grid layout)
                # Nếu 1 cam -> 1 cột. 2-4 cam -> 2 cột. 5-9 cam -> 3 cột.
                cols_num = math.ceil(math.sqrt(num_cams))
                cols = st.columns(cols_num)
                
                for idx, img_path in enumerate(active_cams):
                    # Đọc ảnh
                    try:
                        image = cv2.imread(img_path)
                        # Chuyển BGR sang RGB để hiển thị đúng màu trên Streamlit
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        
                        # Hiển thị vào cột tương ứng
                        col_idx = idx % cols_num
                        with cols[col_idx]:
                            st.image(image, caption=f"Cam Source: {os.path.basename(img_path)}", use_container_width=True)
                    except Exception as e:
                        continue
        
        # Nghỉ một chút trước khi làm mới khung hình
        time.sleep(refresh_rate) 

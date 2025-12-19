import streamlit as st
import cv2
import numpy as np
import os
import time
import glob
from PIL import Image, ImageEnhance
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av

# --- CẤU HÌNH HỆ THỐNG ---
STREAM_DIR = "temp_streams"
if not os.path.exists(STREAM_DIR):
    os.makedirs(STREAM_DIR)

st.set_page_config(page_title="CCTV Pro V3.0", layout="wide", page_icon="🛡️")

# --- HÀM HỖ TRỢ ---
def check_password():
    """Hàm kiểm tra đăng nhập"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔒 HỆ THỐNG BẢO MẬT</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("Nhập mã truy cập:", type="password")
            if st.button("Đăng nhập hệ thống", use_container_width=True):
                if pwd == "1111":
                    st.session_state.authenticated = True
                    st.success("Truy cập thành công!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Mật khẩu sai. Vui lòng thử lại.")
        return False
    return True

# --- LỚP XỬ LÝ VIDEO CHO CHẾ ĐỘ HIỆN ĐẠI (WebRTC) ---
class VideoReceiver(VideoTransformerBase):
    def __init__(self):
        self.client_id = "Unknown"
        self.night_mode = False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Áp dụng bộ lọc Night Mode nếu được bật
        if self.night_mode:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) # Chuyển lại 3 kênh để vẽ màu
            cv2.putText(img, "NIGHT VISION", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Ghi timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(img, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Lưu frame ra ổ đĩa để Server đọc (Cơ chế đồng bộ hóa Hybrid)
        save_path = os.path.join(STREAM_DIR, f"{self.client_id}.jpg")
        cv2.imwrite(save_path, img)

        return img

# --- CHƯƠNG TRÌNH CHÍNH ---
if check_password():
    # MENU CÀI ĐẶT (Sidebar)
    st.sidebar.title("⚙️ Trung Tâm Kiểm Soát")
    
    # Chọn vai trò
    role = st.sidebar.selectbox("Vai trò thiết bị:", ["Chọn vai trò...", "📷 Máy Khách (Camera)", "🖥️ Máy Chủ (Monitor)"])
    
    st.sidebar.markdown("---")
    st.sidebar.header("Tùy chỉnh nâng cao")
    
    # --- LOGIC MÁY KHÁCH ---
    if role == "📷 Máy Khách (Camera)":
        st.title("📷 Thiết Bị Thu Hình")
        
        # Cài đặt máy khách
        client_name = st.sidebar.text_input("Tên thiết bị:", f"Cam_{int(time.time()) % 1000}")
        tech_mode = st.sidebar.radio("Công nghệ truyền tải:", ["🚀 Video Nâng Cao (WebRTC - Máy Mới)", "🐢 Ảnh Tiết Kiệm (HTTP - Máy Cũ)"])
        night_mode_toggle = st.sidebar.checkbox("Bật chế độ ban đêm (Night Mode)")
        
        if tech_mode == "🚀 Video Nâng Cao (WebRTC - Máy Mới)":
            st.info(f"Đang phát tín hiệu dưới tên: **{client_name}**")
            
            # Khởi tạo WebRTC
            ctx = webrtc_streamer(
                key="example",
                video_transformer_factory=VideoReceiver,
                mode=WebRtcMode.SENDRECV,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )
            
            # Truyền tham số tên và chế độ vào bộ xử lý video
            if ctx.video_transformer:
                ctx.video_transformer.client_id = client_name
                ctx.video_transformer.night_mode = night_mode_toggle

        else: # Chế độ Máy Cũ (Lite)
            st.warning("Đang chạy chế độ tương thích cho máy cấu hình thấp/cũ.")
            st.write(f"ID Camera: **{client_name}**")
            
            img_file = st.camera_input("Bật Camera")
            
            if img_file:
                img = Image.open(img_file)
                # Xử lý Night Mode giả lập cho máy cũ
                if night_mode_toggle:
                    img = img.convert('L') # Chuyển sang đen trắng
                
                save_path = os.path.join(STREAM_DIR, f"{client_name}.jpg")
                img.save(save_path)
                
                st.success(f"Đã gửi dữ liệu lúc {time.strftime('%H:%M:%S')}")
                
                # Script tự động bấm nút cho máy cũ
                st.components.v1.html(
                    """<script>setTimeout(function(){window.parent.document.querySelector('button').click();}, 1500);</script>""",
                    height=0
                )

    # --- LOGIC MÁY CHỦ ---
    elif role == "🖥️ Máy Chủ (Monitor)":
        st.title("🖥️ Trung Tâm Giám Sát An Ninh")
        
        # Cài đặt máy chủ
        refresh_rate = st.sidebar.slider("Tốc độ làm mới (giây)", 0.5, 5.0, 1.0)
        grid_cols = st.sidebar.selectbox("Giao diện lưới:", [2, 3, 4], index=0)
        
        placeholder = st.empty()
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Xóa dữ liệu cũ"):
            files = glob.glob(os.path.join(STREAM_DIR, "*"))
            for f in files: os.remove(f)
            st.toast("Đã dọn dẹp bộ nhớ đệm!")

        # Vòng lặp hiển thị
        while True:
            with placeholder.container():
                # Lấy tất cả ảnh từ thư mục (Bất kể từ WebRTC hay Lite mode)
                image_files = glob.glob(os.path.join(STREAM_DIR, "*.jpg"))
                
                # Lọc camera active (trong vòng 15 giây)
                active_cams = []
                current_time = time.time()
                
                for f in image_files:
                    try:
                        if current_time - os.path.getmtime(f) < 15:
                            active_cams.append(f)
                        else:
                            pass # Có thể thêm logic xóa file rác ở đây
                    except:
                        pass
                
                if not active_cams:
                    st.info("Đang chờ kết nối từ các Camera...")
                    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d9/Icon-round-Question_mark.svg", width=100)
                else:
                    st.write(f"🟢 Đang trực tuyến: **{len(active_cams)}** camera")
                    cols = st.columns(grid_cols)
                    
                    for idx, img_path in enumerate(active_cams):
                        # Đọc và hiển thị
                        try:
                            # Dùng PIL để đọc cho an toàn
                            image = Image.open(img_path)
                            cam_name = os.path.basename(img_path).replace(".jpg", "")
                            
                            col_idx = idx % grid_cols
                            with cols[col_idx]:
                                st.image(image, caption=f"🎥 {cam_name}", use_container_width=True)
                        except Exception as e:
                            continue
            
            time.sleep(refresh_rate)
            # st.rerun() là không cần thiết trong vòng lặp while của Streamlit nếu dùng placeholder,
            # nhưng để đảm bảo slider hoạt động mượt mà, ta để code tự loop.
            
    else:
        st.info("👈 Vui lòng chọn vai trò ở thanh bên trái để bắt đầu.")
        st.markdown("""
        ### Hướng dẫn nhanh:
        1. **Máy Khách:** Dùng điện thoại quay phim. 
           - Chọn 'Video Nâng Cao' cho iPhone/Android đời mới.
           - Chọn 'Ảnh Tiết Kiệm' cho máy đời cũ.
        2. **Máy Chủ:** Dùng Laptop/PC để xem toàn bộ camera cùng lúc.
        """)

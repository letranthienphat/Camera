import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import os

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Video AI", layout="wide")

# CSS để giao diện hiển thị tốt trên điện thoại và làm đẹp
st.markdown("""
    <style>
    .stApp { background: #000; color: #00ffcc; }
    /* Đảm bảo menu không bị mất trên điện thoại */
    .main-menu-box {
        background: #111; padding: 20px; border: 2px solid #00ffcc;
        border-radius: 15px; margin-bottom: 20px; text-align: center;
    }
    .video-frame { border: 3px solid #00ffcc; border-radius: 10px; overflow: hidden; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BẢO MẬT 1111 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔐 ACCESS CONTROL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Mật khẩu:", type="password")
        if st.button("XÁC NHẬN"):
            if pwd == "1111":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- GIAO DIỆN CHỌN VAI TRÒ (Đưa ra màn hình chính thay vì Sidebar) ---
st.markdown("<div class='main-menu-box'>", unsafe_allow_html=True)
role = st.radio("CHỌN CHẾ ĐỘ HOẠT ĐỘNG:", ["📷 MÁY QUAY (PHÁT VIDEO)", "🖥️ MÁY CHỦ (XEM VIDEO)"], horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

# Cấu hình STUN để thông mạng (Fix lỗi kết nối)
RTC_CONFIG = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# --- MÁY QUAY VIDEO THỰC THỤ ---
if "📷 MÁY QUAY" in role:
    st.subheader("🎥 ĐANG LÀM MÁY PHÁT VIDEO")
    
    # Đây là máy quay video thực, không phải chụp ảnh
    webrtc_streamer(
        key="streamer",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    st.info("Bấm 'Start' để bắt đầu quay Video trực tiếp.")

# --- MÁY CHỦ XEM VIDEO ---
else:
    st.subheader("🖥️ TRUNG TÂM GIÁM SÁT VIDEO")
    
    # Nhận video từ máy quay
    webrtc_streamer(
        key="streamer",
        mode=WebRtcMode.RECVONLY,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    st.success("Đang chờ nhận luồng video từ máy khách...")

# --- PHẦN CÀI ĐẶT NÂNG CAO (Thêm vào cuối trang) ---
with st.expander("🛠️ CÀI ĐẶT HỆ THỐNG"):
    st.write("Phiên bản: V11.0 (True Video)")
    st.checkbox("Bật chế độ tiết kiệm băng thông")
    st.color_picker("Màu chủ đạo giao diện", "#00ffcc")
    st.slider("Độ phân giải video tối đa", 360, 1080, 720)

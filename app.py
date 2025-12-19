import streamlit as st
import os
import time
from PIL import Image

# --- CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP ---
st.set_page_config(page_title="Hệ thống Giám sát AI", layout="wide")

st.markdown("""
    <style>
    /* Tổng thể giao diện Dark Mode */
    .stApp { background: #0a0a0a; color: #00ffcc; }
    
    /* Header chuyên nghiệp */
    .main-header { 
        padding: 20px; 
        border-bottom: 2px solid #00ffcc; 
        text-align: center; 
        background: rgba(0, 255, 204, 0.05);
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.2);
    }
    
    /* Khung Camera */
    .cam-card {
        border: 1px solid #333;
        border-radius: 10px;
        padding: 5px;
        background: #111;
        transition: all 0.3s;
    }
    .cam-card:hover { border-color: #00ffcc; box-shadow: 0 0 10px #00ffcc; }

    /* Hiệu ứng nhấp nháy REC */
    .rec-icon {
        color: #ff0000;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    @keyframes blink { 50% { opacity: 0; } }

    /* Giấu toàn bộ nút bấm dư thừa để giao diện sạch */
    button[title="Take Photo"] { display: none !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

STORAGE = "cctv_storage"
if not os.path.exists(STORAGE): os.makedirs(STORAGE)

# --- BẢO MẬT ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='main-header'><h1>🔐 HỆ THỐNG ĐƯỢC BẢO VỆ</h1></div>", unsafe_allow_html=True)
    pwd = st.text_input("Mật khẩu truy cập (1111):", type="password")
    if pwd == "1111":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- MENU CHỌN CHẾ ĐỘ ---
mode = st.sidebar.selectbox("CHỨC NĂNG", ["🖥️ MÀN HÌNH TRUNG TÂM", "🎥 CHẾ ĐỘ QUAY VIDEO"])

# --- MÁY QUAY (TỰ ĐỘNG QUAY KHÔNG CẦN BẤM) ---
if mode == "🎥 CHẾ ĐỘ QUAY VIDEO":
    st.markdown("<div class='main-header'><h1>🎥 LIVE STREAMING STATION</h1></div>", unsafe_allow_html=True)
    cam_name = st.text_input("ĐẶT TÊN CAMERA:", "CAM_01")
    
    # Ẩn hướng dẫn, hiển thị trạng thái
    st.markdown("### <span class='rec-icon'>● REC</span> ĐANG QUAY VÀ TRUYỀN DỮ LIỆU TỰ ĐỘNG", unsafe_allow_html=True)

    # Widget Camera
    img_data = st.camera_input("Bật Camera")

    if img_data:
        img = Image.open(img_data)
        img.save(f"{STORAGE}/{cam_name}.jpg", quality=50)
        
        # SCRIPT THÔNG MINH: Tự động nhấn nút chụp liên tục không ngừng
        st.components.v1.html(
            """
            <script>
            function forceCapture() {
                // Tìm tất cả các button trong trang web của Streamlit
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {
                    // Tự động tìm nút Chụp ảnh dựa trên văn bản hoặc thuộc tính
                    if (btn.innerText.includes("Take Photo") || btn.innerText.includes("Chụp ảnh")) {
                        btn.click();
                        break;
                    }
                }
            }
            // Tốc độ cực cao: 500ms (Xấp xỉ tốc độ quay video)
            setTimeout(forceCapture, 500);
            </script>
            """,
            height=0,
        )

# --- MÁY CHỦ (GIAO DIỆN CHUYÊN NGHIỆP) ---
else:
    st.markdown("<div class='main-header'><h1>🖥️ NETWORK MONITORING SYSTEM</h1></div>", unsafe_allow_html=True)
    
    # Sidebar điều khiển
    grid = st.sidebar.slider("Bố cục màn hình (Số cột)", 1, 4, 2)
    speed = st.sidebar.slider("Tốc độ quét tín hiệu (giây)", 0.1, 2.0, 0.5)
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            files = [f for f in os.listdir(STORAGE) if f.endswith(".jpg")]
            
            if not files:
                st.info("📡 Đang tìm kiếm tín hiệu camera trong mạng...")
            else:
                cols = st.columns(grid)
                for idx, f_name in enumerate(files):
                    f_path = os.path.join(STORAGE, f_name)
                    
                    # Kiểm tra xem camera còn sống không (trong 5 giây gần nhất)
                    online = (time.time() - os.path.getmtime(f_path)) < 5
                    
                    with cols[idx % grid]:
                        st.markdown(f"""
                            <div class='cam-card'>
                                <p style='margin:0;'>{'🟢' if online else '🔴'} <b>{f_name.replace('.jpg','')}</b></p>
                                <p style='font-size:10px; margin:0;'>Tình trạng: {'LIVE STREAMING' if online else 'DISCONNECTED'}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        try:
                            st.image(f_path, use_container_width=True)
                        except: pass
                        
        time.sleep(speed)

import streamlit as st
import os
import time
from PIL import Image

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI Surveillance Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050505; color: #00ff00; }
    .camera-box { border: 2px solid #00ff00; border-radius: 15px; padding: 10px; background: #000; }
    .status-bar { padding: 10px; border-radius: 10px; background: #111; border-left: 5px solid #ff0000; margin-bottom: 20px; }
    /* Giấu nút chụp mặc định của Streamlit để giao diện sạch hơn */
    button[title="Take Photo"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

STORAGE = "cctv_storage"
if not os.path.exists(STORAGE): os.makedirs(STORAGE)

# --- KHÓA BẢO MẬT ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.sidebar.text_input("🔑 ACCESS CODE:", type="password")
    if pwd == "1111":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- ĐIỀU HƯỚNG ---
role = st.sidebar.radio("HỆ THỐNG", ["🖥️ GIÁM SÁT", "📷 CAMERA"])

if role == "📷 CAMERA":
    st.markdown("<div class='status-bar'>📡 TRẠM PHÁT ĐANG CHỜ KÍCH HOẠT...</div>", unsafe_allow_html=True)
    cam_name = st.text_input("Tên máy:", "ZONE-01")
    
    # Hướng dẫn thông minh
    st.info("💡 CHỈ CẦN CHẠM VÀO MÀN HÌNH ĐỂ BẮT ĐẦU QUAY TỰ ĐỘNG")

    img_data = st.camera_input("KÍCH HOẠT SENSOR")

    if img_data:
        # Lưu ảnh chất lượng nén để mượt hơn
        img = Image.open(img_data)
        img.save(f"{STORAGE}/{cam_name}.jpg", quality=35)
        
        st.markdown(f"🟢 **{cam_name}** đang truyền tín hiệu...")

        # --- CƠ CHẾ THÔNG MINH: AUTO-INJECTOR V2 ---
        # Tự động tìm nút chụp và bấm liên tục sau khi người dùng kích hoạt 1 lần
        st.components.v1.html(
            """
            <script>
            function startCCTV() {
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.innerText.includes("Take Photo") || btn.innerText.includes("Chụp ảnh")) {
                        btn.click();
                        break;
                    }
                }
            }
            // Tốc độ cao: 600ms (Gần như video)
            setTimeout(startCCTV, 600);
            </script>
            """,
            height=0,
        )

else:
    st.markdown("<h1>🖥️ CONTROL CENTER</h1>", unsafe_allow_html=True)
    refresh = st.sidebar.slider("Tốc độ quét (s)", 0.2, 2.0, 0.5)
    
    placeholder = st.empty()
    while True:
        with placeholder.container():
            files = [f for f in os.listdir(STORAGE) if f.endswith(".jpg")]
            if not files:
                st.write("🔦 Đang tìm kiếm tín hiệu...")
            else:
                cols = st.columns(3)
                for idx, f in enumerate(files):
                    f_path = os.path.join(STORAGE, f)
                    # Kiểm tra xem cam còn online không
                    active = (time.time() - os.path.getmtime(f_path)) < 5
                    with cols[idx % 3]:
                        st.markdown(f"{'🟢' if active else '🔴'} **{f.replace('.jpg','')}**")
                        st.image(f_path, use_container_width=True)
        time.sleep(refresh)

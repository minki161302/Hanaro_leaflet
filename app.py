import streamlit as st
from PIL import Image
import glob
import base64
from io import BytesIO

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Mobile Leaflet")

# 2. 이미지 Base64 변환 함수
def get_b64(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# 3. 이미지 처리 (캐싱 적용)
@st.cache_data
def load_data():
    c_path = next((f for f in glob.glob("*") if "표지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    i_path = next((f for f in glob.glob("*") if "내지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    
    if not c_path or not i_path:
        return None

    cover = Image.open(c_path)
    inner = Image.open(i_path)
    w, h = cover.size
    
    # 분할 및 변환
    return {
        "f": get_b64(cover.crop((w // 2, 0, w, h))), # 앞표지
        "i": get_b64(inner),                         # 내지
        "b": get_b64(cover.crop((0, 0, w // 2, h)))  # 뒤표지
    }

data = load_data()

if data:
    # 스타일과 HTML을 분리하지 않고 한 번에 주입 (문법 오류 방지)
    content = f"""
    <style>
        .main .block-container {{ padding: 0 !important; }}
        header, footer, #MainMenu {{ visibility: hidden; }}
        body {{ background-color: #0e1117; margin: 0; }}
        
        .v-stack {{ width: 100vw; display: flex; flex-direction: column; }}
        .item {{ width: 100vw; display: flex; justify-content: center; overflow: hidden; }}
        .cover {{ height: 100vh; }}
        .inner {{ height: auto; overflow-x: auto; display: block; -webkit-overflow-scrolling: touch; }}
        
        img {{ display: block; }}
        .cover img {{ height: 100%; width: 100%; object-fit: contain; }}
        .inner img {{ width: auto; height: 85vh; }}

        @keyframes b {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-20px); }}
            60% {{ transform: translateY(-10px); }}
        }}
        .bounce {{ animation: b 1.2s ease; }}
    </style>

    <div class="v-stack">
        <div class="item cover bounce"><img src="data:image/png;base64,{data['f']}"></div>
        <div class="item inner"><img src="data:image/png;base64,{data['i']}"></div>
        <div class="item cover"><img src="data:image/png;base64,{data['b']}"></div>
    </div>

    <script>
        setTimeout(() => {{
            window.scrollTo({{ top: 50, behavior: 'smooth' }});
            setTimeout(() => {{ window.scrollTo({{ top: 0, behavior: 'smooth' }}); }}, 400);
        }}, 800);
    </script>
    """
    st.markdown(content, unsafe_allow_html=True)
else:
    st.error("파일명을 확인하세요: '표지', '내지' 포함 필수")

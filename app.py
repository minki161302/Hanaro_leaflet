import streamlit as st
from PIL import Image
import os
import glob
import base64
from io import BytesIO

# --- 1. 배포 환경 설정 ---
st.set_page_config(layout="wide", page_title="Mobile Vertical Viewer")

# 이 함수는 캐싱하지 않습니다 (이미지 객체는 해시가 불가능하기 때문)
def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# 이미지를 처리하는 큰 단위의 함수만 캐싱합니다.
@st.cache_data
def process_images():
    cover_path = next((f for f in glob.glob("*") if "표지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    inner_path = next((f for f in glob.glob("*") if "내지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    
    if not cover_path or not inner_path:
        return None

    cover = Image.open(cover_path)
    inner = Image.open(inner_path)
    w, h = cover.size
    
    # 표지 분할 (오른쪽 절반: 앞표지, 왼쪽 절반: 뒤표지)
    back_img = cover.crop((0, 0, w // 2, h))
    front_img = cover.crop((w // 2, 0, w, h))
    
    # 결과물을 미리 Base64 문자열로 변환하여 딕셔너리로 저장 (문자열은 캐싱이 잘 됩니다)
    return {
        "front": get_image_base64(front_img),
        "inner": get_image_base64(inner),
        "back": get_image_base64(back_img)
    }

# --- 2. 메인 로직 ---
imgs = process_images()

if imgs:
    st.markdown(f"""
        <style>
        .main .block-container {{ padding: 0; max-width: 100vw; }}
        header, footer, #MainMenu {{ visibility: hidden; }}
        
        .vertical-viewer {{
            width: 100vw;
            background-color: #0e1117;
        }}

        .section {{
            width: 100vw;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}

        .cover-section {{
            height: 100vh;
        }}
        
        .inner-section {{
            height: auto;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            display: block;
        }}

        .section img {{
            display: block;
        }}

        .cover-section img {{
            height: 100%;
            width: 100%;
            object-fit: contain;
        }}

        .inner-section img {{
            width: auto;
            height: 85vh; 
        }}

        @keyframes bounce-down {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-30px); }}
            60% {{ transform: translateY(-15px); }}
        }}
        .bounce {{
            animation: bounce-down 1.2s ease;
        }}
        </style>

        <div class="vertical-viewer">
            <div class="section cover-section bounce">
                <img src="data:image/png;base64,{imgs['front']}">
            </div>
            
            <div class="section inner-section">
                <img src="data:image/png;base64,{imgs['inner']}">
            </div>
            
            <div class="section cover-section">
                <img src="data:image/png;base64,{imgs['back']}">
            </div>
        </div>

        <script>
        setTimeout(() => {{
            window.scrollTo({{ top: 70, behavior: 'smooth' }});
            setTimeout(() => {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }}, 500);
        }}, 1000);
        </script>
    """, unsafe_allow_html=True)
else:
    st.error("이미지를 찾을 수 없습니다. 파일명을 확인해주세요.")

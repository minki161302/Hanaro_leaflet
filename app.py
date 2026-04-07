import streamlit as st
from PIL import Image
import os
import glob
import base64
from io import BytesIO

# --- 1. 배포 환경 설정 ---
st.set_page_config(layout="wide", page_title="Mobile Vertical Viewer")

@st.cache_data
def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@st.cache_data
def process_images():
    cover_path = next((f for f in glob.glob("*") if "표지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    inner_path = next((f for f in glob.glob("*") if "내지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    
    if not cover_path or not inner_path:
        return None

    cover = Image.open(cover_path)
    inner = Image.open(inner_path)
    w, h = cover.size
    
    # 표지 분할 (반으로 갈라 앞/뒤 생성)
    back_img = cover.crop((0, 0, w // 2, h))
    front_img = cover.crop((w // 2, 0, w, h))
    
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
        /* 기본 여백 및 헤더 제거 */
        .main .block-container {{ padding: 0; max-width: 100vw; }}
        header, footer, #MainMenu {{ visibility: hidden; }}
        
        /* 전체 세로 컨테이너 */
        .vertical-viewer {{
            width: 100vw;
            background-color: #0e1117;
        }}

        /* 각 섹션 설정 */
        .section {{
            width: 100vw;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}

        /* 앞표지 & 뒤표지: 화면 높이에 꽉 차게 */
        .cover-section {{
            height: 100vh;
        }}
        
        /* 내지: 가로로 튀어나오는 부분 처리 */
        .inner-section {{
            height: auto;
            overflow-x: auto; /* 가로 스크롤 허용 */
            -webkit-overflow-scrolling: touch;
            display: block; /* 가로 스크롤을 위해 블록화 */
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
            width: auto; /* 가로 길이는 원본 비율 유지 */
            height: 80vh; /* 내지는 화면 높이의 80% 정도로 설정 (가로로 긴 것 강조) */
        }

        /* 아래로 튕기는 애니메이션 */
        @keyframes bounce-down {{
            0%, 20%, 50%, 80%, 100% {{transform: translateY(0);}}
            40% {{transform: translateY(-30px);}}
            60% {{transform: translateY(-15px);}}
        }}
        .bounce {{
            animation: bounce-down 1.5s ease;
        }}
        </style>

        <div class="vertical-viewer" id="main-content">
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
        // 최초 진입 시 아래에 내용이 더 있음을 알리기 위해 살짝 아래로 튕기기
        window.scrollTo({{
            top: 50,
            behavior: 'smooth'
        }});
        setTimeout(() => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }}, 600);
        </script>
    """, unsafe_allow_html=True)
else:
    st.error("파일을 찾을 수 없습니다.")

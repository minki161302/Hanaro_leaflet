import streamlit as st
from PIL import Image
import os
import glob
import base64
from io import BytesIO

# --- 1. 배포 환경 설정 ---
st.set_page_config(layout="wide", page_title="Mobile Booklet Viewer")

# 이미지를 HTML에 직접 박기 위해 Base64로 변환 (배포 시 경로 문제 해결)
def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@st.cache_data
def process_images():
    # 확장자 무관하게 '표지', '내지' 키워드 파일 탐색
    cover_path = next((f for f in glob.glob("*") if "표지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    inner_path = next((f for f in glob.glob("*") if "내지" in f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
    
    if not cover_path or not inner_path:
        return None

    # 이미지 처리 (Pillow)
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
    # CSS 및 뷰어 구현
    st.markdown(f"""
        <style>
        /* 배포 시 상단바 및 여백 완전 제거 */
        .main .block-container {{ padding: 0; max-width: 100vw; }}
        header, footer, #MainMenu {{ visibility: hidden; }}
        
        .viewer-container {{
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            -webkit-overflow-scrolling: touch;
            width: 100vw;
            height: 100vh;
            background-color: #0e1117;
            scrollbar-width: none; /* 파이어폭스 */
        }}
        .viewer-container::-webkit-scrollbar {{ display: none; }} /* 크롬, 사파리 */

        .page {{
            flex-shrink: 0;
            scroll-snap-align: start;
            height: 100vh;
            display: flex;
            align-items: center;
        }}

        .cover-page {{ width: 100vw; justify-content: center; }}
        .inner-page {{ width: auto; }} 

        .page img {{
            height: 100%;
            max-width: none;
            object-fit: contain;
            display: block;
        }}

        /* 안내 문구 */
        .scroll-guide {{
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255,255,255,0.15);
            color: white;
            padding: 10px 24px;
            border-radius: 30px;
            backdrop-filter: blur(10px);
            font-size: 14px;
            z-index: 100;
            pointer-events: none;
            animation: fadeOut 1s forwards 4s;
        }}
        @keyframes fadeOut {{ from {{opacity: 1;}} to {{opacity: 0;}} }}
        </style>

        <div class="viewer-container" id="viewer">
            <div class="page cover-page"><img src="data:image/png;base64,{imgs['front']}"></div>
            <div class="page inner-page"><img src="data:image/png;base64,{imgs['inner']}"></div>
            <div class="page cover-page"><img src="data:image/png;base64,{imgs['back']}"></div>
        </div>

        <div class="scroll-guide">옆으로 넘겨서 보세요 ↔</div>

        <script>
        const viewer = document.getElementById('viewer');
        
        // 1. 최초 진입 시 아래/옆으로 살짝 튕기는 Bounce 효과
        setTimeout(() => {{
            viewer.scrollTo({{ left: 100, behavior: 'smooth' }});
            setTimeout(() => {{
                viewer.scrollTo({{ left: 0, behavior: 'smooth' }});
            }}, 500);
        }}, 1000);
        </script>
    """, unsafe_allow_html=True)
else:
    st.error("이미지 파일을 찾을 수 없습니다. 파일명에 '표지', '내지'가 포함되어 있는지 확인해주세요.")
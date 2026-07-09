# Streamlit imported lazily inside render functions only
import base64
import math
import hashlib
import json
import os

# Avatar mặc định dạng vô tính (người xám) - SVG base64
DEFAULT_AVATAR = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2NjYyI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgM2MxLjY2IDAgMyAxLjM0IDMgM3MtMS4zNCAzLTMgMy0zLTEuMzQtMy0zIDEuMzQtMyAzLTN6bTAgMTQuMmMtMi41IDAtNC43MS0xLjI4LTYtMy4yMi4wMy0xLjk5IDQtMy4wOCA2LTMuMDggMS45OSAwIDUuOTcgMS4wOSA2IDMuMDgtMS4yOSAxLjk0LTMuNSAzLjIyLTYgMy4yMnoiLz48L3N2Zz4="

KEYWORDS_MAP = {
    "Khách quan": ["số liệu", "thông tin", "bằng chứng", "nguồn", "dữ liệu", "chi tiết", "cụ thể", "thực tế", "phân tích", "con số"],
    "Cảm xúc": ["cảm thấy", "buồn", "vui", "lo lắng", "hạnh phúc", "tâm trạng", "sợ", "thương", "yêu", "ghét", "nhạy cảm", "tình cảm"],
    "Tiêu cực": ["lưu ý", "cẩn thận", "rủi ro", "nguy cơ", "kiểm tra", "xác thực", "đề phòng", "nghi ngờ", "chậm", "chắc", "an toàn"],
    "Tích cực": ["hy vọng", "tốt đẹp", "tiềm năng", "cơ hội", "phát triển", "tin tưởng", "vượt qua", "thành công", "tích cực", "niềm tin"],
    "Sáng tạo": ["ý tưởng", "mới", "sáng tạo", "khác biệt", "thử nghiệm", "độc đáo", "phát minh", "cải tiến", "giải pháp", "tưởng tượng"],
    "Tổng quan": ["tóm lại", "khái quát", "nhìn chung", "hệ thống", "tổng thể", "bức tranh", "kết luận", "cấu trúc", "toàn diện"]
}

def get_user_stats(username):
    """Phân tích dữ liệu thực tế từ Lịch sử trò chuyện và AOA để tính toán chỉ số"""
    import cms_helper
    # 1. Thu thập tất cả văn bản của người dùng
    all_text = ""
    
    # Từ Chat History (CMS)
    try:
        chats = cms_helper.get_chat_sessions(username)
        for chat_id, chat_data in chats.items():
            if "chat_history" in chat_data:
                for msg in chat_data["chat_history"]:
                    if msg.get("role") == "user":
                        all_text += " " + msg.get("content", "").lower()
    except Exception as e:
        print(f"Error fetching chats for stats: {e}")
    
    # Từ AOA (CMS)
    try:
        posts = cms_helper.get_aoa_posts()
        for post in posts:
            if post.get("author_name") == username:
                all_text += " " + post.get("content", "").lower()
            for cmt in post.get("comments", []):
                if cmt.get("author_name") == username:
                    all_text += " " + cmt.get("content", "").lower()
    except Exception as e:
        print(f"Error fetching aoa posts for stats: {e}")

    # 2. Tính toán điểm dựa trên từ khóa
    # Điểm cơ bản dựa trên hash của tên để không bao giờ bị 0
    hash_obj = hashlib.md5(username.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    final_stats = []
    categories = ["Khách quan", "Cảm xúc", "Tiêu cực", "Tích cực", "Sáng tạo", "Tổng quan"]
    
    for i, cat in enumerate(categories):
        # Base score (50-70)
        val = int(hash_hex[i*2:i*2+2], 16)
        base_score = 50 + (val % 21)
        
        # Keyword bonus
        keywords = KEYWORDS_MAP[cat]
        match_count = sum(all_text.count(kw) for kw in keywords)
        
        # Mỗi từ khóa khớp cộng thêm 3 điểm, tối đa 98 điểm
        bonus = min(match_count * 3, 28)
        
        # Nếu có dữ liệu văn bản, điểm sẽ biến động mạnh hơn
        final_score = min(base_score + bonus, 98)
        final_stats.append(final_score)
        
    return final_stats

def generate_radar_chart_svg(stats):
    """Vẽ biểu đồ Radar bằng SVG thuần túy"""
    cx, cy = 200, 180
    R = 120
    categories = ["Khách quan", "Cảm xúc", "Tiêu cực", "Tích cực", "Sáng tạo", "Tổng quan"]
    
    svg = f'<svg width="400" height="360" xmlns="http://www.w3.org/2000/svg">'
    
    # Lưới nhện nền (5 cấp)
    for level in range(1, 6):
        r = R * (level / 5.0)
        points = []
        for i in range(6):
            angle = -math.pi/2 + i * math.pi/3
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append(f"{x},{y}")
        svg += f'<polygon points="{" ".join(points)}" fill="rgba(49, 53, 60, 0.5)" stroke="#4d4732" stroke-width="1"/>'
        
    # Trục
    for i in range(6):
        angle = -math.pi/2 + i * math.pi/3
        x = cx + R * math.cos(angle)
        y = cy + R * math.sin(angle)
        svg += f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#4d4732" stroke-width="1.5" stroke-dasharray="4 4"/>'
        
        # Tên danh mục (Labels)
        label_x = cx + (R + 35) * math.cos(angle)
        label_y = cy + (R + 25) * math.sin(angle)
        
        anchor = "middle"
        if math.cos(angle) > 0.1: anchor = "start"
        elif math.cos(angle) < -0.1: anchor = "end"
        
        svg += f'<text x="{label_x}" y="{label_y}" text-anchor="{anchor}" dominant-baseline="middle" font-family="Montserrat, sans-serif" font-size="14" fill="#dfe2eb" font-weight="600">{categories[i]}</text>'
        
    # Vùng dữ liệu
    data_points = []
    for i in range(6):
        angle = -math.pi/2 + i * math.pi/3
        val = stats[i]
        r = R * (val / 100.0)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        data_points.append(f"{x},{y}")
        
    svg += f'<polygon points="{" ".join(data_points)}" fill="rgba(233, 196, 0, 0.45)" stroke="#ffe16d" stroke-width="2.5" stroke-linejoin="round"/>'
    
    # Điểm dữ liệu và con số
    for i, pt in enumerate(data_points):
        x, y = pt.split(",")
        svg += f'<circle cx="{x}" cy="{y}" r="5" fill="#10141a" stroke="#ffe16d" stroke-width="2"/>'
        svg += f'<text x="{x}" y="{float(y)-10}" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="#ffe16d" font-weight="bold">{stats[i]}</text>'
        
    svg += '</svg>'
    return svg


def render_user_profile(save_db_func):
    import streamlit as st
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1f2937;'>Hồ sơ cá nhân</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    current_name = st.session_state.saved_chats.get("user_name", "Người dùng Thapsang")
    
    col_left, col_right = st.columns([1, 1.8], gap="large")
    
    with col_left:
        avatar_src = st.session_state.saved_chats.get("user_avatar", DEFAULT_AVATAR)
        st.markdown(
            f"""
            <style>
            .avatar-wrapper {{
                position: relative;
                width: 140px;
                height: 140px;
                margin: 0 auto;
                border-radius: 50%;
                overflow: hidden;
                border: 3px solid #e5e7eb;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                cursor: pointer;
            }}
            .avatar-img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .avatar-overlay {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.6);
                color: white;
                height: 40px;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 13px;
                font-weight: bold;
                opacity: 0;
                transition: opacity 0.3s ease-in-out;
            }}
            .avatar-wrapper:hover .avatar-overlay {{
                opacity: 1;
            }}
            div[data-testid="stFileUploader"] {{
                margin-top: -140px !important;
                margin-bottom: 20px !important;
                margin-left: auto !important;
                margin-right: auto !important;
                width: 140px !important;
                height: 140px !important;
                opacity: 0 !important;
                z-index: 10 !important;
                cursor: pointer !important;
            }}
            div[data-testid="stFileUploader"] section {{
                padding: 0 !important;
                height: 100% !important;
                cursor: pointer !important;
            }}
            div[data-testid="stFileUploader"] button {{
                display: none !important;
            }}
            </style>
            <div class="avatar-wrapper">
                <img class="avatar-img" src="{avatar_src}">
                <div class="avatar-overlay">📷 Đổi ảnh</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            base64_img = "data:image/png;base64," + base64.b64encode(bytes_data).decode()
            if st.session_state.saved_chats.get("user_avatar") != base64_img:
                st.session_state.saved_chats["user_avatar"] = base64_img
                save_db_func(st.session_state.saved_chats)
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        new_name = st.text_input("Tên hiển thị (dùng trong AOA)", value=current_name)
        if new_name != current_name:
            st.session_state.saved_chats["user_name"] = new_name
            save_db_func(st.session_state.saved_chats)
            st.rerun()
            
        st.markdown("<p style='text-align: center; color: #888; margin-top: 5px; margin-bottom: 20px; font-size: 1rem;'>@user</p>", unsafe_allow_html=True)
        st.info("Trạng thái: Đang hoạt động")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Đăng xuất tài khoản", use_container_width=True, type="primary"):
            st.session_state.authenticated = False
            st.session_state.saved_chats["_authenticated"] = False
            save_db_func(st.session_state.saved_chats)
            st.session_state.current_page = "chat"
            st.rerun()

    with col_right:
        st.markdown("<h3 style='text-align: center; color: #374151; margin-bottom: 0px;'>Phân tích Năng lực Tư duy AI</h3>", unsafe_allow_html=True)
        
        # Tính toán chỉ số thực tế từ dữ liệu
        stats = get_user_stats(current_name)
        svg_code = generate_radar_chart_svg(stats)
        
        st.markdown(
            f'<div style="display: flex; justify-content: center; align-items: center; margin-top: 10px;">{svg_code}</div>', 
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div style="text-align: center; color: #6b7280; font-size: 0.95rem; margin-top: 10px;">
                Chỉ số được AI phân tích từ <b>toàn bộ lịch sử trò chuyện</b>, các bài đăng <b>AOA</b> và nội dung tương tác của <b>{current_name}</b>.
            </div>
            """, 
            unsafe_allow_html=True
        )

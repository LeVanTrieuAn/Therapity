# Streamlit imported lazily inside render functions only

# Dữ liệu mẫu các kỳ học
COHORTS = [
    {
        "id": 1,
        "title": "Cohort 1 — Phá vỡ những gì cũ",
        "weeks": "8 tuần",
        "status": "active",
        "start_date": "01/06/2025",
        "theme": "Niềm tin giới hạn bản thân",
        "phases": {
            "unlearn": {
                "title": "🔥 Unlearn — Phá bỏ",
                "weeks": "Tuần 1–3",
                "color": "#ef4444",
                "desc": "Nhận diện và tháo gỡ các niềm tin cũ đang kìm hãm bạn.",
                "tasks": [
                    "Viết nhật ký 'Tôi không thể...' mỗi ngày",
                    "Thực hành phiên Soi chiếu Socratic với Thapsang",
                    "Mapping bản đồ niềm tin hiện tại",
                ]
            },
            "relearn": {
                "title": "🌱 Relearn — Thiết lập",
                "weeks": "Tuần 4–6",
                "color": "#f59e0b",
                "desc": "Xây dựng framework tư duy mới và thử nghiệm các khuôn mẫu hành vi.",
                "tasks": [
                    "Đọc 1 cuốn sách được assign theo cohort",
                    "Thực hành micro-habit mới (chọn 1)",
                    "Check-in hàng tuần với AI Coach",
                ]
            },
            "execute": {
                "title": "🚀 Execute — Vận hành",
                "weeks": "Tuần 7–8",
                "color": "#10b981",
                "desc": "Áp dụng vào cuộc sống thực, đo lường và điều chỉnh.",
                "tasks": [
                    "Thực hiện 1 dự án thực chiến nhỏ",
                    "Chia sẻ kết quả với cộng đồng",
                    "Viết bài tổng kết cá nhân",
                ]
            }
        }
    },
    {
        "id": 2,
        "title": "Cohort 2 — Xây dựng Hệ thống",
        "weeks": "10 tuần",
        "status": "upcoming",
        "start_date": "01/09/2025",
        "theme": "Kỷ luật và Hệ thống cá nhân",
        "phases": {
            "unlearn": {
                "title": "🔥 Unlearn — Phá bỏ",
                "weeks": "Tuần 1–3",
                "color": "#ef4444",
                "desc": "Nhận diện các thói quen phản tác dụng và lý do trì hoãn.",
                "tasks": [
                    "Audit toàn bộ thói quen hàng ngày",
                    "Phân tích vòng lặp Cue-Routine-Reward",
                    "Identify top 3 thói quen cần phá bỏ",
                ]
            },
            "relearn": {
                "title": "🌱 Relearn — Thiết lập",
                "weeks": "Tuần 4–7",
                "color": "#f59e0b",
                "desc": "Thiết kế hệ thống cá nhân: lịch trình, environment design và trigger.",
                "tasks": [
                    "Thiết kế morning routine mới",
                    "Cài đặt 'Implementation Intentions'",
                    "Xây dựng Dashboard theo dõi tiến độ",
                ]
            },
            "execute": {
                "title": "🚀 Execute — Vận hành",
                "weeks": "Tuần 8–10",
                "color": "#10b981",
                "desc": "Vận hành hệ thống 30 ngày liên tục và ghi lại dữ liệu.",
                "tasks": [
                    "30-day challenge cá nhân",
                    "Weekly retrospective với AI Coach",
                    "Demo Day: trình bày kết quả với cộng đồng",
                ]
            }
        }
    },
    {
        "id": 3,
        "title": "Cohort 3 — Vươn tới Xuất sắc",
        "weeks": "12 tuần",
        "status": "upcoming",
        "start_date": "15/11/2025",
        "theme": "Hiệu suất đỉnh cao & Tầm nhìn dài hạn",
        "phases": {
            "unlearn": {
                "title": "🔥 Unlearn — Phá bỏ",
                "weeks": "Tuần 1–4",
                "color": "#ef4444",
                "desc": "Tháo gỡ vùng an toàn và nỗi sợ thất bại quy mô lớn.",
                "tasks": [
                    "Vẽ 'Fear Map' cá nhân",
                    "Thực hành 'Fear Setting' của Tim Ferriss",
                    "Phiên đối thoại chiều sâu về Tầm nhìn 10 năm",
                ]
            },
            "relearn": {
                "title": "🌱 Relearn — Thiết lập",
                "weeks": "Tuần 5–9",
                "color": "#f59e0b",
                "desc": "Học về hiệu suất cao, quản lý năng lượng và xây dựng tầm nhìn.",
                "tasks": [
                    "Xây dựng Personal Vision Statement",
                    "Áp dụng Time Blocking & Deep Work",
                    "Mentorship session (AI + Human mentor)",
                ]
            },
            "execute": {
                "title": "🚀 Execute — Vận hành",
                "weeks": "Tuần 10–12",
                "color": "#10b981",
                "desc": "Launch một dự án có ý nghĩa thực sự với bản thân.",
                "tasks": [
                    "Launch 1 sản phẩm / dịch vụ / dự án cá nhân",
                    "Trình bày Graduation Project",
                    "Định hướng cho Cohort tiếp theo",
                ]
            }
        }
    }
]

def render_phase_card(phase_key, phase_data):
    import streamlit as st
    color = phase_data["color"]
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        border-left: 5px solid {color};
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
            <h4 style="margin: 0; color: {color}; font-size: 1.05rem;">{phase_data['title']}</h4>
            <span style="
                background: {color}20;
                color: {color};
                padding: 2px 12px;
                border-radius: 20px;
                font-size: 0.78rem;
                font-weight: 700;
            ">{phase_data['weeks']}</span>
        </div>
        <p style="margin: 0 0 0.8rem 0; color: #555; font-size: 0.9rem; line-height: 1.5;">{phase_data['desc']}</p>
        <ul style="margin: 0; padding-left: 1.2rem; color: #374151; font-size: 0.85rem;">
            {"".join(f"<li style='margin-bottom: 4px;'>{task}</li>" for task in phase_data['tasks'])}
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_great_rebuild():
    import streamlit as st
    # Header
    st.markdown("""
    <style>
    .rebuild-hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 24px;
        padding: 3rem 2.5rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .rebuild-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(147,51,234,0.15) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    .cohort-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0e6ff;
        transition: all 0.3s ease;
    }
    .cohort-card:hover {
        box-shadow: 0 8px 30px rgba(147,51,234,0.15);
        transform: translateY(-2px);
    }
    .status-badge-active {
        background: #d1fae5; color: #065f46;
        padding: 3px 14px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 700;
        display: inline-block;
    }
    .status-badge-upcoming {
        background: #e0e7ff; color: #3730a3;
        padding: 3px 14px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 700;
        display: inline-block;
    }
    .phase-arrow {
        text-align: center;
        font-size: 1.5rem;
        color: #9333ea;
        margin: 0.3rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown("""
    <style>
    /* Siêu ép màu trắng cho tiêu đề và mô tả */
    .rebuild-hero [id="hero-title"], 
    .rebuild-hero [id="hero-title"] *,
    .rebuild-hero .hero-desc,
    .rebuild-hero .hero-desc * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    .rebuild-hero .stat-label, .rebuild-hero .stat-label * {
        color: rgba(255,255,255,0.8) !important;
        -webkit-text-fill-color: rgba(255,255,255,0.8) !important;
    }
    /* Ép màu trắng cho stat-val */
    .rebuild-hero .stat-val, .rebuild-hero .stat-val * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
    <div class="rebuild-hero">
        <div style="position: relative; z-index: 1;">
            <div id="hero-title" style="color: white !important; font-size: 2.8rem; font-weight: 900; margin: 0 0 0.5rem 0; letter-spacing: -1px; line-height: 1.2;">
                The Great Rebuild
            </div>
            <p class="hero-desc" style="color: white !important; font-size: 1.1rem; margin: 0 0 1.5rem 0; max-width: 600px; margin-left: auto; margin-right: auto;">
                Chương trình học tập theo kỳ — Phá bỏ cũ, Xây dựng mới, Vận hành thực chiến
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; color: white;">
                <div style="text-align: center;">
                    <div class="stat-val" style="color: #ffffff !important; font-size: 2rem; font-weight: 800;">3</div>
                    <div class="stat-label" style="font-size: 0.85rem;">Cohorts</div>
                </div>
                <div style="text-align: center;">
                    <div class="stat-val" style="color: #ffffff !important; font-size: 2rem; font-weight: 800;">8–12</div>
                    <div class="stat-label" style="font-size: 0.85rem;">Tuần / Kỳ</div>
                </div>
                <div style="text-align: center;">
                    <div class="stat-val" style="color: #ffffff !important; font-size: 2rem; font-weight: 800;">3</div>
                    <div class="stat-label" style="font-size: 0.85rem;">Giai đoạn</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Framework Overview
    st.markdown("### 📐 Framework 3 Giai đoạn")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef2f2, #fee2e2); border-radius: 16px; padding: 1.5rem; text-align: center; border: 2px solid #fca5a5;">
            <div style="font-size: 2.5rem;">🔥</div>
            <h3 style="color: #dc2626; margin: 0.5rem 0 0.3rem;">Unlearn</h3>
            <p style="color: #7f1d1d; font-weight: 700; margin: 0 0 0.5rem; font-size: 0.9rem;">Phá bỏ</p>
            <p style="color: #991b1b; font-size: 0.82rem; line-height: 1.5; margin: 0;">
                Nhận diện và giải phóng khỏi những niềm tin, thói quen cũ đang kìm hãm sự phát triển.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fffbeb, #fef3c7); border-radius: 16px; padding: 1.5rem; text-align: center; border: 2px solid #fcd34d; position: relative; top: -8px;">
            <div style="font-size: 2.5rem;">🌱</div>
            <h3 style="color: #d97706; margin: 0.5rem 0 0.3rem;">Relearn</h3>
            <p style="color: #78350f; font-weight: 700; margin: 0 0 0.5rem; font-size: 0.9rem;">Thiết lập</p>
            <p style="color: #92400e; font-size: 0.82rem; line-height: 1.5; margin: 0;">
                Xây dựng tư duy mới, kỹ năng mới và các khuôn mẫu hành vi phù hợp hơn.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-radius: 16px; padding: 1.5rem; text-align: center; border: 2px solid #86efac;">
            <div style="font-size: 2.5rem;">🚀</div>
            <h3 style="color: #16a34a; margin: 0.5rem 0 0.3rem;">Execute</h3>
            <p style="color: #14532d; font-weight: 700; margin: 0 0 0.5rem; font-size: 0.9rem;">Vận hành</p>
            <p style="color: #166534; font-size: 0.82rem; line-height: 1.5; margin: 0;">
                Áp dụng vào thực tiễn, đo lường, điều chỉnh và tạo ra kết quả có thể nhìn thấy được.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Danh sách Cohorts
    st.markdown("### 🗓️ Lộ trình các Kỳ học")

    for cohort in COHORTS:
        status_badge = (
            '<span class="status-badge-active">🟢 Đang diễn ra</span>'
            if cohort["status"] == "active"
            else '<span class="status-badge-upcoming">🔵 Sắp bắt đầu</span>'
        )

        with st.expander(f"**{cohort['title']}** — {cohort['weeks']}  |  Bắt đầu: {cohort['start_date']}", expanded=(cohort["status"] == "active")):
            # Header info
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                {status_badge}
                <span style="background: #f3e8ff; color: #7c3aed; padding: 3px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;">
                    🎯 Chủ đề: {cohort['theme']}
                </span>
                <span style="background: #e0e7ff; color: #3730a3; padding: 3px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;">
                    ⏱️ {cohort['weeks']}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # 3 Phase cards
            render_phase_card("unlearn", cohort["phases"]["unlearn"])
            st.markdown('<div class="phase-arrow">↓</div>', unsafe_allow_html=True)
            render_phase_card("relearn", cohort["phases"]["relearn"])
            st.markdown('<div class="phase-arrow">↓</div>', unsafe_allow_html=True)
            render_phase_card("execute", cohort["phases"]["execute"])

            # Nút tham gia
            st.markdown("<br>", unsafe_allow_html=True)
            if cohort["status"] == "active":
                if st.button(f"🚀 Tham gia Cohort {cohort['id']} ngay", key=f"join_{cohort['id']}", use_container_width=True, type="primary"):
                    st.success(f"✅ Bạn đã đăng ký tham gia **{cohort['title']}**! Chúng tôi sẽ liên hệ sớm.")
            else:
                if st.button(f"🔔 Đăng ký nhận thông báo Cohort {cohort['id']}", key=f"notify_{cohort['id']}", use_container_width=True):
                    st.info(f"📩 Đã ghi nhận! Bạn sẽ được thông báo khi **{cohort['title']}** mở đăng ký.")

    # Nút quay về
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Quay về trang chủ", use_container_width=False):
        st.session_state.current_page = "chat"
        st.rerun()

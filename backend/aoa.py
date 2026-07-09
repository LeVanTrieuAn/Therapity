import json
import os
import datetime
import cms_helper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(os.path.dirname(BASE_DIR), "database")
AOA_LIKES_FILE = os.path.join(DATABASE_DIR, "aoa_likes.json")
AOA_ACTIONS_FILE = os.path.join(DATABASE_DIR, "aoa_actions.json")
REPOSTS_FILE = os.path.join(DATABASE_DIR, "reposts.json")

def load_json_db(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                db = json.load(f)
                
                def translate_str(text):
                    en_text = text
                    mapping = {
                        'Đã hoàn thành:': 'Completed:',
                        'Viết ra 3 kỳ vọng cụ thể đang gây áp lực và thay thế bằng thực tế': 'Write down 3 specific expectations causing pressure and replace them with reality',
                        'Insight & Bài học:': 'Insight & Lessons:',
                        'Xây dựng Routine buổi sáng (Morning Protocol)': 'Build Morning Routine (Morning Protocol)',
                        'Nghe Podcast: Quản trị Năng lượng - Andrew Huberman': 'Listen to Podcast: Energy Management - Andrew Huberman',
                        'Góc nhìn của mình về vấn đề:': 'My perspective on the issue:',
                        'Mọi người nghĩ sao?': 'What does everyone think?',
                        'Rất đồng tình với góc nhìn của bạn! Mình cũng từng trải qua điều tương tự.': 'Totally agree with your perspective! I have experienced something similar.',
                        'Khủng hoảng tuổi 25, mất định hướng': 'Quarter-life crisis, feeling lost',
                        'Áp lực đồng trang lứa khi bạn bè thành công': 'Peer pressure when friends succeed',
                        'Cảm giác trì hoãn không thể kiểm soát': 'Uncontrollable feeling of procrastination',
                        'Sợ thất bại khi bắt đầu một dự án mới': 'Fear of failure when starting a new project',
                        'Mất cân bằng giữa công việc và gia đình': 'Imbalance between work and family',
                        'Thiếu tự tin trong giao tiếp đám đông': 'Lack of confidence in public speaking',
                        'Làm sao để tìm thấy đam mê thực sự?': 'How to find true passion?',
                        'Ám ảnh sự hoàn hảo dẫn đến kiệt sức': 'Obsession with perfection leading to burnout',
                        'Sợ bị đánh giá bởi người khác': 'Fear of being judged by others',
                        'Muốn thay đổi nhưng luôn quay lại thói quen cũ': 'Want to change but always revert to old habits',
                        'Áp lực từ bản thân': 'Pressure from self',
                        'Công việc không phải vấn đề': 'Work is not the problem',
                        "Cam kết với từ 'cố gắng'": "Commitment to the word 'try'",
                        'Kỳ vọng bản thân': 'Self expectations'
                    }
                    for k, v in mapping.items():
                        en_text = en_text.replace(k, v)
                        
                    if en_text == text and len(text.strip()) > 0:
                        # Fallback to Google Translate for arbitrary user input
                        import requests
                        import urllib.parse
                        try:
                            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl=en&dt=t&q=" + urllib.parse.quote(text)
                            res = requests.get(url, timeout=3)
                            if res.status_code == 200:
                                return "".join([d[0] for d in res.json()[0]])
                        except:
                            pass
                            
                    return en_text

                changed = False
                for post in db.get('posts', []):
                    if isinstance(post.get('content'), str):
                        post['content'] = {
                            'vi': post['content'],
                            'en': translate_str(post['content'])
                        }
                        changed = True
                    for comment in post.get('comments', []):
                        if isinstance(comment.get('content'), str):
                            comment['content'] = {
                                'vi': comment['content'],
                                'en': translate_str(comment['content'])
                            }
                            changed = True
                
                if changed:
                    save_aoa_db(db)
                
                return db
            except:
                return default
    return default

def save_json_db(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_aoa_db():
    try:
        posts = cms_helper.get_aoa_posts()
        likes = load_json_db(AOA_LIKES_FILE, {})
        if not isinstance(likes, dict):
            likes = {}
        actions = load_json_db(AOA_ACTIONS_FILE, {})
        if not isinstance(actions, dict):
            actions = {}
        reposts = load_json_db(REPOSTS_FILE, {})
        if not isinstance(reposts, dict):
            reposts = {}
        
        for p in posts:
            try:
                p_id = str(p.get("id", ""))
                if not p_id:
                    continue
                p["liked_by"] = likes.get(p_id, [])
                
                p_act = actions.get(p_id)
                if not isinstance(p_act, dict):
                    p_act = {}
                p["deleted_by"] = p_act.get("deleted_by", [])
                p["hidden_by"] = p_act.get("hidden_by", [])
                p["saved_by"] = p_act.get("saved_by", [])
                
                if p_id in reposts:
                    p["reposted_post"] = reposts[p_id]
            except Exception as e:
                print(f"Error loading post extras for {p.get('id')}: {e}")
                
        return {"posts": posts}
    except Exception as e:
        print(f"Error in load_aoa_db: {e}")
        return {"posts": []}

def save_aoa_db(data):
    pass

def create_post(user_name, user_avatar, content, graph_data, post_privacy="public"):
    new_post = cms_helper.create_aoa_post(user_name, user_avatar, content, graph_data, post_privacy)
    db = load_aoa_db()
    import datetime
    formatted_post = {
        "id": new_post.get("id", str(datetime.datetime.now().timestamp())),
        "author_name": user_name,
        "author_avatar": user_avatar,
        "content": new_post.get("content", content),
        "graph_data": graph_data,
        "timestamp": new_post.get("timestamp", datetime.datetime.now().isoformat() + "Z"),
        "likes": 0,
        "shares": 0,
        "comments": [],
        "post_status": "active",
        "post_privacy": post_privacy
    }
    if "posts" not in db:
        db["posts"] = []
    db["posts"].insert(0, formatted_post)
    save_aoa_db(db)
    return formatted_post

def render_aoa_page():
    import streamlit as st
    from streamlit_agraph import agraph, Node, Edge, Config
    # CSS làm đẹp giao diện
    st.markdown("""
    <style>
    .post-container {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .post-author {
        font-weight: bold;
        font-size: 1.1em;
    }
    .post-time {
        color: #999077;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='margin-bottom: 0px;'>AOA - Ask Others Anything</h2>", unsafe_allow_html=True)
    st.caption("Cộng đồng chia sẻ và cố vấn tâm lý. Noi gương những tư duy tích cực.")
            
    st.markdown("---")
        
    db = load_aoa_db()
    
    tab_community, tab_my_posts = st.tabs(["Bài đăng cộng đồng", "Bài đăng của tôi"])
    
    current_username = st.session_state.saved_chats.get("user_name", "Người dùng Thapsang")
    current_avatar = st.session_state.saved_chats.get("user_avatar", "")
    
    with tab_community:
        if not db["posts"]:
            st.info("Chưa có bài đăng nào trong cộng đồng. Bạn hãy là người đầu tiên!")
        else:
            for i, post in enumerate(db["posts"]):
                render_post(post, i, db, current_username, current_avatar)
                
    with tab_my_posts:
        my_posts = [p for p in db["posts"] if p["author_name"] == current_username]
        if not my_posts:
            st.info("Bạn chưa có bài đăng nào. Hãy vào Trò chuyện và chia sẻ Bản đồ tư duy của bạn!")
        else:
            for i, post in enumerate(my_posts):
                render_post(post, f"my_{i}", db, current_username, current_avatar)

def render_post(post, index, db, current_username, current_avatar):
    import streamlit as st
    from streamlit_agraph import agraph, Node, Edge, Config
    with st.container(border=True):
        col_avatar, col_content = st.columns([1, 11])
        with col_avatar:
            avatar = post.get("author_avatar")
            if not avatar:
                avatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2NjYyI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgM2MxLjY2IDAgMyAxLjM0IDMgM3MtMS4zNCAzLTMgMy0zLTEuMzQtMy0zIDEuMzQtMyAzLTN6bTAgMTQuMmMtMi41IDAtNC43MS0xLjI4LTYtMy4yMi4wMy0xLjk5IDQtMy4wOCA2LTMuMDggMS45OSAwIDUuOTcgMS4wOSA2IDMuMDgtMS4yOSAxLjk0LTMuNSAzLjIyLTYgMy4yMnoiLz48L3N2Zz4="
            st.markdown(
                f'<img src="{avatar}" width="48" height="48" style="border-radius: 50%; object-fit: cover;">', 
                unsafe_allow_html=True
            )
        with col_content:
            st.markdown(f"<span class='post-author'>{post.get('author_name', 'Người dùng Thapsang')}</span> <span class='post-time'>• {post.get('timestamp', '')}</span>", unsafe_allow_html=True)
            st.write(post.get("content", ""))
            
            # Mini Mindmap
            graph_data = post.get("graph_data", {"nodes": [], "edges": []})
            if graph_data.get("nodes"):
                with st.expander("Xem Bản đồ tư duy đính kèm", expanded=True):
                    nodes = []
                    edges = []
                    for n in graph_data.get("nodes", []):
                        nodes.append(Node(id=n["id"], label=n["label"], color=n.get("color", "#e9c400"), size=25))
                    for e in graph_data.get("edges", []):
                        color = "#ffb4ab" if e.get("is_contradiction") else "#e9c400"
                        dashes = True if e.get("is_contradiction") else False
                        width = 3 if e.get("is_contradiction") else 1
                        edges.append(Edge(source=e["source"], target=e["target"], label=e.get("label", ""), color=color, dashes=dashes, width=width))
                    
                    config = Config(
                        width="100%", 
                        height=400, 
                        directed=True, 
                        hierarchical=False
                    )
                    config.physics["barnesHut"] = {
                        "springLength": 200,
                        "springConstant": 0.02,
                        "damping": 0.5
                    }
                    config.physics["stabilization"] = {"iterations": 50}
                    try:
                        agraph(nodes=nodes, edges=edges, config=config)
                    except Exception as e:
                        st.caption("Bản đồ đang được tải...")
                        
            # Tương tác (Like, Comment, Share, Delete)
            is_author = (post.get('author_name') == current_username)
            if is_author:
                c_like, c_comment, c_share, c_delete, c_empty = st.columns([1.5, 1.5, 1.5, 1.5, 6])
            else:
                c_like, c_comment, c_share, c_empty = st.columns([1.5, 1.5, 1.5, 7.5])
                
            with c_like:
                if st.button(f"❤️ {post.get('likes', 0)}", key=f"like_{post['id']}_{index}", help="Thích"):
                    post["likes"] = post.get("likes", 0) + 1
                    save_aoa_db(db)
                    st.rerun()
            with c_comment:
                if st.button(f"💬 {len(post.get('comments', []))}", key=f"btn_cmt_{post['id']}_{index}", help="Bình luận"):
                    st.session_state[f"show_cmt_{post['id']}"] = not st.session_state.get(f"show_cmt_{post['id']}", False)
                    st.rerun()
            with c_share:
                if st.button(f"🔁 {post.get('shares', 0)}", key=f"share_{post['id']}_{index}", help="Chia sẻ"):
                    post["shares"] = post.get("shares", 0) + 1
                    save_aoa_db(db)
                    st.success("Đã sao chép liên kết!")
            if is_author:
                with c_delete:
                    if st.button("Xóa", key=f"del_{post['id']}_{index}", help="Xóa bài đăng"):
                        db["posts"].remove(post)
                        save_aoa_db(db)
                        st.rerun()
                    
            # Khu vực bình luận
            if st.session_state.get(f"show_cmt_{post['id']}", False):
                st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'>", unsafe_allow_html=True)
                for cmt in post.get("comments", []):
                    c_av, c_txt = st.columns([1, 15])
                    with c_av:
                        c_avatar = cmt.get("author_avatar")
                        if not c_avatar:
                            c_avatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2NjYyI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgM2MxLjY2IDAgMyAxLjM0IDMgM3MtMS4zNCAzLTMgMy0zLTEuMzQtMy0zIDEuMzQtMyAzLTN6bTAgMTQuMmMtMi41IDAtNC43MS0xLjI4LTYtMy4yMi4wMy0xLjk5IDQtMy4wOCA2LTMuMDggMS45OSAwIDUuOTcgMS4wOSA2IDMuMDgtMS4yOSAxLjk0LTMuNSAzLjIyLTYgMy4yMnoiLz48L3N2Zz4="
                        st.markdown(f'<img src="{c_avatar}" width="32" height="32" style="border-radius: 50%; object-fit: cover;">', unsafe_allow_html=True)
                    with c_txt:
                        st.markdown(f"**{cmt.get('author_name', 'Người dùng Thapsang')}** <span style='color: gray; font-size: 0.8em;'>• {cmt.get('timestamp', '')}</span>", unsafe_allow_html=True)
                        st.write(cmt.get("content", ""))
                
                # Input bình luận mới
                c_inp, c_btn = st.columns([8, 2])
                with c_inp:
                    cmt_text = st.text_input("Viết bình luận...", key=f"inp_cmt_{post['id']}_{index}", label_visibility="collapsed")
                with c_btn:
                    if st.button("Gửi", key=f"send_cmt_{post['id']}_{index}", use_container_width=True):
                        if cmt_text:
                            post["comments"].append({
                                "author_name": current_username,
                                "author_avatar": current_avatar,
                                "content": cmt_text,
                                "timestamp": datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
                            })
                            save_aoa_db(db)
                            st.rerun()

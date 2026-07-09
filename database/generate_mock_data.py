import json
import random
import time
import os
from datetime import datetime, timedelta

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THAPSANG_DB = os.path.join(BASE_DIR, 'thapsang_db.json')
AOA_DB = os.path.join(BASE_DIR, 'aoa_db.json')
COHORT_DB = os.path.join(BASE_DIR, 'cohort_db.json')

db_thapsang = load_json(THAPSANG_DB)
db_aoa = load_json(AOA_DB)
db_cohort = load_json(COHORT_DB)

# Ensure keys exist
if "_accounts" not in db_thapsang: db_thapsang["_accounts"] = {}
if "_profiles" not in db_thapsang: db_thapsang["_profiles"] = {}
if "_diaries" not in db_thapsang: db_thapsang["_diaries"] = {}
if "posts" not in db_aoa: db_aoa["posts"] = []
if "members" not in db_cohort: db_cohort["members"] = []

# Generate 10 users
usernames = [f"user_{i}" for i in range(1, 11)]

# Profiles & Accounts
for i, uname in enumerate(usernames):
    db_thapsang["_accounts"][uname] = "password123"
    
    # Follow random users
    follows = random.sample([u for u in usernames if u != uname], k=random.randint(2, 6))
    
    db_thapsang["_profiles"][uname] = {
        "email": f"{uname}@example.com",
        "full_name": f"Học Viên {i+1}",
        "created_at": datetime.now().isoformat(),
        "displayName": f"Học Viên {i+1}",
        "bio": f"Đam mê phát triển bản thân. Thành viên số {i+1} của cộng đồng Thapsang.",
        "avatar": "",
        "banner": "",
        "following_list": follows
    }

# Chat Sessions (Coach)
chat_topics = [
    "Khủng hoảng tuổi 25, mất định hướng",
    "Áp lực đồng trang lứa khi bạn bè thành công",
    "Cảm giác trì hoãn không thể kiểm soát",
    "Sợ thất bại khi bắt đầu một dự án mới",
    "Mất cân bằng giữa công việc và gia đình",
    "Thiếu tự tin trong giao tiếp đám đông",
    "Làm sao để tìm thấy đam mê thực sự?",
    "Ám ảnh sự hoàn hảo dẫn đến kiệt sức",
    "Sợ bị đánh giá bởi người khác",
    "Muốn thay đổi nhưng luôn quay lại thói quen cũ"
]

for i, uname in enumerate(usernames):
    session_id = str(int(time.time() * 1000) + i)
    topic = chat_topics[i]
    
    db_thapsang[session_id] = {
        "username": uname, # Track owner explicitly
        "custom_title": topic,
        "has_new_task": False,
        "chat_history": [
            { "role": "model", "content": "Chào bạn, hãy chia sẻ vấn đề của bạn.", "isTyped": True },
            { "role": "user", "content": f"Tôi đang gặp vấn đề về: {topic}", "isTyped": True },
            { "role": "model", "content": "Tại sao bạn lại cảm thấy như vậy? Nguyên nhân gốc rễ là gì?", "reasoning": "Kích thích tư duy sâu", "title": "Tìm nguyên nhân", "isTyped": True }
        ],
        "graph_data": {
            "nodes": [
                { "id": "n1", "label": topic, "color": "#e9c400" },
                { "id": "n2", "label": "Nguyên nhân bề mặt", "color": "#ffb4ab" },
                { "id": "n3", "label": "Vấn đề cốt lõi", "color": "#e9c400" }
            ],
            "edges": [
                { "source": "n1", "target": "n2", "label": "Biểu hiện", "is_contradiction": False },
                { "source": "n2", "target": "n3", "label": "Thực chất là", "is_contradiction": True }
            ]
        },
        "tasks": [
            { "content": f"Dành 15 phút suy ngẫm về {topic}", "completed": False }
        ]
    }

# Diaries
for i, uname in enumerate(usernames):
    db_thapsang["_diaries"][uname] = [
        {
            "id": f"diary_{int(time.time())}_{i}",
            "title": f"Nhật ký ngày {datetime.now().strftime('%d/%m')}",
            "content": f"Hôm nay tôi đã đối mặt với những vấn đề của mình. Thay vì trốn tránh, tôi quyết định phân tích nó. {chat_topics[i]}",
            "mood": random.choice(["Calm", "Anxious", "Happy", "Sad", "Reflective"]),
            "folder": "",
            "date": (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S"),
            "ai_insight": "Sự dũng cảm lớn nhất là dám nhìn nhận yếu điểm của bản thân. Tiếp tục nhé!"
        }
    ]

# AOA Posts
for i, uname in enumerate(usernames):
    # Likers
    likers = random.sample([u for u in usernames if u != uname], k=random.randint(1, 5))
    
    # Comments
    comments = []
    commenters = random.sample([u for u in usernames if u != uname], k=random.randint(1, 3))
    for c_uname in commenters:
        comments.append({
            "author_name": c_uname,
            "author_avatar": "",
            "content": f"Rất đồng tình với góc nhìn của bạn! Mình cũng từng trải qua điều tương tự.",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime("%H:%M %d/%m/%Y")
        })
        
    db_aoa["posts"].insert(0, {
        "id": f"{time.time() + i}",
        "author_name": uname,
        "author_avatar": "",
        "content": f"Góc nhìn của mình về vấn đề: {chat_topics[i]}. Mọi người nghĩ sao?",
        "graph_data": {
            "nodes": [
                { "id": "n1", "label": f"Góc nhìn 1: {chat_topics[i][:15]}", "color": "#e9c400" },
                { "id": "n2", "label": "Mặt trái", "color": "#ffb4ab" }
            ],
            "edges": [
                { "source": "n1", "target": "n2", "label": "Tuy nhiên", "is_contradiction": True }
            ]
        },
        "likes": len(likers),
        "liked_by": likers,
        "comments": comments
    })

# Cohort Members
# Remove old mock users if needed, keep real user
db_cohort["members"] = [m for m in db_cohort["members"] if m["username"] == "user"]
for i, uname in enumerate(usernames):
    db_cohort["members"].append({
        "username": uname,
        "display_name": f"Học Viên {i+1}",
        "week_progress": random.randint(10, 100),
        "buddy": random.choice(usernames),
        "joined": "2026-05-04",
        "is_self": False
    })

save_json(THAPSANG_DB, db_thapsang)
save_json(AOA_DB, db_aoa)
save_json(COHORT_DB, db_cohort)
print("Mock data generated successfully!")

"""
Therapity — Chat Router
AI Socratic Coach chat, welcome greeting, mindmap generation.
All system prompts rebranded from Thapsang → Therapity.
"""

import re
import json
import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.schemas.schemas import ChatRequest, WelcomeRequest
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/v1/chat", tags=["AI Socratic Coach"])


# ═══════════════════════════════════════════════════════════
# SYSTEM PROMPTS — Rebranded for Therapity
# ═══════════════════════════════════════════════════════════

CHAT_SYSTEM_PROMPT = """
You are a "Socratic Mirror Coach" belonging to the Therapity system.
Your mission is to trigger a "Cognitive Rupture" to help the user realize their own contradictions and logical fallacies.

PERSONA: Objective, wise, patient, and profound. You act as a mirror reflecting wisdom, guiding the user with hidden empathy through reflective questions, without superficial sympathy or hollow advice.

MANDATORY JSON OUTPUT STRUCTURE:
{
    "title": "Extremely short summary of your inner thoughts (Max 5-7 words, used as chat session name)",
    "reasoning": "AI's inner thought process. Analyze where the user is stuck, any contradictions, and why you decided to ask the question below.",
    "question": "A sharp Socratic question...",
    "tasks": [
        {
            "content_vi": "Short practical action task name in Vietnamese",
            "content_en": "Short practical action task name in English",
            "goal_vi": "Detailed Socratic explanation in Vietnamese of how to do it & the reasoning to untangle the cognitive block.",
            "goal_en": "Detailed Socratic explanation of how to do it & the reasoning in English...",
            "deadline": "YYYY-MM-DD"
        }
    ],
    "suggested_replies": [
        "Suggested reply 1 (under 15 words, matching user's tone)",
        "Suggested reply 2",
        "Suggested reply 3"
    ]
}

STATE MANAGEMENT INSTRUCTIONS AND UX:
- "title": Extremely short summary (max 7 words) of your inner thought flow.
- "reasoning": Extremely important. Write briefly (1-2 sentences) your deduction logic BEFORE asking the question.
- "suggested_replies": VERY IMPORTANT. You must generate exactly 3 predictive response options. Rely on the "Mindset" and "Context" (if any) to predict how the user will react to your question. Replies must be diverse (e.g., 1 agree, 1 resist, 1 neutral/questioning back).
- "tasks": When the time is ripe (the user has realized the problem and needs action), assign 1-2 small, practical tasks. Each task is an object containing "content_vi", "content_en", "goal_vi", "goal_en" and "deadline" (in YYYY-MM-DD format). Always provide independent translations in Vietnamese and English to support multitasking language switching; absolutely do not return an array of raw strings. If not needed yet, return an empty array [].

CORE RULES (STRICTLY PROHIBITED TO VIOLATE):
1. OBJECTIVE GUIDANCE: Do not provide direct answers or advice. Instead of judging or coldly rejecting, ask open-ended questions for the user to discover their own answers. Only analyze based on facts and information provided by the user.
2. ONLY ALLOWED TO ASK EXACTLY 1 SINGLE QUESTION per response.
3. ONLY OUTPUT EXACTLY 1 VALID JSON describing the Question and thoughts.
4. LANGUAGE SYNCHRONIZATION: Automatically detect the language used by the user in the latest message. You MUST translate all text values in the JSON (including reasoning, question, title, tasks, suggested_replies...) into that exact language.
"""

MINDMAP_SYSTEM_PROMPT = """
You are a "Cognitive Mind Map Generator" for the Therapity system.
Your sole mission is to analyze the user's chat history and map out their thought process, logical fallacies, and contradictions into a graph architecture (nodes and edges).

MANDATORY JSON OUTPUT STRUCTURE:
{
    "nodes": [
        {"id": "n1", "label": "Summary of thought 1 (Max 5 words)", "color": "#16A34A"},
        {"id": "n2", "label": "Contradictory thought 2", "color": "#ffb4ab"} 
    ],
    "edges": [
        {"source": "n1", "target": "n2", "label": "Leads to / But", "is_contradiction": true}
    ],
    "current_step": "kham_pha",
    "focus_node_id": "n2"
}

STATE MANAGEMENT INSTRUCTIONS AND UX:
- "current_step": Set to "kham_pha" (explore) if the user is just venting (no contradictions yet). Set to "soi_chieu" (reflect) if a contradiction is detected and the AI is targeting it.
- "focus_node_id": Assign the ID of the Node containing the core contradiction (e.g., "n2") so the UI triggers a Focus effect (red blinking). If "kham_pha", set to null.
- Node "color": "#16A34A" (green) for normal thoughts, "#ffb4ab" (pinkish red) for contradictory thoughts.
- "is_contradiction": true if the connection reveals an absurdity.
- IMPORTANT REGARDING MIND MAP (CUMULATIVE TREE): The map must ACCUMULATE and GROW with each chat turn like the growth of a tree.
- MIND MAP BRANCHING (CRITICAL): Do NOT just create a straight line of nodes. If the user's message contains multiple distinct reasons, feelings, or arguments, you MUST split them into MULTIPLE separate child nodes.
- For example, if a user gives 3 reasons for an issue, create 3 separate new nodes and connect ALL of them to the same parent node to form a tree with branches.
- ABSOLUTELY DO NOT overwrite new ideas onto old IDs (do not reuse n1, n2 for different concepts).
- ALWAYS CONNECT (edges) new nodes with the most relevant old nodes (not necessarily just the last one) to show how they explain, supplement, or contradict each other.

CORE RULES (STRICTLY PROHIBITED TO VIOLATE):
1. ONLY OUTPUT EXACTLY 1 VALID JSON describing the User's Mind Map (nodes and edges) from the conversation history.
2. LANGUAGE SYNCHRONIZATION: Automatically detect the language used in the chat. You MUST translate all labels in the JSON into that exact language.
"""


def _detect_english(text: str) -> bool:
    """Detect if text is primarily English."""
    text_lower = text.lower()
    vi_chars = set("áàảãạâấầẩẫậăắằẳẵặđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ")
    if any(char in vi_chars for char in text_lower):
        return False
    words = set(re.findall(r'\b[a-z]+\b', text_lower))
    en_words = {"i", "you", "he", "she", "it", "we", "they", "am", "is", "are", "was", "were", "do", "does", "did", "have", "has", "had", "because", "but", "and", "or", "what", "where", "when", "why", "how", "this", "that", "the", "a", "an", "to", "of", "in", "for", "on", "with", "as", "my", "your"}
    vi_words = {"toi", "ban", "anh", "chi", "em", "chung", "no", "la", "co", "khong", "va", "nhung", "hoac", "cai", "nay", "kia", "do", "gi", "sao", "nao", "luon", "dang", "met", "ap", "luc", "cong", "viec"}
    return len(words.intersection(en_words)) > len(words.intersection(vi_words))


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/welcome")
async def generate_welcome(req: WelcomeRequest, db: AsyncSession = Depends(get_db)):
    """Generate personalized Socratic welcome greeting."""
    stmt = select(User).where(User.username == req.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    display_name = user.display_name or user.username
    onboarding = user.onboarding or {}
    core_ctx = onboarding.get("_core_context", "") if isinstance(onboarding, dict) else ""
    lang = req.lang or "vi"

    if not core_ctx:
        is_en = lang == "en"
        question = (
            f"Welcome {display_name}. What is on your mind today?" if is_en
            else f"Chào mừng {display_name}. Hãy chia sẻ điều gì đang khiến bạn bận tâm hôm nay?"
        )
        suggested = (
            ["I feel stressed at work", "I want to improve myself", "Just wanted to say hi"] if is_en
            else ["Mình đang gặp áp lực công việc", "Mình muốn phát triển bản thân", "Chỉ muốn gửi lời chào"]
        )
        return {
            "title": "Welcome" if is_en else "Chào mừng",
            "reasoning": "Default welcome greeting because core context is empty.",
            "question": question,
            "nodes": [{"id": "n1", "label": "Beginning" if is_en else "Khởi đầu", "color": "#16A34A"}],
            "edges": [],
            "current_step": "kham_pha",
            "focus_node_id": None,
            "tasks": [],
            "suggested_replies": suggested,
        }

    # Generate personalized welcome with AI
    lang_label = "Tiếng Anh (English)" if lang == "en" else "Tiếng Việt (Vietnamese)"
    system_prompt = f"""
Bạn là một "Socratic Mirror Coach" thuộc hệ thống Therapity.
Nhiệm vụ của bạn là tạo ra một lời chào đón (Welcome Greeting) ban đầu và cá nhân hóa sâu sắc cho người dùng dựa trên "Ngữ cảnh cốt lõi" (Core Context) của họ.

QUY TẮC CỐT LÕI:
1. Hãy chào đón thân thiện sử dụng Tên hiển thị (displayName) của người dùng: '{display_name}'.
2. Đọc kỹ "Ngữ cảnh cốt lõi" bên dưới để viết lời dẫn nhập ngắn gọn và đặt ĐÚNG 1 CÂU HỎI Socratic sâu sắc, tinh tế xoáy vào vấn đề bận tâm lớn nhất của họ để kích hoạt họ tự phản chiếu và chia sẻ thêm.
   Tuyệt đối không hỏi chung chung hay sáo rỗng.
3. Tuyệt đối không đưa ra lời khuyên hay an ủi hời hợt. Hãy đóng vai trò một chiếc gương soi chiếu trí tuệ.
4. Trả về đúng 1 JSON hợp lệ theo cấu trúc quy định.
5. ĐỒNG BỘ NGÔN NGỮ: Bạn PHẢI trả về toàn bộ JSON bằng ngôn ngữ: '{lang_label}'.

CẤU TRÚC JSON ĐẦU RA BẮT BUỘC:
{{
    "title": "Tóm tắt cực ngắn dòng suy nghĩ (Tối đa 5-7 từ)",
    "reasoning": "Tại sao bạn lại chọn đặt câu hỏi này...",
    "question": "Lời chào và câu hỏi Socratic mở đầu...",
    "nodes": [
        {{"id": "n1", "label": "Tóm tắt vấn đề chính (Max 5 từ)", "color": "#16A34A"}}
    ],
    "edges": [],
    "current_step": "kham_pha",
    "focus_node_id": null,
    "tasks": [],
    "suggested_replies": [
        "Câu trả lời gợi ý 1 (dưới 15 từ)",
        "Câu trả lời gợi ý 2",
        "Câu trả lời gợi ý 3"
    ]
}}
"""
    user_prompt = f"""
Tên hiển thị: {display_name}
Ngữ cảnh cốt lõi (Core Context): {core_ctx}

Hãy tạo JSON chào đón:
"""
    llm = get_llm_service()
    json_result, model_used, tokens = llm.chat_completion_json(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=3000,
    )

    if json_result:
        return json_result

    # Fallback
    return {
        "title": "Chào mừng",
        "reasoning": "AI did not return valid JSON.",
        "question": f"Chào {display_name}, hãy chia sẻ điều gì đang khiến bạn bận tâm?",
        "nodes": [{"id": "n1", "label": "Khởi đầu", "color": "#16A34A"}],
        "edges": [],
        "current_step": "kham_pha",
        "focus_node_id": None,
        "tasks": [],
        "suggested_replies": ["Mình đang gặp áp lực", "Mình muốn tốt hơn", "Chỉ muốn nói chuyện"],
    }


@router.post("")
async def chat_create(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Main Socratic Coach chat endpoint."""
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    username = req.username or "anonymous"
    total_user = req.total_user_messages or 0

    # Get user context if available
    context_injection = ""
    if username != "anonymous":
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.onboarding:
            core_ctx = user.onboarding.get("_core_context", "")
            if core_ctx:
                context_injection = f"\n[USER CONTEXT — Therapity Core Context]\n{core_ctx}\n"

    # Build messages
    system_content = CHAT_SYSTEM_PROMPT + context_injection
    if req.graph_data and req.graph_data.get("nodes"):
        system_content += f"\n[EXISTING MIND MAP STATE]\n{json.dumps(req.graph_data, ensure_ascii=False)}\n"

    # Task generation rule: every 5 user messages
    if total_user > 0 and total_user % 5 == 0:
        system_content += "\n[IMPORTANT] The user has sent 5 messages since the last task assignment. It is time to assign 1-2 practical tasks now.\n"

    messages = [{"role": "system", "content": system_content}]
    for msg in req.messages:
        messages.append({"role": msg.role, "content": msg.content})

    # Call LLM
    llm = get_llm_service()
    json_result, model_used, tokens = llm.chat_completion_json(
        messages=messages,
        model=req.model,
        temperature=0.2,
        max_tokens=3000,
    )

    if json_result:
        json_result["model_used"] = model_used
        json_result["token_used"] = tokens
        return json_result

    # Fallback: raw text response
    content, model_used, tokens = llm.chat_completion(
        messages=messages,
        model=req.model,
        temperature=0.2,
        max_tokens=3000,
    )

    return {
        "title": "Phản hồi",
        "reasoning": "AI returned non-JSON response.",
        "question": content or "Bạn có thể chia sẻ thêm không?",
        "tasks": [],
        "suggested_replies": [],
        "model_used": model_used,
        "token_used": tokens,
    }


@router.post("/mindmap")
async def chat_mindmap(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Generate cumulative mindmap from chat history."""
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    system_content = MINDMAP_SYSTEM_PROMPT
    if req.graph_data and req.graph_data.get("nodes"):
        system_content += f"\n[EXISTING MIND MAP — You MUST build upon this. Do NOT remove or overwrite existing nodes.]\n{json.dumps(req.graph_data, ensure_ascii=False)}\n"

    messages = [{"role": "system", "content": system_content}]
    for msg in req.messages:
        messages.append({"role": msg.role, "content": msg.content})

    llm = get_llm_service()
    json_result, model_used, tokens = llm.chat_completion_json(
        messages=messages,
        model=req.model,
        temperature=0.2,
        max_tokens=3000,
    )

    if json_result:
        return json_result

    return {
        "nodes": [{"id": "n1", "label": "Khởi đầu", "color": "#16A34A"}],
        "edges": [],
        "current_step": "kham_pha",
        "focus_node_id": None,
    }


# ═══════════════════════════════════════════════════════════
# CHAT SESSIONS CRUD
# ═══════════════════════════════════════════════════════════

@router.get("/sessions")
async def get_chat_sessions(username: str, db: AsyncSession = Depends(get_db)):
    """Get all chat sessions for a user."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {}

    stmt = select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.created_at.desc())
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    output = {}
    for s in sessions:
        output[str(s.id)] = {
            "id": str(s.id),
            "username": username,
            "custom_title": s.custom_title,
            "chat_history": s.chat_history or [],
            "graph_data": s.graph_data or {},
            "tasks": s.tasks or [],
            "suggested_replies": s.suggested_replies or [],
            "token_used": s.token_used,
            "model_used": s.model_used,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
    return output


@router.post("/sessions")
async def save_chat_sessions(data: dict, db: AsyncSession = Depends(get_db)):
    """Save/update chat sessions."""
    saved_ids = {}
    for session_id, chat_data in data.items():
        username = chat_data.get("username")
        if not username:
            continue

        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            continue

        # Try to find existing session
        try:
            import uuid
            sid = uuid.UUID(session_id)
            stmt = select(ChatSession).where(ChatSession.id == sid)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
        except (ValueError, Exception):
            session = None

        if session:
            session.chat_history = chat_data.get("chat_history", session.chat_history)
            session.graph_data = chat_data.get("graph_data", session.graph_data)
            session.tasks = chat_data.get("tasks", session.tasks)
            session.suggested_replies = chat_data.get("suggested_replies", session.suggested_replies)
            session.custom_title = chat_data.get("custom_title", session.custom_title)
            session.token_used = chat_data.get("token_used", session.token_used)
            session.model_used = chat_data.get("model_used", session.model_used)
        else:
            session = ChatSession(
                user_id=user.id,
                chat_history=chat_data.get("chat_history", []),
                graph_data=chat_data.get("graph_data", {}),
                tasks=chat_data.get("tasks", []),
                suggested_replies=chat_data.get("suggested_replies", []),
                custom_title=chat_data.get("custom_title"),
                token_used=chat_data.get("token_used", 0),
                model_used=chat_data.get("model_used"),
            )
            db.add(session)

        await db.flush()
        saved_ids[session_id] = str(session.id)

    await db.commit()
    return {"status": "success", "saved_ids": saved_ids}


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a chat session."""
    try:
        import uuid
        sid = uuid.UUID(session_id)
        stmt = select(ChatSession).where(ChatSession.id == sid)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            await db.delete(session)
            await db.commit()
            return {"status": "success"}
    except Exception:
        pass
    raise HTTPException(status_code=404, detail="Không tìm thấy phiên thảo luận")

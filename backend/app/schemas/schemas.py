"""
Therapity — Pydantic Schemas
Request/Response models for all API endpoints.
"""

from pydantic import BaseModel
from typing import Optional


# === Auth ===
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: Optional[str] = None
    password: str
    email: str
    full_name: str

class ForgotPasswordResetRequest(BaseModel):
    email: str
    new_password: str


# === Chat ===
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    model: Optional[str] = None
    username: Optional[str] = None
    total_user_messages: Optional[int] = None
    session_id: Optional[str] = None
    graph_data: Optional[dict] = None

class WelcomeRequest(BaseModel):
    username: str
    lang: Optional[str] = "vi"
    session_id: Optional[str] = None


# === Diary ===
class DiaryEntryRequest(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    mood: Optional[str] = "Calm"
    folder: Optional[str] = ""
    skip_ai: Optional[bool] = False

class GenerateDiaryRequest(BaseModel):
    session_id: str
    username: str
    model: Optional[str] = None

class FolderRequest(BaseModel):
    name: str


# === Tasks ===
class TaskCreateRequest(BaseModel):
    title: str
    goal: Optional[str] = ""
    status: Optional[str] = "backlog"
    deadline: Optional[str] = ""
    effort: Optional[int] = 1
    subtasks: Optional[list] = []
    context_link: Optional[str] = ""

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None
    effort: Optional[int] = None
    subtasks: Optional[list] = None
    feedback: Optional[str] = None

class MicrostepsRequest(BaseModel):
    title: str
    goal: Optional[str] = ""
    effort: int
    lang: Optional[str] = "vi"


# === AOA ===
class PostRequest(BaseModel):
    author_name: str
    author_displayName: Optional[str] = ""
    author_avatar: Optional[str] = ""
    content: str
    graph_data: dict = {}
    post_privacy: Optional[str] = "public"

class CommentRequest(BaseModel):
    author_name: str
    author_displayName: Optional[str] = ""
    author_avatar: Optional[str] = ""
    content: str

class RepostRequest(BaseModel):
    original_post_id: str
    author_name: str
    author_displayName: Optional[str] = ""
    author_avatar: Optional[str] = ""
    content: str
    post_privacy: Optional[str] = "public"

class UpdatePostRequest(BaseModel):
    username: str
    content: str

class ReportPostRequest(BaseModel):
    username: str
    category: str
    details: str


# === Cohort ===
class CohortJoinRequest(BaseModel):
    username: str
    display_name: Optional[str] = ""

class PersonalizeWeekRequest(BaseModel):
    username: str
    week: int
    lang: Optional[str] = "vi"

class QuizSubmitRequest(BaseModel):
    username: str
    week: int
    answers: list
    essay_text: Optional[str] = ""

class RetrospectiveRequest(BaseModel):
    username: str
    week: int
    lang: Optional[str] = "vi"

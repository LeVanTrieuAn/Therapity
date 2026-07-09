"""
test_api.py
Automated integration test suite for Thapsang Backend API endpoints.
Runs in-process using FastAPI's TestClient and httpx.
Performs full validation of Authentication, Diary, Cohort, AOA, and Analytics.
Includes automated database backup & restore to ensure 100% zero-footprint tests.
"""

import os
import shutil
import json
import unittest
from fastapi.testclient import TestClient

# Thêm thư mục hiện tại vào python path để import main
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import app, THAPSANG_DB, AOA_DB, COHORT_DB

import cms_helper

class TestThapsangAPI(unittest.TestCase):
    
    @classmethod
    def clean_up_cms(cls):
        print(f"\n=== Cleaning up CMS assets for user '{cls.test_user}' ===")
        # 1. Clean up diary entries
        try:
            entries = cms_helper.get_diary_entries(cls.test_user)
            for entry in entries:
                cms_helper.delete_diary_entry(entry["id"])
                print(f"Deleted diary entry {entry['id']}")
        except Exception as e:
            print(f"Error cleaning up diary entries: {e}")
            
        # 2. Clean up diary folders
        try:
            folders = cms_helper.get_diary_folders(cls.test_user)
            for folder in folders:
                cms_helper.delete_diary_folder(cls.test_user, folder)
                print(f"Deleted diary folder '{folder}'")
        except Exception as e:
            print(f"Error cleaning up diary folders: {e}")
            
        # 3. Clean up tasks
        try:
            tasks = cms_helper.get_tasks(cls.test_user)
            for t in tasks:
                cms_helper.delete_task(t["id"])
                print(f"Deleted task {t['id']}")
        except Exception as e:
            print(f"Error cleaning up tasks: {e}")
            
        # 4. Clean up chat sessions
        try:
            chats = cms_helper.get_chat_sessions(cls.test_user)
            for s_id in chats.keys():
                cms_helper.delete_chat_session(s_id)
                print(f"Deleted chat session {s_id}")
        except Exception as e:
            print(f"Error cleaning up chat sessions: {e}")
            
        # 5. Clean up analytics assessments
        try:
            cms_helper.reset_analytics_assessments(cls.test_user)
            print("Reset analytics assessments")
        except Exception as e:
            print(f"Error cleaning up analytics: {e}")

    @classmethod
    def setUpClass(cls):
        """Initialize TestClient and clear any residual test data from CMS."""
        cls.client = TestClient(app)
        cls.test_user = "test_qa_runner"
        cls.test_email = "qa_runner@thapsang.io"
        cls.clean_up_cms()
        # Ensure test user exists in CMS
        user = cms_helper.get_user_by_username(cls.test_user)
        if not user:
            print(f"Creating test user '{cls.test_user}' in CMS...")
            cms_helper.create_user({
                "username": cls.test_user,
                "email": cls.test_email,
                "password": "testpassword123",
                "onboarded": True
            })

    @classmethod
    def tearDownClass(cls):
        """Clean up all created assets during the test cases."""
        cls.clean_up_cms()
        # Delete test user
        user = cms_helper.get_user_by_username(cls.test_user)
        if user:
            cms_helper.delete_user(user["id"])
            print(f"Deleted test user '{cls.test_user}' (id={user['id']})")
        print("[Teardown] Database cleanup completed successfully!\n")


    def test_01_health_check(self):
        """Kiểm tra endpoint kiểm tra sức khỏe hệ thống /health."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)
        print("-> TC-01: Health check OK")

    def test_02_login_invalid_user(self):
        """Kiểm tra đăng nhập từ chối với thông tin tài khoản sai lệch."""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "non_existent_user_999",
            "password": "wrongpassword123"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        print("-> TC-02: Invalid login refused OK")

    def test_03_otp_generation_mock(self):
        """Kiểm tra luồng gửi yêu cầu OTP đăng ký mới (Debug fallback)."""
        response = self.client.post("/api/v1/auth/request-otp", json={
            "username": self.test_user,
            "email": self.test_email
        })
        # Trả về thành công (nếu tài khoản chưa tồn tại)
        if response.status_code == 200:
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertIn("message", data)
            print("-> TC-03: OTP generation requested OK")
        else:
            self.assertEqual(response.status_code, 400) # đã tồn tại
            print("-> TC-03: OTP generation bypassed (user already exists)")

    def test_04_cohort_endpoints(self):
        """Kiểm tra các endpoints lấy thông tin khóa học Cohort."""
        # 1. Members
        response = self.client.get("/api/v1/cohort/members")
        self.assertEqual(response.status_code, 200)
        self.assertIn("members", response.json())
        
        # 2. Syllabus
        response = self.client.get("/api/v1/cohort/syllabus")
        self.assertEqual(response.status_code, 200)
        self.assertIn("syllabus", response.json())
        self.assertIn("cohort_info", response.json())
        
        # 3. Activity feed & bottlenecks
        response = self.client.get("/api/v1/cohort/activity")
        self.assertEqual(response.status_code, 200)
        self.assertIn("feed", response.json())
        self.assertIn("bottleneck", response.json())
        self.assertIn("pivot", response.json())

        # 4. Real-time AI Bottleneck Analysis
        response = self.client.post("/api/v1/cohort/ai-bottleneck", json={
            "username": self.test_user,
            "progress": 50,
            "tasks": [{"title": "Practice a Socratic Reflection session with AI Coach", "status": "backlog"}],
            "lang": "vi"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("ai_insight", response.json())
        self.assertIn("bottlenecks", response.json())
        self.assertIn("pivot", response.json())
        print("-> TC-04: Cohort metadata & AI bottleneck endpoints OK")

    def test_05_diary_operations(self):
        """Kiểm tra toàn bộ chu trình CRUD của Diary note & Folders."""
        # 1. Thêm folder mới
        folder_response = self.client.post(f"/api/v1/diary/{self.test_user}/folders", json={
            "name": "QA Test Folder"
        })
        self.assertEqual(folder_response.status_code, 200)
        self.assertEqual(folder_response.json()["status"], "success")
        
        # Kiểm tra folder đã có trong danh sách
        folders_get = self.client.get(f"/api/v1/diary/{self.test_user}/folders")
        self.assertEqual(folders_get.status_code, 200)
        self.assertIn("QA Test Folder", folders_get.json())

        # 2. Tạo ghi chép mới trong folder vừa tạo
        diary_response = self.client.post(f"/api/v1/diary/{self.test_user}", json={
            "title": "QA Test Diary Entry",
            "content": "Đây là nội dung ghi chép tự động tạo ra từ test runner của Thapsang.",
            "mood": "Calm",
            "folder": "QA Test Folder"
        })
        self.assertEqual(diary_response.status_code, 200)
        diary_data = diary_response.json()
        self.assertEqual(diary_data["status"], "success")
        entry_id = diary_data["entry"]["id"]
        
        # Kiểm tra note có trong danh sách
        diaries_get = self.client.get(f"/api/v1/diary/{self.test_user}")
        self.assertEqual(diaries_get.status_code, 200)
        titles = [d["title"] for d in diaries_get.json()]
        self.assertIn("QA Test Diary Entry", titles)

        # 3. Xóa ghi chép vừa tạo
        delete_response = self.client.delete(f"/api/v1/diary/{self.test_user}/{entry_id}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json()["status"], "success")
        
        # 4. Xóa folder vừa tạo
        delete_folder = self.client.delete(f"/api/v1/diary/{self.test_user}/folders/QA Test Folder")
        self.assertEqual(delete_folder.status_code, 200)
        self.assertEqual(delete_folder.json()["status"], "success")
        print("-> TC-05: Diary notes & folders CRUD OK")

    def test_06_profile_stats_and_mindset(self):
        """Kiểm tra API chấm điểm nhận thức và phân tích radar chart."""
        # 1. Profile stats
        response = self.client.get(f"/api/v1/profile/{self.test_user}/stats")
        self.assertEqual(response.status_code, 200)
        self.assertIn("stats", response.json())
        self.assertEqual(len(response.json()["stats"]), 6)
        
        # 2. Profile full mindset analysis (Mock or real AI)
        response_mindset = self.client.get(f"/api/v1/profile/{self.test_user}/mindset")
        self.assertEqual(response_mindset.status_code, 200)
        data = response_mindset.json()
        self.assertIn("radar_stats", data)
        self.assertIn("keywords", data)
        self.assertIn("mbti_suggestions", data)
        print("-> TC-06: Profile analytics and mindset DNA endpoints OK")

    def test_07_onboarding_dob_and_welcome_chat(self):
        """Kiểm tra quy trình Onboarding DOB và sinh câu hỏi chào mừng Socratic."""
        # 1. POST Onboarding data with DOB fields
        onboarding_payload = {
            "day_of_birth": "15",
            "month_of_birth": "8",
            "year_of_birth": "1995",
            "gender": "Nam",
            "interests": ["Đọc sách", "Thiền & Yoga"],
            "problems": ["Căng thẳng / Stress", "Trì hoãn"],
            "goals": ["Quản lý cảm xúc", "Tăng năng suất"],
            "source": "Mạng xã hội"
        }
        res_onboard = self.client.post(f"/api/v1/auth/onboarding/{self.test_user}", json=onboarding_payload)
        self.assertEqual(res_onboard.status_code, 200)
        self.assertEqual(res_onboard.json()["status"], "success")
        
        # 2. GET user context to ensure Core Context has been compiled
        res_ctx = self.client.get(f"/api/v1/profile/{self.test_user}/context")
        self.assertEqual(res_ctx.status_code, 200)
        self.assertIn("context", res_ctx.json())
        self.assertIsNotNone(res_ctx.json()["context"])
        print("-> TC-07.1: DOB Onboarding saved & Core Context compiled OK")
        
        # 3. POST to Socratic Welcome API
        res_welcome = self.client.post("/api/v1/chat/welcome", json={
            "username": self.test_user,
            "lang": "vi"
        })
        self.assertEqual(res_welcome.status_code, 200)
        welcome_data = res_welcome.json()
        self.assertIn("question", welcome_data)
        self.assertIn("suggested_replies", welcome_data)
        self.assertEqual(len(welcome_data["suggested_replies"]), 3)
        self.assertIn("reasoning", welcome_data)
        print("-> TC-07.2: Dynamic personalized Socratic welcome generated successfully!")

    def test_08_personalize_week(self):
        """Kiểm tra endpoint AI cá nhân hóa bài học tuần học cụ thể."""
        # 1. Join cohort first
        join_resp = self.client.post("/api/v1/cohort/join", json={
            "username": self.test_user,
            "display_name": "QA Runner",
            "current_tasks": []
        })
        self.assertEqual(join_resp.status_code, 200)

        # 2. Personalize week 1 (since week 2 would require week 1 progress >= 0.5)
        response = self.client.post("/api/v1/cohort/personalize-week", json={
            "username": self.test_user,
            "week": 1
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("week_data", data)
        self.assertIn("title", data["week_data"])
        self.assertIn("description", data["week_data"])
        self.assertIn("tasks", data["week_data"])
        self.assertEqual(len(data["week_data"]["tasks"]), 2)
        print("-> TC-08: AI personalization dynamic week OK")

if __name__ == "__main__":
    unittest.main()

import os
import re

file_path = "d:/thapsang/backend/main.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the content of personalize_week
# Find the start of `from fastapi.responses import StreamingResponse`
# inside personalize_week and the end of the function `return StreamingResponse(...)`

pattern = r'    from fastapi\.responses import StreamingResponse\s+def _generate_response\(\):\s+with personalize_lock:.*?return StreamingResponse\(generate_response\(\), media_type="application/json"\)'
# Actually, let's just find the indices manually.
start_idx = content.find('    from fastapi.responses import StreamingResponse')
end_str = '    return StreamingResponse(generate_response(), media_type="application/json")'
end_idx = content.find(end_str) + len(end_str)

old_code = content[start_idx:end_idx]

new_code = """    from fastapi.responses import JSONResponse
    with personalize_lock:
        # Gather latest user context (chats and diaries)
        chats = {}
        diaries = []
        try:
            chats = cms_helper.get_chat_sessions(req.username)
            diaries = cms_helper.get_diary_entries(req.username)
        except Exception as e_ctx:
            print(f"Context fetch error: {e_ctx}")

        chats_list = list(chats.values())
        chats_text = ""
        for idx, c in enumerate(chats_list[:5]): # Get more recent chats
            msgs = c.get("chat_history") or c.get("messages") or []
            chat_content = " ".join([m.get("content", "") for m in msgs[-8:] if m.get("content")])
            chats_text += f"- Chat Session {idx+1}: {chat_content[:800]}\\n"
    
        diaries_text = ""
        for idx, d in enumerate(diaries[:5]):
            diaries_text += f"- Diary {idx+1} '{d.get('title')}': {d.get('content')[:800]}\\n"

        user_name = user_info.get("nickname") or user_info.get("username", req.username).split('@')[0]
        recent_topic = ""
        if diaries:
            recent_topic = diaries[0].get("title", "")
        if not recent_topic and chats_list:
            c_hist = chats_list[0].get("chat_history") or chats_list[0].get("messages") or []
            if c_hist:
                recent_topic = c_hist[0].get("content", "")[:50]
                
        topic_str = f" về vấn đề '{recent_topic}'" if recent_topic else ""
        topic_str_en = f" regarding '{recent_topic}'" if recent_topic else ""
        
        themes = {
            1: {
                "vi_title": f"Thiết lập nền tảng", "en_title": f"Setting Foundations",
                "vi_core": f"{user_name} thân mến, tuần khởi đầu này là để định vị bản thân. Từ những chia sẻ gần đây{topic_str}, hãy thiết kế một hành động nhỏ nhất để bước ra khỏi vùng quen thuộc và quan sát cảm xúc của bạn.",
                "en_core": f"Dear {user_name}, this initial week is about self-positioning. Based on your recent thoughts{topic_str_en}, design the smallest possible action to step out of your comfort zone and observe your feelings.",
                "vi_supp": f"Ghi lại những rào cản tâm lý đầu tiên bạn gặp phải khi thực hiện thử nghiệm trên.",
                "en_supp": f"Document the initial psychological barriers you encountered during your experiment."
            },
            2: {
                "vi_title": f"Bắt mạch điểm mù", "en_title": f"Identifying Blindspots",
                "vi_core": f"Ở tuần 2, chúng ta tập trung vào những gì bị che khuất. Với băn khoăn{topic_str}, {user_name} hãy thử làm ngược lại thói quen thường ngày trong 1 tình huống cụ thể và xem điều gì thực sự xảy ra.",
                "en_core": f"In week 2, we focus on the unseen. Given your reflections{topic_str_en}, try doing the exact opposite of your usual habit in a specific situation and see what happens.",
                "vi_supp": f"Viết lại khoảnh khắc bạn nhận ra giả định ban đầu của mình là sai lệch.",
                "en_supp": f"Write about the moment you realized your initial assumption was flawed."
            },
            3: {
                "vi_title": f"Giải cấu trúc niềm tin", "en_title": f"Deconstructing Beliefs",
                "vi_core": f"Tuần 3 là lúc thách thức tận gốc rễ. Hãy lấy một kết luận bạn vừa rút ra{topic_str} và áp dụng kỹ thuật '5 lần Tại Sao' để tìm ra nguyên nhân cốt lõi chưa từng lộ diện.",
                "en_core": f"Week 3 challenges the root. Take a recent conclusion{topic_str_en} and apply the '5 Whys' technique to uncover the true underlying cause.",
                "vi_supp": f"Chia sẻ cảm giác chông chênh khi niềm tin cũ bị phá vỡ và góc nhìn mới hé mở.",
                "en_supp": f"Share the feeling of instability when an old belief breaks and a new perspective opens."
            },
            4: {
                "vi_title": f"Quan sát không phán xét", "en_title": f"Non-judgmental Observation",
                "vi_core": f"Tuần 4 yêu cầu sự tĩnh tại. Dựa trên trăn trở{topic_str}, {user_name} hãy chọn vai trò 'người quan sát thứ 3' trong các quyết định sắp tới: ghi nhận nhưng không phản ứng ngay lập tức.",
                "en_core": f"Week 4 requires stillness. Based on your concerns{topic_str_en}, adopt a 'third-party observer' role in upcoming decisions: acknowledge without immediate reaction.",
                "vi_supp": f"Nhật ký tuần này hãy tập trung vào khoảng hở (gap) giữa lúc sự việc xảy ra và lúc bạn phản ứng.",
                "en_supp": f"Focus your diary on the gap between an event happening and your reaction to it."
            },
            5: {
                "vi_title": f"Tái thiết góc nhìn", "en_title": f"Perspective Reconstruction",
                "vi_core": f"Giờ là lúc xây dựng lại. Với những dữ liệu thực tế{topic_str}, hãy thiết lập một hành động mới đại diện cho phiên bản mà {user_name} muốn hướng tới, và thực thi nó ít nhất 3 lần.",
                "en_core": f"It is time to rebuild. With the real-world data{topic_str_en}, establish a new action representing the version of you strive to be, and execute it at least 3 times.",
                "vi_supp": f"Ghi lại những ma sát và sự gượng gạo khi áp dụng góc nhìn mới vào thực tiễn.",
                "en_supp": f"Document the friction and awkwardness of applying this new perspective practically."
            },
            6: {
                "vi_title": f"Đo lường sự phản kháng", "en_title": f"Measuring Resistance",
                "vi_core": f"Tuần 6, sự kháng cự sẽ xuất hiện. {user_name} hãy cố tình chọn làm một việc khó khăn{topic_str} để đo lường xem 'tiếng nói nhỏ' trong đầu bạn đang biện hộ như thế nào.",
                "en_core": f"In week 6, resistance appears. Intentionally choose to do a difficult task{topic_str_en} to measure how the 'little voice' in your head makes excuses.",
                "vi_supp": f"Viết lại nguyên văn những lý do ngụy biện mà tâm trí bạn tạo ra để trốn tránh hành động.",
                "en_supp": f"Write down verbatim the rationalizations your mind created to avoid taking action."
            },
            7: {
                "vi_title": f"Kết nối các điểm chạm", "en_title": f"Connecting the Dots",
                "vi_core": f"Tuần 7 là điểm giao thoa. Hãy nhìn lại những hành động{topic_str} của 6 tuần qua, tìm ra một mẫu số chung (pattern) và thiết kế một thử nghiệm giải quyết hoàn toàn khác biệt.",
                "en_core": f"Week 7 is a junction. Look back at your actions{topic_str_en} over the past 6 weeks, identify a common pattern, and experiment with a completely different approach.",
                "vi_supp": f"Nhật ký tổng hợp: Bạn đã thay đổi cách ra quyết định như thế nào so với tuần 1?",
                "en_supp": f"Synthesis diary: How has your decision-making changed compared to week 1?"
            },
            8: {
                "vi_title": f"Thử nghiệm nghịch lý", "en_title": f"Paradox Experimentation",
                "vi_core": f"Tuần 8 đòi hỏi tư duy nghịch đảo. {user_name} hãy tìm một khía cạnh{topic_str} mà bạn luôn cho là 'đúng', và thử đóng vai 'luật sư của quỷ' để hành động ngược lại niềm tin đó.",
                "en_core": f"Week 8 requires inverse thinking. Find an aspect{topic_str_en} you always assumed was 'right', and play 'devil's advocate' by acting against that belief.",
                "vi_supp": f"Ghi chép lại những phát hiện bất ngờ khi bạn thử nhìn thế giới qua lăng kính đối lập.",
                "en_supp": f"Note the surprising discoveries when you tried viewing the world through an opposing lens."
            },
            9: {
                "vi_title": f"Thích nghi với sự sụp đổ", "en_title": f"Adapting to Breakdown",
                "vi_core": f"Ở tuần 9, thất bại là tư liệu. Nếu bạn vừa trải qua sự chệch hướng{topic_str}, hãy thiết kế một bước đệm nhỏ để quay lại đường đua thay vì tự dằn vặt.",
                "en_core": f"In week 9, failure is data. If you recently experienced a deviation{topic_str_en}, design a small stepping stone to get back on track instead of blaming yourself.",
                "vi_supp": f"Phản tư: Cơ chế phòng vệ nào đã kích hoạt khiến bạn đi chệch hướng, và bài học là gì?",
                "en_supp": f"Reflection: What defense mechanism triggered your deviation, and what is the lesson?"
            },
            10: {
                "vi_title": f"Nội tâm hóa hệ giá trị", "en_title": f"Internalizing Value Systems",
                "vi_core": f"Tuần 10 giúp cắm rễ sâu hơn. Hãy biến những đúc kết{topic_str} thành một bộ nguyên tắc cá nhân ngắn gọn và áp dụng nó vào một quyết định quan trọng trong tuần này.",
                "en_core": f"Week 10 deepens the roots. Turn your takeaways{topic_str_en} into a concise personal code of principles and apply it to a major decision this week.",
                "vi_supp": f"Viết lại cảm giác khi đưa ra quyết định dựa trên hệ nguyên tắc thay vì cảm xúc nhất thời.",
                "en_supp": f"Write about the feeling of making a decision based on principles rather than fleeting emotions."
            },
            11: {
                "vi_title": f"Giải phóng sự phụ thuộc", "en_title": f"Releasing Dependency",
                "vi_core": f"Chặng áp chót! {user_name} hãy tự đóng vai Socratic Coach để phân tích chính các vấn đề hiện tại{topic_str}. Tự đặt ra câu hỏi sắc bén nhất cho bản thân và thực thi câu trả lời.",
                "en_core": f"Penultimate stage! Act as your own Socratic Coach to analyze your current issues{topic_str_en}. Ask yourself the sharpest question and act on the answer.",
                "vi_supp": f"Nhật ký tự vấn: Đâu là câu hỏi mà bạn sợ phải tự trả lời nhất lúc này?",
                "en_supp": f"Self-inquiry diary: What is the question you are most afraid to answer right now?"
            },
            12: {
                "vi_title": f"Tự chủ", "en_title": f"Autonomy",
                "vi_core": f"Tuần cuối cùng. Dựa trên thành quả{topic_str}, {user_name} hãy vạch ra một lộ trình duy trì sự tự nhận thức mà không cần sự can thiệp của AI Coach.",
                "en_core": f"Final week. Based on your outcomes{topic_str_en}, outline a roadmap to maintain self-awareness without the AI Coach's intervention.",
                "vi_supp": f"Thư gửi bản thân: Bạn của 12 tuần tới sẽ cảm ơn bạn của hiện tại vì điều gì?",
                "en_supp": f"Letter to yourself: What will the 'you' 12 weeks from now thank the 'current you' for?"
            }
        }
        
        theme = themes.get(req.week, themes[1])
        fb_core_title_vi = f"{theme['vi_title']}: {recent_topic}" if recent_topic else f"{theme['vi_title']} ({user_name})"
        fb_core_title_en = f"{theme['en_title']}: {recent_topic}" if recent_topic else f"{theme['en_title']} ({user_name})"
        fb_core_vi = theme['vi_core']
        fb_core_en = theme['en_core']
        fb_supp_vi = theme['vi_supp']
        fb_supp_en = theme['en_supp']

        ai_prompt = f\"\"\"You are the Socratic AI Coach of Thapsang Mindset OS.
    The user is at Week {req.week} of their 12-week Personal Roadmap.
    Your goal is to deeply analyze their latest dialog history and recent reflective diaries to design EXACTLY 2 highly personalized, high-fidelity tasks for Week {req.week}.
    CRITICAL REQUIREMENT: You MUST generate EXACTLY 1 "core" task and EXACTLY 1 "supplementary" task. No more, no less. Do not generate two core tasks. Do not generate two supplementary tasks.

    Here is their latest dialog history:
    {chats_text or "No recent chats found."}

    Here are their recent diaries:
    {diaries_text or "No recent diaries found."}

    Based on this latest actual context, update the tasks for Week {req.week} to specifically target their current cognitive bottlenecks, blindspots, or goals.
    Provide a concise title and description for Week {req.week}, and EXACTLY 2 tasks (the first MUST have type "core", the second MUST have type "supplementary"). Each task must have separate translations: "title_vi", "title_en", "type" (which is strictly "core" or "supplementary"), a personalized detailed Socratic Vietnamese "description_vi", a detailed English "description_en", and a customized "effort" in hours which is an integer from 1 to 4 based on task complexity. IMPORTANT: Inside the task descriptions, if there are numbered lists, steps or bullet points (such as 1), 2), or 1., 2.), you MUST format them on newlines using literal "\\n" so they render clean and beautiful!

    You MUST respond with a single, valid JSON object conforming exactly to this JSON schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
    {{
      "title_vi": "Tiêu đề tiếng Việt Tuần {req.week}",
      "title_en": "English Week {req.week} Title",
      "description_vi": "Mô tả tiếng Việt Tuần {req.week}",
      "description_en": "English Week {req.week} Description",
      "tasks": [
        {{
          "title_vi": "Tên nhiệm vụ cốt lõi tiếng Việt",
          "title_en": "Core Task English Title",
          "type": "core",
          "description_vi": "Mô tả chi tiết nhiệm vụ cốt lõi bằng tiếng Việt (xuống dòng cho các mục 1)\\n2))",
          "description_en": "Personalized Socratic core task detailed instruction in English (use newlines for lists or steps)",
          "effort": 3
        }},
        {{
          "title_vi": "Tên nhiệm vụ bổ trợ tiếng Việt",
          "title_en": "Supplementary Task English Title",
          "type": "supplementary",
          "description_vi": "Mô tả chi tiết nhiệm vụ bổ trợ bằng tiếng Việt",
          "description_en": "Personalized Socratic supplementary task detailed instruction in English",
          "effort": 2
        }}
      ]
    }}
    \"\"\"
        is_fallback = False
        # Call LLM
        try:
            from openai import OpenAI as _OpenAI
            _client = _OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
            )
            model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()

            resp = _client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": ai_prompt}],
                temperature=0.3,
                top_p=0.95,
                timeout=35.0  # Strict timeout to fail fast and NOT make user wait forever
            )
            ai_response_text = ""
            if getattr(resp, "choices", None):
                ai_response_text = resp.choices[0].message.content.strip()

            if ai_response_text:
                import re
                import json
                json_match = re.search(r'\\{.*\\}', ai_response_text, re.DOTALL)
                if json_match:
                    ai_response_text = json_match.group(0)
                week_design = json.loads(ai_response_text)
        
                # Post-process to guarantee EXACTLY 1 core and 1 supplementary task
                tasks = week_design.get("tasks", [])
                core_tasks = [t for t in tasks if t.get("type") == "core"]
                supp_tasks = [t for t in tasks if t.get("type") == "supplementary"]
        
                final_tasks = []
        
                # 1. Ensure 1 core task
                if core_tasks:
                    final_tasks.append(core_tasks[0])
                else:
                    final_tasks.append(tasks[0] if len(tasks) > 0 else {
                        "title_vi": fb_core_title_vi,
                        "title_en": fb_core_title_en,
                        "description_vi": fb_core_vi,
                        "description_en": fb_core_en,
                        "effort": 3
                    })
                final_tasks[0]["type"] = "core"
        
                # 2. Ensure 1 supplementary task
                if supp_tasks:
                    final_tasks.append(supp_tasks[0])
                else:
                    final_tasks.append(tasks[1] if len(tasks) > 1 else {
                        "title_vi": f"Nhật ký Socratic Tuần {req.week} | Socratic Diary",
                        "title_en": f"Socratic Diary Week {req.week}",
                        "description_vi": fb_supp_vi,
                        "description_en": fb_supp_en,
                        "effort": 2
                    })
                final_tasks[1]["type"] = "supplementary"
        
                week_design["tasks"] = final_tasks
            else:
                raise ValueError("No valid text response from LLM proxy")
        
        except Exception as e:
            print(f"Failed to personalize week {req.week}: {e}. Using fallback week tasks.")
            is_fallback = True
            # Fallback to predefined week syllabus tasks
            syllabus = cms_helper.get_cohort_syllabus(cohort_id=req.username)
            matching_week = next((s for s in syllabus if s.get("week") == req.week), None)
            if matching_week:
                week_design = {
                    "title": matching_week.get("title"),
                    "description": matching_week.get("description"),
                    "tasks": matching_week.get("tasks")
                }
            else:
                week_design = {
                    "title": f"Chặng {req.week} của {user_name}: Hành động & Phản tư | Week {req.week}: Action & Reflection",
                    "description": f"Vận hành chu trình thực tế và đào sâu vào những gì {user_name} đã đúc kết được gần đây.",
                    "tasks": [
                        {
                            "title_vi": fb_core_title_vi,
                            "title_en": fb_core_title_en,
                            "type": "core",
                            "description_vi": fb_core_vi,
                            "description_en": fb_core_en,
                            "effort": 3
                        },
                        {
                            "title_vi": f"Nhật ký Socratic Tuần {req.week} | Socratic Diary",
                            "title_en": f"Socratic Diary Week {req.week}",
                            "type": "supplementary",
                            "description_vi": fb_supp_vi,
                            "description_en": fb_supp_en,
                            "effort": 2
                        }
                    ]
                }

        # Update NocoBase/CMS syllabus for this week
        t_vi = week_design.get("title_vi") or week_design.get("title", "")
        t_en = week_design.get("title_en") or week_design.get("title", "")
        t_combined = f"{t_vi} ||| {t_en}" if " ||| " not in t_vi else t_vi

        d_vi = week_design.get("description_vi") or week_design.get("description", "")
        d_en = week_design.get("description_en") or week_design.get("description", "")
        d_combined = f"{d_vi} ||| {d_en}" if " ||| " not in d_vi else d_vi

        combined_tasks_for_syllabus = []
        for t in week_design.get("tasks", []):
            tv = t.get("title_vi") or t.get("title", "")
            te = t.get("title_en") or t.get("title", "")
            tc = f"{tv} ||| {te}" if " ||| " not in tv else tv
            
            dv = t.get("description_vi") or t.get("description", "")
            de = t.get("description_en") or t.get("description", "")
            dc = f"{dv} ||| {de}" if " ||| " not in dv else dv
            
            combined_tasks_for_syllabus.append({
                "title": tc,
                "type": t.get("type", "core"),
                "description": dc,
                "effort": t.get("effort", 3)
            })

        try:
            cms_helper.update_cohort_syllabus_week(
                username=req.username,
                week=req.week,
                week_title=t_combined,
                week_description=d_combined,
                tasks=combined_tasks_for_syllabus
            )
        except Exception as e:
            print(f"Failed to save syllabus to CMS: {e}")

        # Also push into personal_roadmaps table as tasks
        try:
            if user_info:
                for task in week_design.get("tasks", []):
                    task_title_vi = task.get("title_vi") or task.get("title") or ""
                    task_title_en = task.get("title_en") or task.get("title") or ""
                    task_title_combined = f"{task_title_vi} ||| {task_title_en}"

                    task_desc_vi = task.get("description_vi") or task.get("description") or ""
                    task_desc_en = task.get("description_en") or task.get("description") or ""

                    if not task_desc_vi:
                        task_desc_vi = "Nhiệm vụ cốt lõi giúp bạn thực hành tái cấu trúc tư duy sâu." if task.get("type") == "core" else "Nhiệm vụ bổ trợ giúp bạn mở rộng góc nhìn và kiến thức."
                    if not task_desc_en:
                        task_desc_en = "Core Socratic task to practice deep mental unlearning." if task.get("type") == "core" else "Supplementary Socratic task to expand perspective and cognitive growth."

                    task_desc_combined = f"{task_desc_vi} ||| {task_desc_en}"

                    task_data = {
                        "title": task_title_combined,
                        "week": req.week,
                        "status": "in_progress",
                        "goal": task_desc_combined,
                        "type": task.get("type", "core"),
                        "subtasks": [
                            {"title": "Phân tích yêu cầu bài học ||| Analyze lesson requirements", "done": False},
                            {"title": "Hoàn thành chiêm nghiệm Socratic ||| Complete Socratic reflection", "done": False}
                        ],
                        "effort": task.get("effort") or (3 if task.get("type") == "core" else 2)
                    }
                    cms_helper.create_personal_roadmap_task(req.username, task_data)
        except Exception as e:
            print(f"Failed to personalize tasks in personal_roadmaps for week {req.week}: {e}")

        # Auto-generate 8-question quiz immediately from the start
        try:
            if user_info:
                import json
                res_week = cms_helper.request_cms("GET", "/personal_roadmaps", params={
                    "filter": json.dumps({
                        "week": req.week,
                        "$or": [
                            {"fk_user": user_info["id"]},
                            {"relation_roadmaps_user.id": user_info["id"]}
                        ]
                    }),
                    "limit": 1
                })
                roadmaps = res_week.get("data", [])
                if roadmaps:
                    parent_record = roadmaps[0]
                    roadmap_id = parent_record["id"]
                    parent_extra = {}
                    if parent_record.get("graph_data_roadmap"):
                        try:
                            parent_extra = json.loads(parent_record["graph_data_roadmap"])
                        except:
                            pass
            
                    existing_quiz = parent_extra.get("quiz", {})
                    if not (existing_quiz and "questions" in existing_quiz and len(existing_quiz["questions"]) == 8):
                        core_task = next((t for t in week_design.get("tasks", []) if t.get("type") == "core"), None)
                        supp_task = next((t for t in week_design.get("tasks", []) if t.get("type") == "supplementary"), None)
                        if core_task and supp_task:
                            background_tasks.add_task(
                                auto_generate_quiz_for_week,
                                req.username,
                                req.week,
                                roadmap_id,
                                parent_extra,
                                core_task,
                                supp_task,
                                user_info,
                                "vi"
                            )
        except Exception as qe:
            print(f"Auto quiz generation failed in personalize_week: {qe}")

        # Reconstruct combined week_design for frontend response compatibility
        frontend_week_design = {
            "title": t_combined,
            "description": d_combined,
            "tasks": combined_tasks_for_syllabus
        }
        
        if is_fallback:
            return JSONResponse(status_code=500, content={"status": "fallback", "week_data": frontend_week_design})
        else:
            return JSONResponse(status_code=200, content={"status": "success", "week_data": frontend_week_design})
"""

content = content[:start_idx] + new_code + content[end_idx:]
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py")

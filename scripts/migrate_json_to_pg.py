"""
Therapity — JSON to PostgreSQL Migration Script
Migrates all data from the old JSON-based storage to PostgreSQL.
Passwords are hashed with bcrypt during migration.

Usage: python scripts/migrate_json_to_pg.py [--dry-run]
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.diary import DiaryEntry, DiaryFolder
from app.models.task import Task
from app.models.aoa import AOAPost, AOAComment, AOALike
from app.models.cohort import CohortMember, PersonalRoadmap
from app.services.auth_service import hash_password

# Paths
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'database')
THAPSANG_DB = os.path.join(DATABASE_DIR, 'thapsang_db.json')
AOA_DB = os.path.join(DATABASE_DIR, 'aoa_db.json')
COHORT_DB = os.path.join(DATABASE_DIR, 'cohort_db.json')
AOA_LIKES = os.path.join(DATABASE_DIR, 'aoa_likes.json')


def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return default
    return default


def migrate(db_url: str, dry_run: bool = False):
    print(f"{'[DRY RUN] ' if dry_run else ''}Starting migration...")
    print(f"Database URL: {db_url}")

    engine = create_engine(db_url)

    if not dry_run:
        Base.metadata.create_all(engine)
        print("✅ Tables created")

    with Session(engine) as db:
        # === 1. Migrate Users ===
        ts_data = load_json(THAPSANG_DB)
        accounts = ts_data.get('_accounts', {})
        profiles = ts_data.get('_profiles', {})
        user_id_map = {}  # username -> UUID

        print(f"\n📦 Migrating {len(accounts)} users...")
        for username, password in accounts.items():
            profile = profiles.get(username, {})

            user = User(
                username=username,
                email=profile.get('email', f'{username}@therapity.local'),
                password_hash=hash_password(password),  # 🔐 Hash plaintext passwords!
                display_name=profile.get('displayName', username),
                bio=(profile.get('bio', '') or '').replace('Thapsang', 'Therapity'),
                avatar=profile.get('avatar_url') or profile.get('avatar', ''),
                banner=profile.get('banner_url') or profile.get('banner', ''),
                following_list=profile.get('following_list', []),
                onboarding=profile.get('onboarding', {}),
                onboarded=profile.get('onboarded', False),
            )

            if not dry_run:
                db.add(user)
                db.flush()
                user_id_map[username] = user.id
            else:
                fake_id = uuid.uuid4()
                user_id_map[username] = fake_id
            print(f"  ✅ User: {username} (password hashed)")

        # === 2. Migrate Chat Sessions ===
        session_keys = [k for k in ts_data.keys() if k not in ('_accounts', '_profiles', '_diaries', '_folders')]
        print(f"\n💬 Migrating {len(session_keys)} chat sessions...")
        for session_key in session_keys:
            session_data = ts_data[session_key]
            if not isinstance(session_data, dict):
                continue
            username = session_data.get('username')
            if not username or username not in user_id_map:
                continue

            session = ChatSession(
                user_id=user_id_map[username],
                custom_title=session_data.get('custom_title'),
                chat_history=session_data.get('chat_history', []),
                graph_data=session_data.get('graph_data', {}),
                tasks=session_data.get('tasks', []),
                suggested_replies=session_data.get('suggested_replies', []),
                token_used=session_data.get('token_used', 0),
                model_used=session_data.get('model_used'),
                voice=session_data.get('voice'),
            )
            if not dry_run:
                db.add(session)

        # === 3. Migrate Diary Entries ===
        diaries = ts_data.get('_diaries', {})
        total_entries = sum(len(entries) for entries in diaries.values())
        print(f"\n📝 Migrating {total_entries} diary entries...")
        for username, entries in diaries.items():
            if username not in user_id_map:
                continue
            for entry in entries:
                diary = DiaryEntry(
                    user_id=user_id_map[username],
                    title=entry.get('title', ''),
                    content=entry.get('content', ''),
                    ai_insight=entry.get('ai_insight', ''),
                    mood=entry.get('mood', 'Calm'),
                    folder=entry.get('folder', ''),
                    date=entry.get('date'),
                )
                if not dry_run:
                    db.add(diary)

        # === 4. Migrate Diary Folders ===
        folders = ts_data.get('_folders', {})
        print(f"\n📂 Migrating diary folders...")
        for username, folder_list in folders.items():
            if username not in user_id_map:
                continue
            for folder_name in folder_list:
                folder = DiaryFolder(
                    user_id=user_id_map[username],
                    name=folder_name,
                )
                if not dry_run:
                    db.add(folder)

        # === 5. Migrate Tasks ===
        print(f"\n✅ Migrating tasks...")
        for username, profile in profiles.items():
            if username not in user_id_map:
                continue
            tasks_list = profile.get('tasks', [])
            for t in tasks_list:
                task = Task(
                    user_id=user_id_map[username],
                    title=t.get('title', ''),
                    goal=t.get('goal', ''),
                    status=t.get('status', 'backlog'),
                    deadline=t.get('deadline', ''),
                    effort=t.get('effort', 1),
                    subtasks=t.get('subtasks', []),
                    context_link=t.get('context_link', ''),
                    feedback=t.get('feedback'),
                    source=t.get('source', 'manual'),
                )
                if not dry_run:
                    db.add(task)

        # === 6. Migrate AOA Posts ===
        aoa_data = load_json(AOA_DB, {"posts": []})
        posts = aoa_data.get('posts', [])
        post_id_map = {}  # old_id -> new_uuid
        print(f"\n🌐 Migrating {len(posts)} AOA posts...")

        for p in posts:
            author_name = p.get('author_name', '')
            if author_name not in user_id_map:
                # Create a placeholder user for unknown authors
                if author_name and author_name not in user_id_map:
                    placeholder = User(
                        username=author_name,
                        email=f'{author_name}@therapity.local',
                        password_hash=hash_password('placeholder123'),
                        display_name=author_name,
                    )
                    if not dry_run:
                        db.add(placeholder)
                        db.flush()
                        user_id_map[author_name] = placeholder.id
                    else:
                        user_id_map[author_name] = uuid.uuid4()

            post = AOAPost(
                author_id=user_id_map.get(author_name, user_id_map.get(list(user_id_map.keys())[0] if user_id_map else 'user')),
                content=(p.get('content', '') or '').replace('ThapsangOS', 'TherapityOS').replace('Thapsang', 'Therapity'),
                graph_data=p.get('graph_data', {}),
                likes_count=p.get('likes', 0),
                shares_count=p.get('shares', 0),
                privacy=p.get('post_privacy', 'public'),
                status=p.get('post_status', 'active'),
            )
            if not dry_run:
                db.add(post)
                db.flush()
                post_id_map[p.get('id', '')] = post.id
            else:
                post_id_map[p.get('id', '')] = uuid.uuid4()

            # Comments
            for c in p.get('comments', []):
                c_author = c.get('author_name', author_name)
                if c_author not in user_id_map:
                    user_id_map[c_author] = uuid.uuid4()

                comment = AOAComment(
                    post_id=post_id_map[p.get('id', '')],
                    author_id=user_id_map.get(c_author, user_id_map[author_name]),
                    content=c.get('content', ''),
                )
                if not dry_run:
                    db.add(comment)

        # === 7. Migrate Cohort Members ===
        cohort_data = load_json(COHORT_DB, {"members": [], "syllabus": []})
        members = cohort_data.get('members', [])
        print(f"\n🎓 Migrating {len(members)} cohort members...")

        for m in members:
            m_username = m.get('username', '')
            if m_username not in user_id_map:
                continue
            member = CohortMember(
                user_id=user_id_map[m_username],
                display_name=m.get('display_name', ''),
                week_progress=m.get('week_progress', {}),
                buddy=m.get('buddy'),
                is_self=m.get('is_self', False),
            )
            if not dry_run:
                db.add(member)

        # === Commit ===
        if not dry_run:
            db.commit()
            print(f"\n🎉 Migration complete! All data committed to PostgreSQL.")
        else:
            print(f"\n🔍 Dry run complete. No data was written.")

        # Summary
        print(f"\n📊 Migration Summary:")
        print(f"   Users: {len(accounts)}")
        print(f"   Chat Sessions: {len(session_keys)}")
        print(f"   Diary Entries: {total_entries}")
        print(f"   AOA Posts: {len(posts)}")
        print(f"   Cohort Members: {len(members)}")
        print(f"   ⚠️  All passwords have been bcrypt-hashed during migration")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate Therapity data from JSON to PostgreSQL')
    parser.add_argument('--dry-run', action='store_true', help='Preview migration without writing data')
    parser.add_argument('--db-url', default='postgresql://therapity:therapity_dev@localhost:5432/therapity',
                        help='PostgreSQL connection URL')
    args = parser.parse_args()

    migrate(args.db_url, dry_run=args.dry_run)

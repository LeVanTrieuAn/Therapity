# Therapity

**AI-Powered Cognitive Mindset Operating System**

> Kiến tạo bản đồ tư duy & Phản chiếu tri thức

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 + Vite + TailwindCSS v4 |
| **Backend** | FastAPI + SQLAlchemy (async) |
| **Database** | PostgreSQL 16 |
| **Auth** | bcrypt + JWT (access + refresh tokens) |
| **AI** | OpenAI-compatible LLM (Socratic Coach) |
| **Infra** | Docker Compose (hot-reload dev) |

## Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your credentials

# 2. Launch (PostgreSQL + Backend + Frontend)
docker compose -f docker-compose.dev.yml up --build

# 3. Migrate old data (optional)
python scripts/migrate_json_to_pg.py --db-url postgresql://therapity:therapity_dev@localhost:5432/therapity

# 4. Access
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Project Structure

```
therapity/
├── backend/
│   └── app/
│       ├── main.py          # App factory
│       ├── config.py         # Environment config
│       ├── database.py       # Async SQLAlchemy
│       ├── models/           # 11 PostgreSQL models
│       ├── routers/          # 7 API routers
│       ├── schemas/          # Pydantic request/response
│       └── services/         # Auth, Email, LLM
├── frontend-react/
│   └── src/
│       ├── components/       # Layout, Sidebar
│       ├── pages/            # Login, Coach, Diary, Tasks, AOA, Cohort
│       ├── store/            # Zustand (auth, theme)
│       └── services/         # API client
├── scripts/
│   └── migrate_json_to_pg.py # JSON → PostgreSQL migration
├── docker-compose.dev.yml    # Dev environment
└── .env.example              # Config template
```

## Theme

| Mode | Background | Accent | Text |
|------|-----------|--------|------|
| Light | `#FFFFFF` | `#16A34A` (Green) | `#111827` (Black) |
| Dark | `#0A0A0F` | `#A855F7` (Purple) | `#F9FAFB` (White) |

## License

Private — All rights reserved.
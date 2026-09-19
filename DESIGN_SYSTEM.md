# Therapity — Design System Documentation

> **Đây là nguồn tham khảo duy nhất (single source of truth) về cách sửa giao diện, chọn màu, sử dụng icon và thư viện mã nguồn mở.**  
> Mọi thay đổi UI phải tuân theo tài liệu này để giữ tính nhất quán.

---

## 1. Triết lý thiết kế (Design Philosophy)

### Hai chủ đề cảm xúc

| Mode | Cảm xúc | Hình ảnh tham chiếu |
|------|---------|---------------------|
| **Light** | Hoàng hôn 18h trên biển cả — dịu dàng, ấm áp, dễ chịu | Bầu trời tím hồng, mặt trời san hô, đại dương phản chiếu |
| **Dark** | Sự sâu thẳm của biển đêm — bí ẩn, tĩnh lặng, sao trời | Midnight navy, sao lấp lánh, ánh bioluminescent |

### Ngôn ngữ hình ảnh
- **Minimalist flat design** — không dùng hình ảnh chân thật (photo-realistic)
- **Vector art / motion graphic** — SVG inline, geometric shapes
- **Taste-skill aesthetic** — geometric celestial symbols, KHÔNG dùng stroke UI icons thông thường
- **Glassmorphism** — backdrop-filter blur, semi-transparent cards

---

## 2. Bảng màu (Color Palette)

### 2.1 CSS Variables — `frontend-react/src/index.css`

Tất cả màu được định nghĩa qua CSS custom properties trong `:root` (light) và `.dark` (dark).  
**KHÔNG hardcode hex trong component**, phải dùng `var(--color-*)`.

```css
/* Light mode tokens */
--color-accent:          #B07FD4   /* Lavender purple — màu chủ đạo */
--color-accent-dark:     #7C3AED   /* Deeper violet */
--color-accent-light:    rgba(201,164,245,0.15)
--color-accent-subtle:   rgba(201,164,245,0.08)

--color-bg-primary:      #FFF7FB   /* Near-white rose tint */
--color-bg-secondary:    #FEF0F8
--color-bg-card:         rgba(255,247,251,0.85)
--color-bg-sidebar:      linear-gradient(180deg,#FEF0F8,#F8E6F6)

--color-text-primary:    #1A0A2E
--color-text-secondary:  #3D1F5E
--color-text-muted:      #8B6FAB

--color-border:          rgba(176,127,212,0.2)
--color-border-subtle:   rgba(176,127,212,0.12)

/* Dark mode tokens */
--color-accent:          #7C3AED
--color-bg-primary:      #0D0B1A   /* Abyss navy */
--color-bg-sidebar:      linear-gradient(180deg,#100A25,#0D0B1A)
--color-text-muted:      #6B5A8A
```

### 2.2 Màu ngữ nghĩa (Semantic Colors)

| Tên | Light | Dark | Dùng cho |
|-----|-------|------|---------|
| Sunset coral | `#FFBFA3` | — | Sun glow, warm highlights |
| Rose horizon | `#F4A8C6` | — | Gradient midpoint |
| Lavender sky | `#C9A4F5` | `#A78BFA` | Stars, constellation |
| Abyss navy | — | `#0D0B1A` | Background dark |
| Midnight violet | — | `#120B2E` | Card bg dark |
| Contradiction | `#F4607E` | `#F87171` | Mâu thuẫn node/edge |
| Connection | `rgba(176,127,212,0.5)` | `rgba(124,58,237,0.5)` | Liên kết edge |

### 2.3 Quy tắc chọn màu khi thêm tính năng mới

```
✅ ĐÚNG:
  - Dùng var(--color-accent) cho primary interactive elements
  - Dùng var(--color-accent-subtle) cho backgrounds nhẹ
  - Contradiction/error → #F4607E (light) / #F87171 (dark)
  - Success → accent color (violet) — KHÔNG dùng màu xanh lá

❌ SAI:
  - Dùng màu xanh lá (#22c55e, #16a34a) làm UI color
  - Dùng màu đỏ thuần (#ef4444, #dc2626) làm error
  - Hardcode màu trắng/đen thay vì var(--color-text-*)
  - Dùng generic gray (#6b7280, #9ca3af)
```

---

## 3. Typography

```css
--font-display: 'Playfair Display', Georgia, serif   /* Headings, brand names */
--font-sans:    'DM Sans', system-ui, sans-serif      /* Body text, UI labels */
```

### Quy tắc dùng font
- `font-display` (Playfair Display): h1, h2, branding, tarot-style labels
- `font-sans` (DM Sans): body, buttons, inputs, labels, tooltips
- **KHÔNG dùng font khác** ngoài hai font trên

---

## 4. Icon System — Taste-Skill Geometric Symbols

> **Quy tắc quan trọng**: KHÔNG dùng icon từ Lucide, Heroicons, FontAwesome, hay bất kỳ icon library nào có stroke-based UI icons. Tất cả biểu tượng phải là **flat geometric / celestial SVG** theo taste-skill aesthetic.

### 4.1 Bộ icon hiện tại (`Sidebar.jsx`)

| Icon | Shape | Dùng cho |
|------|-------|---------|
| `TsIcon.dashboard` | ✦ 4-pointed diamond star | Dashboard / Tổng quan |
| `TsIcon.coach` | ◎ Double circle + eye | Tham vấn / Dialogue |
| `TsIcon.diary` | ☽ Crescent + dots | Nhật ký / Diary |
| `TsIcon.aoa` | ✤ Compass rose (diamond + ring) | Bản tin AOA |
| `TsIcon.tasks` | ○ Ring + checkmark | Nhiệm vụ / Tasks |
| `TsIcon.cohort` | △ Triangle silhouette | Lộ trình / Roadmap |
| `TsIcon.sun` | ☀ Sun rays | Toggle light mode |
| `TsIcon.moon` | ☽ Crescent | Toggle dark mode |

### 4.2 Quy tắc tạo icon mới

```jsx
// Template icon mới — chỉ dùng geometric primitives
const NewIcon = (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
    {/* Chỉ dùng: path, circle, ellipse, polygon, line, rect */}
    {/* KHÔNG dùng: image, text, use (external symbol) */}
    {/* Màu: luôn dùng "currentColor" để inherit từ parent */}
  </svg>
);
```

### 4.3 CSS shape utilities (`index.css`)

```css
.ts-diamond     /* Full-size 4-pointed star via clip-path */
.ts-diamond-sm  /* Small version — dùng làm divider/decorator */
```

---

## 5. Background Images

### 5.1 Files

| File | Theme | Kích thước | Dùng cho |
|------|-------|-----------|---------|
| `/public/sunset_bg.png` | Light | ~386KB | Dashboard, CoachPage background |
| `/public/abyss_bg.png` | Dark | ~352KB | Dashboard, CoachPage background |

### 5.2 CSS Classes (`index.css → @layer utilities`)

```css
.scene-bg-sunset {
  background-image: url('/sunset_bg.png');
  background-size: cover;
  background-position: center 40%;
  background-repeat: no-repeat;
}
.scene-bg-abyss {
  background-image: url('/abyss_bg.png');
  background-size: cover;
  background-position: center 40%;
  background-repeat: no-repeat;
}
```

### 5.3 Cách dùng trong component

```jsx
// Pattern chuẩn cho page có background
<div className="relative overflow-hidden" style={{ borderRadius: '1.25rem' }}>
  {/* Background layer */}
  <div
    className={`absolute inset-0 pointer-events-none ${isDark ? 'scene-bg-abyss' : 'scene-bg-sunset'}`}
    style={{ opacity: isDark ? 0.6 : 0.72, backgroundPosition: 'center 25%' }}
  />
  {/* Gradient fade */}
  <div className="absolute inset-0 pointer-events-none" style={{
    background: isDark
      ? 'linear-gradient(to bottom, transparent 15%, var(--color-bg-primary) 75%)'
      : 'linear-gradient(to bottom, transparent 20%, var(--color-bg-primary) 68%)',
    borderRadius: '1.25rem',
  }}/>
  {/* Content — phải có relative z-10 */}
  <div className="relative z-10">
    {/* ... */}
  </div>
</div>
```

---

## 6. Thư viện mã nguồn mở (Open Source Libraries)

### 6.1 Frontend Dependencies

| Library | Version | Mục đích | Docs |
|---------|---------|---------|------|
| **React** | ^18 | UI framework | https://react.dev |
| **Vite** | ^8.3 | Build tool, HMR | https://vitejs.dev |
| **Framer Motion** | ^11 | Animations, transitions | https://framer.com/motion |
| **React Router DOM** | ^6 | Client-side routing | https://reactrouter.com |
| **Axios** | ^1 | HTTP client | https://axios-http.com |
| **Zustand** | ^4 | State management | https://zustand-demo.pmnd.rs |
| **TailwindCSS** | ^4 | Utility CSS classes | https://tailwindcss.com |

### 6.2 Backend Dependencies

| Library | Version | Mục đích |
|---------|---------|---------|
| **FastAPI** | ^0.110 | API framework |
| **SQLAlchemy** | ^2 | ORM |
| **asyncpg** | ^0.29 | PostgreSQL async driver |
| **python-jose** | ^3 | JWT authentication |
| **httpx** | ^0.27 | HTTP client cho OpenRouter |
| **Pydantic** | ^2 | Data validation |

### 6.3 Infrastructure

| Tool | Mục đích |
|------|---------|
| **Docker + Docker Compose** | Container orchestration |
| **PostgreSQL 15** | Database |
| **OpenRouter API** | LLM gateway (free models) |

### 6.4 Design Resources (Taste-Skill)

- **taste-skill**: https://github.com/leonxlnx/taste-skill
  - Install: `npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"`
  - Dùng cho: design aesthetic guidance, icon language, color sensibility
  - **Không tự động install vào code** — dùng làm tham khảo phong cách

---

## 7. Component Architecture

```
frontend-react/src/
├── components/
│   ├── Layout/
│   │   ├── Sidebar.jsx     ← Navigation + taste-skill icons
│   │   └── AppLayout.jsx   ← Main layout wrapper
│   └── MindMap.jsx         ← Cognitive graph visualization
├── pages/
│   ├── LoginPage.jsx       ← Auth (split layout, tarot animation)
│   ├── DashboardPage.jsx   ← Home (sunset/abyss bg, stat cards)
│   ├── CoachPage.jsx       ← Socratic dialogue + MindMap panel
│   ├── DiaryPage.jsx       ← Journal
│   ├── TasksPage.jsx       ← Task management
│   ├── AOAPage.jsx         ← Community feed
│   └── CohortPage.jsx      ← Learning roadmap
├── store/
│   ├── authStore.js        ← Zustand: user session
│   └── themeStore.js       ← Zustand: theme + language
├── services/
│   └── api.js              ← Axios: all API calls
└── index.css               ← Design system tokens + components
```

---

## 8. Quy tắc sửa giao diện

### 8.1 Thêm màu mới vào design system

```
1. Thêm CSS variable vào :root và .dark trong index.css
2. Đặt tên theo pattern: --color-[category]-[variant]
3. KHÔNG tạo màu độc lập không có biến thể dark
```

### 8.2 Thêm component mới

```
1. Luôn nhận prop isDark (hoặc lấy từ useThemeStore)
2. Sử dụng var(--color-*) cho tất cả màu
3. Animation: dùng Framer Motion, KHÔNG dùng CSS animation riêng
   (trừ @keyframes đã có sẵn trong index.css)
4. Icon: tạo flat geometric SVG, KHÔNG import từ icon library
5. Font: className="font-display" hoặc font-family: var(--font-sans)
```

### 8.3 Thêm page mới

```
1. Copy pattern background từ DashboardPage/CoachPage
2. Thêm route vào App.jsx / router config
3. Thêm nav item vào Sidebar.jsx với TsIcon mới
4. Sử dụng glass-card, tarot-card, btn-primary từ index.css
```

### 8.4 Sửa màu cụ thể

| Muốn sửa | Sửa ở đâu |
|---------|-----------|
| Màu chủ đạo (accent) | `index.css` → `--color-accent` |
| Background sidebar | `index.css` → `.dark .sidebar` |
| Màu node MindMap | `MindMap.jsx` → `PALETTE` object |
| Màu edge MindMap | `MindMap.jsx` → `PALETTE.*.edge` |
| Legend màu | `CoachPage.jsx` → legend section |
| Background ảnh | Thay file `/public/sunset_bg.png` hoặc `abyss_bg.png` |

---

## 9. Quy trình deploy khi thay đổi giao diện

> **Vấn đề**: Docker trên Windows không trigger Vite HMR qua volume mount (inotify không hoạt động).  
> **Giải pháp**: Phải rebuild image sau mỗi lần thay đổi frontend code.

```bash
# Quy trình chuẩn khi sửa code frontend
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml build --no-cache frontend
docker compose -f docker-compose.dev.yml up

# Sau khi up xong, nhấn Ctrl+Shift+R trên trình duyệt (hard refresh)
```

```bash
# Chỉ sửa backend (.env, Python files) — không cần rebuild frontend
docker compose -f docker-compose.dev.yml restart backend
```

---

## 10. LLM Model Configuration

File: `.env`

```env
# Các free model ổn định trên OpenRouter (cập nhật tháng 9/2026)
LLM_MODEL=google/gemma-4-31b-it:free,google/gemma-4-26b-a4b-it:free,meta-llama/llama-3.3-70b-instruct:free
```

**Cách hoạt động**: Backend thử từng model theo thứ tự, nếu fail chuyển sang model tiếp theo (fallback chain).

**Kiểm tra model available**: https://openrouter.ai/models → filter "Free"

---

## 11. MindMap — Graph Data Contract

Backend (`POST /api/v1/chat/mindmap`) trả về:

```json
{
  "nodes": [
    { "id": "n1", "label": "Lo âu công việc", "color": "#16A34A" },
    { "id": "n2", "label": "Tôi không đủ giỏi", "color": "#ffb4ab" }
  ],
  "edges": [
    { "source": "n1", "target": "n2", "label": "gây ra", "is_contradiction": false }
  ],
  "current_step": "kham_pha",
  "focus_node_id": "n2"
}
```

| Field | Giá trị | Ý nghĩa |
|-------|---------|---------|
| `color: #16A34A` | Thought node | Hiển thị: lavender/violet |
| `color: #ffb4ab` | Contradiction node | Hiển thị: rose/red |
| `current_step: kham_pha` | Đang khám phá | Badge: violet |
| `current_step: soi_chieu` | Đang soi chiếu | Badge: rose (pulse) |
| `focus_node_id` | Node đang active | Hiển thị: orbit ring xoay |
| `is_contradiction: true` | Edge mâu thuẫn | Hiển thị: dashed rose |

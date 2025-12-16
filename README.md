# Process Mining Platform

A modern process mining tool powered by PM4Py with a Next.js frontend and FastAPI backend.

## 🚀 Quick Start

### Local Development

**1. Start Backend (Terminal 1):**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Start Frontend (Terminal 2):**
```bash
npm install
npm run dev
```

**3. Open:** http://localhost:3000

---

## 📁 Project Structure

```
process-miner/
├── src/                    # Next.js frontend
│   ├── app/               # Pages (App Router)
│   ├── components/        # React components
│   ├── lib/               # Utilities, API client, stores
│   └── hooks/             # React hooks
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # PM4Py, file handling
│   │   └── models/        # Pydantic schemas
│   └── requirements.txt
└── docker-compose.yml     # Run both services
```

---

## 🌿 Git Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `dev` | Development/staging |
| `feature/*` | New features |
| `fix/*` | Bug fixes |

### Workflow
```bash
# Start a new feature
git checkout dev
git pull origin dev
git checkout -b feature/my-feature

# Work on feature...
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
# Create PR: feature/my-feature → dev

# After review, merge to dev
# When ready for production, merge dev → main
```

---

## 🚀 Deployment (FREE Options)

### Frontend → Vercel (FREE)

1. Go to [vercel.com](https://vercel.com)
2. Connect your GitHub repo
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL` = your backend URL
4. Deploy!

### Backend → Railway (FREE tier: 500 hrs/month)

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Select the `backend` folder as root
4. Set environment variables:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   DEBUG=false
   ```
5. Deploy!

### Alternative: Render (FREE with auto-sleep)

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect repo, select `backend` folder
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🐳 Docker (Optional)

```bash
# Run both services
docker-compose up

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## ⚙️ Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
HOST=0.0.0.0
PORT=8000
DEBUG=true
FRONTEND_URL=http://localhost:3000
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=100
```

---

## 🧪 Testing

```bash
# Frontend type check
npm run type-check

# Backend health check
curl http://localhost:8000/api/health
```

---

## 📚 API Documentation

When backend is running: http://localhost:8000/docs

---

## 🛠️ Tech Stack

- **Frontend:** Next.js 14, React Flow, Zustand, TailwindCSS
- **Backend:** FastAPI, PM4Py, Pandas
- **Deployment:** Vercel (frontend), Railway (backend)

---

## 📄 License

MIT

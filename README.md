<div align="center">

# ✨ IntelScout

**The Next-Generation AI-Powered Competitive Intelligence & Automated Market Scraper**

🔗 **Live Demo:** [https://intel-scout.vercel.app/](https://intel-scout.vercel.app/)

<br/>

![NEXT.JS](https://img.shields.io/badge/NEXT.JS-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FASTAPI](https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PLAYWRIGHT](https://img.shields.io/badge/PLAYWRIGHT-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![NEON](https://img.shields.io/badge/NEON-00E599?style=for-the-badge&logo=neon&logoColor=black)
![PINECONE](https://img.shields.io/badge/PINECONE-000000?style=for-the-badge&logo=pinecone&logoColor=white)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-76B900?style=for-the-badge&logo=nvidia&logoColor=white)

<br/>
<i>IntelScout acts as an automated scout for your business. By leveraging deep web scraping, NLP-driven insights, and predictive modeling, it tracks your rivals in real-time and generates actionable battlecards.</i>

</div>

---

## 📑 Table of Contents
- [Overview](#-overview)
- [Data Science & NLP Pipeline](#-data-science--nlp-pipeline)
- [Architecture](#%EF%B8%8F-architecture)
- [Key Features (V3)](#-key-features-v3)
- [Technology Stack](#%EF%B8%8F-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Deployment](#%EF%B8%8F-deployment)

---

## 📖 Overview

In today's fast-paced market, keeping tabs on competitors is crucial but time-consuming. **IntelScout** automates competitive intelligence. Simply provide a competitor's domain, and IntelScout's scraping engines will traverse their website, extract product positioning, and analyze their marketing copy. The data is processed through **NVIDIA NIM's Llama 3.3** to extract weaknesses, strengths, and predict future market moves.

---

## 🔬 Data Science & NLP Pipeline

At its core, IntelScout is an advanced **Natural Language Processing (NLP)** and **Data Engineering** pipeline. It transforms unstructured web data into structured competitive insights using the following workflow:

1. **Data Collection & ETL:** Playwright operates as a headless crawler, navigating DOM trees and bypassing bot-protections to scrape unstructured text into raw datasets.
2. **Data Cleaning & Chunking:** The raw text is normalized and split into semantically contiguous chunks (tokens).
3. **High-Dimensional Embeddings:** Chunks are passed through NVIDIA's `nv-embedqa-e5-v5` model to generate dense vector embeddings (1024-dimensional arrays).
4. **Vector Space Modeling:** These vectors are stored in **Pinecone**, establishing a high-dimensional vector space. **(V3 Fast-Path Optimized: Database caching reduces vector search load times from 1-2 minutes to < 1.3 seconds).**
5. **Retrieval-Augmented Generation (RAG):** When generating a Battlecard or Insight, the system queries Pinecone using **Cosine Similarity** algorithms to retrieve the exact text chunks relevant to pricing, weaknesses, or market positioning.
6. **V3 Autonomous Multi-Agent Pipeline:**
   - **Agent 1 (Research & Monitoring):** Extracts pricing, features, messaging, and overall Customer Sentiment (Positive/Neutral/Negative) from the raw text.
   - **Agent 2 (Change Detection):** Compares the current snapshot against historical snapshots to detect real business shifts or sentiment drops.
   - **Agent 3 (Strategy Agent):** Drafts an immediate counter-action strategy for executive teams if a High-Threat shift is detected.

---

## 🏗️ Architecture

IntelScout uses a highly decoupled microservice architecture, allowing the AI/Scraping backend to scale independently of the React frontend.

<div align="center">

```mermaid
graph TD
    Client[Client Browser] -->|HTTP / React| NextJS[Next.js Frontend]
    Client -->|Auth| Clerk[Clerk Auth]
    
    NextJS -->|REST API| FastAPI[FastAPI Backend]
    
    FastAPI -->|Playwright| WebScraper[Web Scraper & Crawler]
    FastAPI -->|Multi-Agent Pipeline| NVIDIA[NVIDIA NIM Llama 3.3]
    FastAPI -->|Vectors| Pinecone[(Pinecone Vector DB)]
    FastAPI -->|Data| Neon[(Neon PostgreSQL)]
    FastAPI -->|Push Alerts| Slack[Slack Webhook]
    
    WebScraper -->|Scraped Content| FastAPI
    NVIDIA -->|AI Insights & Battlecards| FastAPI
```

</div>

---

## ✨ Key Features (V3)

1. 🕵️ **V3 Multi-Agent Autonomous Pipeline:** A background cron system that continuously researches, compares, and strategizes against competitors without human intervention.
2. 📉 **V3 Customer Sentiment Detection:** Extracts customer sentiment (Positive, Neutral, Negative) and confidence scores from scattered web context to alert you if a competitor's users are unhappy.
3. 🚨 **V3 Slack Webhook Alerts:** Instantly pushes "High Threat" alerts and counter-strategy recommendations directly to your company's Slack channel.
4. 🧠 **AI-Powered Insights:** Uses advanced LLMs to distill thousands of words of web copy into actionable signals.
5. ⚔️ **Dynamic Battlecards:** Instantly generates comparative battlecards showing SWOT analysis, pricing models, and key differentiators.
6. ⚡ **DB Fast-Path Optimization:** Intelligent caching of raw context locally in PostgreSQL to bypass expensive embedding generation, drastically reducing LLM inference latency.
7. 🎨 **Premium Glassmorphic UI:** A stunning, premium dark-mode interface built with Tailwind CSS and Framer Motion for a native app feel.

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Frontend** | Next.js 14, React, Tailwind CSS | UI Framework & Styling |
| **Animations** | Framer Motion | Fluid micro-interactions |
| **Auth** | Clerk | Secure user authentication |
| **Backend** | FastAPI, Python 3.12, `uv` | High-performance async API |
| **Web Scraping**| Playwright, BeautifulSoup4 | DOM parsing and headless browsing |
| **AI / LLM** | NVIDIA NIM (Llama 3.3) | Multi-Agent NLP Pipeline |
| **Vector DB** | Pinecone | Semantic search & Embeddings |
| **Relational DB**| Neon (PostgreSQL) | Persistent storage |

---

## 📂 Project Structure

```text
IntelScout/
├── frontend/                   # Next.js App Router Client
│   ├── src/app/                # Routes & Pages
│   ├── src/components/         # Reusable UI Components
│   ├── public/                 # Static Assets
│   └── package.json            # Node Dependencies
├── backend/                    # FastAPI Server
│   ├── src/routers/            # API Endpoints
│   ├── src/services/           # AI Multi-Agent Pipeline & Scraping
│   ├── src/tasks/              # Background Task Definitions
│   ├── main.py                 # FastAPI Application Entrypoint
│   └── pyproject.toml          # Python Dependencies (uv managed)
├── render.yaml                 # Render Blueprint Configuration
└── README.md                   # Project Documentation
```

---

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python 3.12+](https://www.python.org/)
- [uv](https://astral.sh/blog/uv) (Extremely fast Python package manager)
- Accounts for: Clerk, NVIDIA Build, Pinecone, Neon.

### Environment Variables

You will need to set up `.env` files in both the frontend and backend directories.

**`backend/.env`**
```ini
DATABASE_URL="postgresql+asyncpg://user:password@endpoint/dbname"
PINECONE_API_KEY="your_pinecone_api_key"
NVIDIA_API_KEY="your_nvidia_nim_api_key"
SLACK_WEBHOOK_URL="optional_slack_webhook_for_alerts"
```

**`frontend/.env.local`**
```ini
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="your_clerk_publishable_key"
CLERK_SECRET_KEY="your_clerk_secret_key"
NEXT_PUBLIC_API_URL="http://127.0.0.1:8000" # Local backend URL
```

### Local Installation

**1. Clone the repository**
```bash
git clone https://github.com/rishabhsingh8445/IntelScout.git
cd IntelScout
```

**2. Setup and run the Backend**
```bash
cd backend
uv pip install -e .
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```
> The API documentation will be available at `http://127.0.0.1:8000/docs`.

**3. Setup and run the Frontend**
```bash
# Open a new terminal
cd frontend
npm install
npm run dev
```
> The web application will be available at `http://localhost:3000`.

---

## ☁️ Deployment

### 1. Deploying the Backend (Render)
IntelScout includes a `render.yaml` Blueprint for 1-click deployment to Render.
- Connect your GitHub repository to Render via "New Blueprint Instance".
- The Blueprint automatically provisions the Python environment using `uv` and starts the Uvicorn server.
- **Ensure you add your Environment Variables** (`NVIDIA_API_KEY`, `PINECONE_API_KEY`, `DATABASE_URL`, `SLACK_WEBHOOK_URL`) in the Render dashboard.

### 2. Deploying the Frontend (Vercel)
The frontend is heavily optimized for Vercel.
- Import the repository into Vercel.
- Set the **Root Directory** to `frontend`.
- Add your Clerk API keys as Environment Variables.
- Set `NEXT_PUBLIC_API_URL` to your deployed Render backend URL (e.g., `https://intelscout-backend.onrender.com`).

---

<div align="center">
  <i>Built for high-performance AI workflows. Designed for scale.</i>
</div>

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
- [Key Features](#-key-features)
- [Technology Stack](#%EF%B8%8F-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Local Installation](#local-installation)
- [Deployment](#%EF%B8%8F-deployment)
- [Usage Guide](#-usage-guide)

---

## 📖 Overview

In today's fast-paced market, keeping tabs on competitors is crucial but time-consuming. **IntelScout** automates competitive intelligence. Simply provide a competitor's domain, and IntelScout's scraping engines will traverse their website, extract product positioning, and analyze their marketing copy. The data is processed through **NVIDIA NIM's Llama 3.3** to extract weaknesses, strengths, and predict future market moves.

---

## 🔬 Data Science & NLP Pipeline

At its core, IntelScout is an advanced **Natural Language Processing (NLP)** and **Data Engineering** pipeline. It transforms unstructured web data into structured competitive insights using the following workflow:

1. **Data Collection & ETL:** Playwright operates as a headless crawler, navigating DOM trees and bypassing bot-protections to scrape unstructured text (product specs, pricing, blog posts, about pages) into raw datasets.
2. **Data Cleaning & Chunking:** The raw text is normalized and split into semantically contiguous chunks (tokens) optimized for the embedding model's context window.
3. **High-Dimensional Embeddings:** Chunks are passed through NVIDIA's `nv-embedqa-e5-v5` model to generate dense vector embeddings (1024-dimensional floating-point arrays) representing the semantic meaning of the text.
4. **Vector Space Modeling:** These vectors are stored in **Pinecone**, establishing a high-dimensional vector space.
5. **Retrieval-Augmented Generation (RAG):** When generating a Battlecard or Insight, the system queries Pinecone using **Cosine Similarity** algorithms to retrieve the exact text chunks relevant to pricing, weaknesses, or market positioning.
6. **LLM Inferencing & Sentiment Analysis:** The retrieved context is fed into **Meta Llama 3.3 (70B-Instruct)** along with engineered prompts to perform Sentiment Analysis, SWOT extraction, and predictive modeling on the competitor's behavior.

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
    FastAPI -->|Context / Prompts| NVIDIA[NVIDIA NIM Llama 3.3]
    FastAPI -->|Vectors| Pinecone[(Pinecone Vector DB)]
    FastAPI -->|Data| Neon[(Neon PostgreSQL)]
    
    WebScraper -->|Scraped Content| FastAPI
    NVIDIA -->|AI Insights & Battlecards| FastAPI
```

</div>

### Component Breakdown:
- **Client (Browser):** Renders the Glassmorphic UI using Framer Motion animations.
- **Frontend (Next.js):** Handles routing, SSR, and API proxying. Authenticates via Clerk.
- **Backend (FastAPI):** Orchestrates long-running scraping tasks and AI inferences asynchronously.
- **Web Scraper (Playwright):** Runs headless browsers to bypass standard bot protections and extract dynamic DOM content.
- **AI Engine (NVIDIA NIM):** Uses `meta/llama-3.3-70b-instruct` for natural language understanding and `nvidia/nv-embedqa-e5-v5` for high-dimensional embeddings.

---

## ✨ Key Features

1. 🕵️ **Real-Time Competitor Tracking:** Add any competitor domain and IntelScout will autonomously scrape and analyze their web presence, extracting product pages, pricing, and company updates.
2. 🧠 **AI-Powered Insights:** Uses advanced LLMs to distill thousands of words of web copy into actionable signals, product changes, and market shifts.
3. ⚔️ **Dynamic Battlecards:** Instantly generates comparative battlecards showing SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis, pricing models, and key differentiators.
4. 📊 **Feature Matrix:** Visual side-by-side comparison matrix of your product vs. competitors.
5. 🔍 **Semantic Search:** Query your entire competitor database using natural language (e.g., "Which competitor has SOC2 compliance?").
6. 🎨 **Premium Glassmorphic UI:** A stunning, premium dark-mode interface built with Tailwind CSS and Framer Motion for a native app feel.

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Frontend** | Next.js 14, React, Tailwind CSS | UI Framework & Styling |
| **Animations** | Framer Motion | Fluid micro-interactions |
| **Auth** | Clerk | Secure user authentication |
| **Backend** | FastAPI, Python 3.12, `uv` | High-performance async API |
| **Web Scraping**| Playwright, BeautifulSoup4 | DOM parsing and headless browsing |
| **AI / LLM** | NVIDIA NIM (Llama 3.3) | Natural Language Processing |
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
│   ├── src/services/           # AI, Scraping, & DB Logic
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
- **Ensure you add your Environment Variables** (`NVIDIA_API_KEY`, `PINECONE_API_KEY`, `DATABASE_URL`) in the Render dashboard.

### 2. Deploying the Frontend (Vercel)
The frontend is heavily optimized for Vercel.
- Import the repository into Vercel.
- Set the **Root Directory** to `frontend`.
- Add your Clerk API keys as Environment Variables.
- Set `NEXT_PUBLIC_API_URL` to your deployed Render backend URL (e.g., `https://intelscout-backend.onrender.com`).

---

## 🎮 Usage Guide

1. **Dashboard Overview:** View high-level metrics and recent insights.
2. **Add Competitors:** Navigate to the "Competitors" tab and add a competitor's domain URL. The backend will immediately begin scraping their site.
3. **Generate Battlecards:** Navigate to the "Battlecards" tab to generate SWOT analyses based on the scraped context.
4. **View Insights:** Check the "Insights" feed for AI-generated observations regarding pricing changes, new feature releases, or marketing shifts.

---

<div align="center">
  <i>Built for high-performance AI workflows. Designed for scale.</i>
</div>

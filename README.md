# 🎓 Gradwise AI

**Gradwise AI**, an academic intelligence platform designed to help educational institutions manage student data, academic workflows, and enable AI-driven insights.

This repository currently contains the **initial backend data layer**, including database connectivity, raw SQL query modules, and foundational project structure for future API and AI integration.

---

## 🚀 Project Goal

Gradwise aims to build a centralized academic system where:

* Students can track attendance, grades, enrollment, and performance
* Institutions can manage organizational data and academic structures
* AI modules can later provide personalized academic insights
* Backend services act as the **core data pipeline** powering intelligent features

---

## 🧱 Current Backend Architecture (As of 25/03/2026)

```text
gradwise-ai/
│
└── backend/
    │
    ├── database/
    │   ├── connection.py      # PostgreSQL connection handling
    │   └── queries.py         # Raw SQL query functions
    │
    ├── main.py                # Temporary execution / testing entry point
    ├── requirements.txt       # Python dependencies
    ├── .env                   # Environment configuration (ignored by git)
    └── .gitignore             # Git ignore rules
```

---

## 🗄️ Database Layer

* Database: **PostgreSQL**
* Access method: **psycopg2 (raw SQL — no ORM)**
* Schema-driven relational design
* Query functions written per entity to support future feature-driven expansion

Current development focuses on:

* Connection lifecycle management
* Insert / fetch query pipelines
* Structured data access layer foundation

---

## ⚙️ Local Setup Instructions

### 1️⃣ Clone repository

```bash
git clone <repo-url>
cd gradwise-ai
```

### 2️⃣ Create and activate virtual environment

```bash
python -m venv backend/venv
backend/venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4️⃣ Configure environment variables

Create a `.env` file inside the `backend` directory:

```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

⚠️ This file must **not be committed to Git.**

---

### ▶️ Running the backend test entry

From project root:

```bash
python backend/main.py
```

This currently runs basic query layer tests.

---

## 📌 Development Philosophy

* Build **feature-driven query layers**, not entire schema logic upfront
* Maintain clean separation between:

  * data access logic
  * business logic (future service layer)
  * API routing layer (future FastAPI integration)
* Prioritize working data pipelines before scaling architecture

---

## 🔮 Planned Roadmap

* Complete CRUD query coverage for core entities
* Introduce service layer abstraction
* Integrate FastAPI REST endpoints
* Implement authentication and role-based access
* Add AI integration (LLM-powered academic assistance)
* Deployment and cloud infrastructure setup

---

## 👨‍💻 Maintainer

**Aaditya Kaushik**
B.Tech ICT

---

> This backend is currently in foundational development phase and will evolve into a scalable academic intelligence platform.

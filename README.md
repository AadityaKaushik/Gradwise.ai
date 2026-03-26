<p align="center">
  <img src="assets/logo.png" alt="Gradwise Logo" width="420"/>
</p>
<p align="center"><b>Your AI-powered academic intelligence platform</b></p>

---

## 🚀 Overview

**Gradwise AI** is an academic intelligence platform designed to help educational institutions manage student data, streamline academic workflows, and unlock AI-driven insights.

This repository currently contains the **foundational backend data layer**, including database connectivity, raw SQL query modules, and a scalable project structure for future API and AI integration.

---

## 🎯 Project Vision

Gradwise aims to become a centralized academic system where:

* Students can track attendance, grades, enrollment, and performance
* Institutions can manage organizational and academic structures
* AI modules provide personalized academic insights
* Backend services act as the **core data pipeline** powering intelligent features

---

## 🧱 Backend Architecture

```
gradwise-ai/
│
└── backend/
    │
    ├── database/
    │   ├── connection.py
    │   ├── organization_queries.py
    │   ├── user_queries.py
    │   ├── membership_queries.py
    │   └── __init__.py
    │
    ├── services/                     
    │   ├── auth_service.py
    │   ├── organization_service.py
    │   └── __init__.py
    │
    ├── utils/
    │   └── security.py               
    │
    ├── main.py                       
    │
    ├── requirements.txt
    ├── .env                          
    └── .gitignore
```

---

## 🗄️ Database Layer

* **Database:** PostgreSQL
* **Driver:** psycopg2 (raw SQL — no ORM)
* **Design:** Schema-driven relational structure

### Current Focus:

* Connection lifecycle management
* Insert / fetch query pipelines
* Modular query functions per entity

---

## ⚙️ Local Setup

### 1️⃣ Clone Repository

```bash
git clone <repo-url>
cd gradwise-ai
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv backend/venv
backend/venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file inside `backend/`:

```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

⚠️ Do NOT commit this file.

---

## ▶️ Running the Backend

```bash
python backend/main.py
```

Currently used for testing database queries and connectivity.

---

## 🧠 Development Philosophy

* Build **feature-driven query layers**, not over-engineered systems
* Maintain clear separation between:

  * Data access layer
  * Business logic (services)
  * API layer (future FastAPI)
* Focus on **working pipelines before scaling complexity**

---

## 🔮 Roadmap

* [ ] Complete CRUD operations for core entities
* [ ] Expand service layer
* [ ] Integrate FastAPI APIs
* [ ] Implement authentication & role-based access
* [ ] Add AI-powered academic insights
* [ ] Deploy to cloud infrastructure

---

## 👨‍💻 Maintainer

**Aaditya Kaushik**
B.Tech ICT

---

<p align="center">
  <i>Building the infrastructure for intelligent academic systems.</i>
</p>

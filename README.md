<p align="center">
  <img src="assets/logo.png" alt="Gradwise Logo" width="420"/>
</p>
<p align="center"><b>Your AI-powered academic intelligence platform</b></p>

---

## 🚀 Overview

**Gradwise AI** is an academic intelligence platform designed to help educational institutions manage student data, streamline academic workflows, and unlock AI-driven insights.

This repository contains the **backend system**, including a FastAPI application, pure SQL database connectivity, JWT authentication, and a containerized infrastructure with Docker.

---

## 🎯 Project Vision

Gradwise aims to become a centralized academic system where:

* Students can track attendance, grades, enrollment, and performance
* Institutions can manage organizational and academic structures
* AI modules provide personalized academic insights
* Backend services act as the **core data pipeline** powering intelligent features

---

## 🧱 Architecture

```
gradwise-ai/
│
├── backend/
│   ├── database/          # Pure SQL queries and DB connections
│   ├── services/          # Business logic and auth service
│   ├── Utils/             # Security, JWT, and helpers
│   ├── main.py            # FastAPI entrypoint
│   ├── Dockerfile         # Docker image definition
│   └── requirements.txt
│
└── docker-compose.yml     # API and Postgres container orchestration
```

---

## 🗄️ Technology Stack

* **API Framework:** FastAPI
* **Database:** PostgreSQL
* **Driver:** psycopg2 (raw SQL — no ORM)
* **Authentication:** JWT (JSON Web Tokens)
* **Containerization:** Docker & Docker Compose

---

## ⚙️ Local Setup & Running (Docker)

The recommended way to run the application is using Docker Compose.

### 1️⃣ Clone Repository

```bash
git clone <repo-url>
cd gradwise-ai
```

### 2️⃣ Configure Environment Variables

Create a `.env` file inside the `backend/` directory:

```env
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=gradwise
JWT_SECRET_KEY=your_super_secret_dev_key
```

⚠️ Do NOT commit this file to version control.

### 3️⃣ Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`. You can test the endpoints via the interactive Swagger documentation at `http://localhost:8000/docs`.

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

* [x] Complete CRUD operations for core entities
* [x] Expand service layer
* [x] Integrate FastAPI APIs
* [x] Implement authentication & role-based access
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

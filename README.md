<div align="center">

⚡ AgentOS

Enterprise Multi-Agent AI Operating System

A unified AI workspace that turns natural-language requests into intelligent, observable workflows.

<br/>

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=111827" alt="React">
  <img src="https://img.shields.io/badge/LangGraph-Orchestration-111827?style=for-the-badge" alt="LangGraph">
  <img src="https://img.shields.io/badge/ChromaDB-RAG-FF6B35?style=for-the-badge" alt="ChromaDB">
  <img src="https://img.shields.io/badge/SQLite-Persistence-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

<br/>

<!-- Add your final hero GIF here -->

<img src="docs/assets/agentos-demo.gif" width="900" alt="AgentOS demo">

<br/><br/>

Ask · Analyze · Research · Retrieve · Generate

</div>

✦ Introduction

AgentOS is a multi-agent AI operating system built to bring several AI capabilities into one intelligent workspace.

Instead of treating every request as a simple:

User → Prompt → LLM → Answer

AgentOS uses a Supervisor Agent to understand the user's intent, create an execution plan, route the request to the appropriate specialized agent, and return the result through a visual workspace.

The system currently brings together:

💬 General AI conversations

📚 Document-grounded RAG

🔎 Research workflows

📊 Natural-language data analytics

📄 AI-powered PDF/DOCX report generation

💾 Persistent conversations

👁️ Workflow execution visualization

The goal was not to build several disconnected AI demos.

The goal was to build one coherent system in which specialized AI capabilities work together through a controlled architecture.

01 · The Problem

Modern AI applications often start as a single chatbot.

That works well for simple questions, but becomes difficult when the application needs to handle very different types of work.

For example:

"Explain dependency injection."

is fundamentally different from:

"Search my uploaded resume and tell me about my projects."

which is different from:

"Analyze this dataset and find the average sales by region."

and different again from:

"Use the information you found and generate a professional report."

Putting all of these responsibilities into one large prompt creates a system that becomes harder to reason about, maintain, test, and extend.

AgentOS addresses this by separating responsibilities.

                    USER REQUEST
                         │
                         ▼
                 ┌───────────────┐
                 │   SUPERVISOR  │
                 │     AGENT     │
                 └───────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        RAG          ANALYTICS       RESEARCH
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                    DOCUMENT
                       AGENT
                         │
                         ▼
                    PDF / DOCX

The user describes what they want.

The system decides how it should be executed.

02 · What I Built

AgentOS is built around six focused agents.

Agent

Responsibility

🧠 Supervisor Agent

Understands intent, creates execution plans, and controls routing

💬 Chat Agent

Handles general conversational requests

📚 RAG Agent

Retrieves information from uploaded documents and generates grounded answers

🔎 Research Agent

Handles research-oriented requests

📊 Analytics Agent

Converts natural-language analysis requests into executable data analysis

📄 Document Agent

Converts agent outputs into professional PDF/DOCX reports

The important design choice

The specialized agents are not randomly chained together.

The Supervisor remains the orchestration layer.

For example:

User
 │
 ▼
Supervisor
 │
 ├── RAG
 │
 └── Document

or:

User
 │
 ▼
Supervisor
 │
 ├── Analytics
 │
 └── Document

This keeps the architecture understandable and prevents the system from becoming a collection of tightly coupled agent-to-agent dependencies.

03 · Architecture

◈ System Overview

flowchart TB

    U(["👤 User"])

    UI["🖥️ AgentOS Workspace<br/>React + Vite"]

    API["⚡ FastAPI<br/>REST API"]

    S["🧠 Supervisor Agent<br/>Intent → Execution Plan"]

    C["💬 Chat Agent"]
    R["📚 RAG Agent"]
    RS["🔎 Research Agent"]
    A["📊 Analytics Agent"]
    D["📄 Document Agent"]

    V["🗃️ ChromaDB<br/>Vector Retrieval"]
    P["🐼 Pandas<br/>Data Processing"]

    M["💾 SQLite<br/>Conversations + Reports"]

    O["✨ Final Response"]
    F["📑 PDF / DOCX"]

    U --> UI
    UI --> API
    API --> S

    S --> C
    S --> R
    S --> RS
    S --> A

    R --> V
    A --> P

    R --> D
    RS --> D
    A --> D

    D --> F
    D --> M

    C --> O
    R --> O
    RS --> O
    A --> O
    F --> O

    classDef user fill:#111827,stroke:#67e8f9,color:#f9fafb
    classDef control fill:#172554,stroke:#60a5fa,color:#f9fafb
    classDef agent fill:#1e293b,stroke:#a5b4fc,color:#f9fafb
    classDef storage fill:#052e2b,stroke:#2dd4bf,color:#f9fafb
    classDef output fill:#3f1d38,stroke:#f0abfc,color:#f9fafb

    class U user
    class S control
    class C,R,RS,A,D agent
    class V,P,M storage
    class O,F output

Architecture flow

User
  ↓
React Workspace
  ↓
FastAPI
  ↓
Supervisor
  ↓
Specialized Agent
  ↓
Agent-specific processing
  ↓
Shared workflow state
  ↓
Final response / document

The architecture deliberately separates:

presentation → API → orchestration → specialized intelligence → storage/output

04 · How the Agents Work Together

🧠 Supervisor

The Supervisor is the control layer.

It interprets the user's request and determines the execution plan.

Examples:

"What is Python?"
        ↓
Supervisor
        ↓
Chat

"What does my resume say about my projects?"
        ↓
Supervisor
        ↓
RAG

"Analyze this dataset."
        ↓
Supervisor
        ↓
Analytics

"Create a report from the information in my resume."
        ↓
Supervisor
        ↓
RAG → Document

The Supervisor does not perform every task itself.

It decides which specialized capability should perform the task.

05 · RAG Pipeline

AgentOS includes a document-grounded retrieval pipeline.

┌──────────────────┐
│  Uploaded File   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│     Parsing      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│     Chunking     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│    Embeddings    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│     ChromaDB     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Hybrid Retrieval │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  Relevance Gate  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Relevant Context │
└────────┬─────────┘
         ↓
┌──────────────────┐
│       LLM        │
└────────┬─────────┘
         ↓
   Grounded Answer

This allows users to ask questions about their uploaded material without treating the LLM as the source of truth.

06 · Analytics Pipeline

Analytics uses a different principle:

The LLM understands the request. Deterministic code performs the calculation.

Natural Language Query
          ↓
   Analysis Planning
          ↓
    Analysis Plan
          ↓
        Pandas
          ↓
 ┌────────┼────────┐
 ↓        ↓        ↓
Filter   Group   Aggregate
 └────────┼────────┘
          ↓
   Structured Result
          ↓
    LLM Explanation
          ↓
     Final Answer

This avoids unnecessarily sending entire datasets through an LLM and allows actual calculations to be performed by Pandas.

07 · Research Workflow

Research is intentionally separated from document-grounded RAG.

User Research Request
          ↓
      Supervisor
          ↓
    Research Agent
          ↓
 Research / Synthesis
          ↓
     Final Response

The distinction is:

RAG
→ "Find information in my uploaded content."

Research
→ "Research and synthesize information about this topic."

08 · Document Generation

One of the key capabilities of AgentOS is converting existing agent intelligence into professional documents.

flowchart LR

    U["User Request"]

    S["Supervisor"]

    R["📚 RAG"]
    A["📊 Analytics"]
    RS["🔎 Research"]

    D["📄 Document Agent"]

    PDF["PDF"]
    DOCX["DOCX"]

    U --> S

    S --> R
    S --> A
    S --> RS

    R --> D
    A --> D
    RS --> D

    D --> PDF
    D --> DOCX

The Document Agent receives useful output from the source agent and transforms it into a structured report.

Report lifecycle

Agent Output
     ↓
Document Agent
     ↓
Document Service
     ↓
 ┌─────────┐
 │ PDF     │
 │ DOCX    │
 └────┬────┘
      ↓
SQLite Metadata
      ↓
Reports UI
      ↓
Download / Delete

09 · Conversation Memory

AgentOS persists conversations using SQLite.

Conversation
     │
     ├── User Message
     ├── Assistant Message
     ├── User Message
     └── Assistant Message

The workspace allows users to:

start a new conversation

view previous conversations

restore a conversation

continue interacting

delete a conversation

Memory operations are isolated inside the MemoryService, keeping persistence separate from agent reasoning.

10 · Workflow Visualization

AgentOS exposes the execution path through a workflow trace.

For example:

             ┌─────────────┐
             │ Supervisor  │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │     RAG     │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │  Document   │
             └─────────────┘

The frontend uses this information to highlight the agents involved in the current execution.

This gives the user visibility into:

Which agents ran?
        ↓
What was the execution path?
        ↓
What kind of workflow was performed?

11 · What AgentOS Actually Does

💬 Ask Anything

Ask a general question and AgentOS routes it to the Chat Agent.

📚 Search Documents

Upload a document and ask questions about its contents using the RAG pipeline.

🔎 Research Topics

Send research-oriented requests to the dedicated Research Agent.

📊 Analyze Data

Provide structured data and ask questions in natural language.

📄 Generate Reports

Turn RAG, Research, or Analytics outputs into professional PDF/DOCX reports.

💾 Continue Conversations

Return to previous conversations through the persistent workspace.

👁️ Observe the Workflow

See which agents participated in the current execution.

12 · Project Structure

Agent-OS/
│
└── agentos-scaffold/
    │
    ├── backend/
    │   │
    │   ├── agents/
    │   │   ├── api/
    │   │   ├── config/
    │   │   ├── database/
    │   │   ├── models/
    │   │   ├── prompts/
    │   │   ├── schemas/
    │   │   ├── services/
    │   │   └── workflows/
    │   │
    │   ├── main.py
    │   └── requirements.txt
    │
    ├── frontend/
    │   │
    │   ├── public/
    │   ├── src/
    │   │   ├── components/
    │   │   ├── hooks/
    │   │   ├── pages/
    │   │   └── services/
    │   │
    │   └── package.json
    │
    ├── docs/
    │   ├── assets/
    │   │   ├── agentos-demo.gif
    │   │   ├── rag-workflow.gif
    │   │   └── report-generation.gif
    │   │
    │   └── screenshots/
    │       ├── dashboard.png
    │       ├── workspace.png
    │       ├── analytics.png
    │       └── reports.png
    │
    └── README.md

Backend organization

agents/
    Agent behavior and orchestration logic

api/
    REST endpoints

database/
    Database connections and vector-store integration

models/
    Persistence models

prompts/
    Agent-specific LLM prompts

schemas/
    Shared state and API contracts

services/
    Reusable application services

workflows/
    LangGraph execution graph

Frontend organization

components/
    Reusable UI components

hooks/
    Frontend state and interaction logic

pages/
    Main application screens

services/
    Backend API communication

13 · Run AgentOS on Your Computer

Prerequisites

Install:

Python 3.x

Node.js + npm

Git

A Groq API key

Verify the installations:

python --version
node --version
npm --version
git --version

Step 1 — Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>

Move into the project:

cd Agent-OS/agentos-scaffold

Step 2 — Configure the backend

cd backend

Create a virtual environment:

python -m venv .venv

Windows

.venv\Scripts\activate

macOS / Linux

source .venv/bin/activate

Install Python dependencies:

pip install -r requirements.txt

Step 3 — Configure environment variables

Create:

backend/.env

Add the required API configuration used by the application, including your Groq API key.

Example:

GROQ_API_KEY=your_groq_api_key

Keep .env private. Never commit API keys to GitHub.

Step 4 — Start the backend

From the backend directory:

uvicorn main:app --reload --port 8000

The API will be available at:

http://localhost:8000

FastAPI Swagger documentation:

http://localhost:8000/docs

Health check:

http://localhost:8000/api/v1/health

Step 5 — Start the frontend

Open a second terminal.

Move to:

cd Agent-OS/agentos-scaffold/frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend will normally be available at:

http://localhost:5173

Step 6 — Open AgentOS

Open:

http://localhost:5173

You can then:

Enter Workspace
      ↓
Ask a question
      ↓
Upload a document
      ↓
Search your document
      ↓
Analyze data
      ↓
Generate a report
      ↓
View the workflow
      ↓
Download / manage reports

14 · Screenshots

The repository can showcase the actual product here.

Replace the placeholder files with your final screenshots.

<div align="center">

Dashboard

<img src="docs/screenshots/dashboard.png" width="850" alt="AgentOS Dashboard">

<br/><br/>

Workspace

<img src="docs/screenshots/workspace.png" width="850" alt="AgentOS Workspace">

<br/><br/>

Analytics

<img src="docs/screenshots/analytics.png" width="850" alt="AgentOS Analytics">

<br/><br/>

Reports

<img src="docs/screenshots/reports.png" width="850" alt="AgentOS Reports">

</div>

15 · Product Demonstrations

AgentOS Demo

<img src="docs/assets/agentos-demo.gif" width="900" alt="AgentOS demonstration">

RAG Workflow

<img src="docs/assets/rag-workflow.gif" width="900" alt="AgentOS RAG workflow">

Report Generation

<img src="docs/assets/report-generation.gif" width="900" alt="AgentOS report generation">

16 · Technology

<div align="center">

Layer

Technology

Frontend

React, Vite, Tailwind CSS

Backend

Python, FastAPI

Orchestration

LangGraph

LLM

Groq — openai/gpt-oss-120b

RAG

ChromaDB + embeddings + retrieval

Analytics

Pandas

Persistence

SQLite + SQLAlchemy

Documents

PDF + DOCX

Visualization

React Flow

API Client

Axios

</div>

17 · The Engineering Idea Behind AgentOS

The central idea is simple:

             One User
                │
                ▼
        Natural-language Intent
                │
                ▼
          Supervisor Agent
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
      RAG    Analytics Research
       │        │        │
       └────────┼────────┘
                ▼
         Document Agent
                │
                ▼
           Final Output

But the engineering challenge is making all of those capabilities work together without turning the application into one tightly coupled AI pipeline.

AgentOS addresses that through:

centralized orchestration + shared state + specialized agents + dedicated services + persistent storage + observable workflows.

<div align="center">

✨ Thanks for exploring AgentOS

Built to explore what happens when AI capabilities become a coordinated system instead of a single chatbot.

Ask. Analyze. Research. Retrieve. Generate.

<br/>

Built by Chandu
B.Tech — Artificial Intelligence & Machine Learning

</div>

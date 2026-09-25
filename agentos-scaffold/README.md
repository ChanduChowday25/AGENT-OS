<div align="center">

⚡ AgentOS

Enterprise Multi-Agent AI Operating System

A unified AI workspace for intelligent conversation, document analysis, research, data analytics, and automated report generation.

<br>








<br><br>

Ask anything · Search documents · Research · Analyze data · Generate reports

</div>

Introduction

AgentOS is a multi-agent AI operating system that brings different AI capabilities into one workspace.

Instead of sending every request directly to one large language-model prompt, AgentOS uses a Supervisor Agent to understand the user's intent and route the request to the appropriate specialized agent.

The current system includes:

Supervisor Agent — intent understanding and workflow routing

Chat Agent — general conversational requests

RAG Agent — document-grounded question answering

Research Agent — research-oriented tasks

Analytics Agent — natural-language data analysis

Document Agent — professional PDF/DOCX generation

The application also includes conversation persistence, file uploads, workflow visualization, report management, and a React-based AI workspace.

The idea behind AgentOS:
Turn a natural-language request into a controlled, observable AI workflow.

What Problem Does It Solve?

A traditional AI application often looks like:

User
  ↓
One Prompt
  ↓
LLM
  ↓
Response

That approach becomes difficult when an application needs to perform very different types of work.

For example:

"Explain REST APIs."

requires general conversation.

"Find the projects mentioned in my resume."

requires document retrieval.

"Find the average sales for each region."

requires deterministic data processing.

"Create a professional report from this information."

requires document generation.

These are different responsibilities.

AgentOS separates them into specialized agents and places a Supervisor in control of the workflow.

                       User Request
                            │
                            ▼
                    ┌───────────────┐
                    │   Supervisor  │
                    │     Agent     │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
           Chat            RAG          Research
             │              │              │
             │              │              │
             │              └──────┐       │
             │                     │       │
             │                     ▼       │
             │                Document     │
             │                  Agent      │
             │                     ▲       │
             │                     │       │
             └─────────────────────┴───────┘

The user describes what they want.

The Supervisor determines which capability should execute it.

What I Built

1. Centralized Multi-Agent Orchestration

The Supervisor controls the execution plan.

Supported workflows include:

Chat
RAG
Research
Analytics

RAG       → Document
Research  → Document
Analytics → Document

Specialized agents do not arbitrarily call one another. The workflow layer keeps orchestration centralized.

2. Document Intelligence with RAG

Users can upload documents and ask questions about their content.

The RAG workflow performs:

Uploaded File
     ↓
Document Ingestion
     ↓
Parsing / Chunking
     ↓
Embeddings
     ↓
ChromaDB
     ↓
Hybrid Retrieval
     ↓
Relevance Filtering
     ↓
Context Construction
     ↓
LLM
     ↓
Grounded Answer

The retrieved information can also become the source for a later document-generation workflow.

3. Natural-Language Data Analytics

The Analytics Agent uses a hybrid approach.

The LLM understands the request and creates an analysis plan, while Pandas performs the actual data operations.

User Query
    ↓
Analysis Planning
    ↓
Structured Analysis Plan
    ↓
Pandas
    ↓
Filtering / Grouping / Aggregation
    ↓
Structured Result
    ↓
LLM Explanation
    ↓
Final Answer

This keeps numerical processing deterministic instead of asking the LLM to perform calculations itself.

4. Research

Research requests are handled separately from document-grounded RAG.

Research Request
      ↓
Supervisor
      ↓
Research Agent
      ↓
Research / Synthesis
      ↓
Final Response

RAG answers questions from uploaded material, while Research handles research-oriented requests.

5. AI-Powered Report Generation

The Document Agent converts useful output from other agents into professional documents.

For example:

User Request
     ↓
Supervisor
     ↓
RAG / Research / Analytics
     ↓
Document Agent
     ↓
Document Service
     ↓
PDF / DOCX
     ↓
Reports

Generated reports are persisted so they can be viewed, downloaded, and deleted from the Reports interface.

6. Conversation Memory

AgentOS stores conversations in SQLite.

Users can:

start a new chat

view previous conversations

restore a conversation

continue the conversation

delete a conversation

Memory operations are isolated inside the MemoryService.

7. Workflow Visualization

The backend records which agents participate in an execution.

For example:

Supervisor
    │
    ▼
   RAG
    │
    ▼
Document

The frontend uses the workflow trace to highlight the participating agents in the Agent Network.

This makes the multi-agent execution visible instead of hiding everything behind a single chatbot response.

Architecture

High-Level Architecture

flowchart TB

    USER["👤 User"]

    FRONTEND["🖥️ React Workspace<br/>Dashboard · Workspace · Analytics · Reports"]

    API["⚡ FastAPI<br/>REST API"]

    SUPERVISOR["🧠 Supervisor Agent<br/>Intent → Execution Plan"]

    CHAT["💬 Chat Agent"]
    RAG["📚 RAG Agent"]
    RESEARCH["🔎 Research Agent"]
    ANALYTICS["📊 Analytics Agent"]
    DOCUMENT["📄 Document Agent"]

    CHROMA["🗃️ ChromaDB<br/>Document Retrieval"]
    PANDAS["🐼 Pandas<br/>Data Processing"]

    SQLITE["💾 SQLite<br/>Conversations + Reports"]

    OUTPUT["✨ Final Response"]
    REPORTS["📑 PDF / DOCX"]

    USER --> FRONTEND
    FRONTEND --> API
    API --> SUPERVISOR

    SUPERVISOR --> CHAT
    SUPERVISOR --> RAG
    SUPERVISOR --> RESEARCH
    SUPERVISOR --> ANALYTICS

    RAG --> CHROMA
    ANALYTICS --> PANDAS

    RAG --> DOCUMENT
    RESEARCH --> DOCUMENT
    ANALYTICS --> DOCUMENT

    CHAT --> OUTPUT
    RAG --> OUTPUT
    RESEARCH --> OUTPUT
    ANALYTICS --> OUTPUT

    DOCUMENT --> REPORTS
    DOCUMENT --> SQLITE

    FRONTEND -. conversations .-> SQLITE

The architecture in one line

React → FastAPI → Supervisor → Specialized Agent(s) → Result / Document

Shared AgentState

Agents communicate through a shared workflow state rather than being tightly coupled to one another.

The state carries information such as:

query
uploaded_files
conversation_history
execution_plan

rag_output
research_output
analytics_output
document_output

final_response
workflow_trace

This gives the workflow a consistent contract between the Supervisor, specialized agents, and final response aggregation.

Project Structure

The repository is organized around the separation between the AI backend and the React workspace.

Agent-OS/
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
    │   │   ├── workflows/
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   │
    │   └── .env
    │
    └── frontend/
        │
        ├── public/
        ├── src/
        │   ├── components/
        │   ├── hooks/
        │   ├── pages/
        │   └── services/
        │
        └── package.json

Backend

agents/       → Agent implementations
api/          → FastAPI routes
config/       → Application configuration
database/     → Database and vector-store connections
models/       → SQLAlchemy persistence models
prompts/      → Agent-specific prompts
schemas/      → Pydantic schemas and AgentState
services/     → Reusable application services
workflows/    → LangGraph orchestration
main.py       → FastAPI application entry point

Frontend

components/   → Reusable UI components
hooks/        → Frontend state and workflow logic
pages/        → Dashboard, Workspace, Analytics, Reports
services/     → Backend API communication
public/       → Static frontend assets

How AgentOS Works in Practice

Example 1 — General Question

"What is dependency injection?"
            ↓
        Supervisor
            ↓
        Chat Agent
            ↓
        Final Answer

Example 2 — Ask About an Uploaded Document

"What projects are mentioned in my resume?"
                    ↓
                Supervisor
                    ↓
                  RAG
                    ↓
                ChromaDB
                    ↓
            Relevant Context
                    ↓
                   LLM
                    ↓
             Grounded Answer

Example 3 — Generate a Report

"Create a professional report from my resume."
                    ↓
                Supervisor
                    ↓
                   RAG
                    ↓
             Retrieved Output
                    ↓
              Document Agent
                    ↓
              PDF / DOCX

Example 4 — Analyze Data

"Find the average sales by region."
                    ↓
                Supervisor
                    ↓
               Analytics
                    ↓
            Analysis Planner
                    ↓
                  Pandas
                    ↓
            Computed Result
                    ↓
             LLM Explanation
                    ↓
              Final Answer

Technology Stack

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

Data Processing

Pandas

Persistence

SQLite + SQLAlchemy

Documents

PDF / DOCX generation

Workflow UI

React Flow

API Client

Axios

Markdown Rendering

React Markdown + Remark GFM

Run AgentOS Locally

Prerequisites

Install:

Python 3.x

Node.js and npm

Git

A Groq API key

Verify:

python --version
node --version
npm --version
git --version

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Agent-OS/agentos-scaffold

2. Set up the backend

cd backend

Create a Python virtual environment:

python -m venv .venv

Windows

.venv\Scripts\activate

macOS / Linux

source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

3. Configure environment variables

Create:

backend/.env

Add the required Groq configuration:

GROQ_API_KEY=your_groq_api_key

Keep .env private and do not commit API keys to GitHub.

4. Start the backend

From backend/:

uvicorn main:app --reload --port 8000

Backend:

http://localhost:8000

Swagger:

http://localhost:8000/docs

Health check:

http://localhost:8000/api/v1/health

5. Set up the frontend

Open a second terminal:

cd Agent-OS/agentos-scaffold/frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Open:

http://localhost:5173

6. Start using AgentOS

Once both services are running:

Open AgentOS
     ↓
Enter the Workspace
     ↓
Ask a question
     ↓
Upload a document when needed
     ↓
Search documents / research / analyze
     ↓
Generate a report when required
     ↓
Inspect the workflow
     ↓
Download or manage generated reports

Screenshots

Screenshots can be added here once the final project captures are ready.

No placeholder images are included in this README, so the repository will not display broken or empty image cards.

Project Highlights

┌─────────────────────────────────────────────────────────────┐
│                        AgentOS                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 Supervisor        Centralized AI orchestration          │
│  📚 RAG               Document-grounded answers             │
│  🔎 Research          Research-oriented workflows           │
│  📊 Analytics         Natural-language data analysis        │
│  📄 Documents         PDF / DOCX report generation          │
│  💾 Memory            Persistent conversations               │
│  👁️ Workflow          Visible agent execution               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Closing

AgentOS was built to explore how multiple specialized AI capabilities can be combined into one coherent application.

The core idea is:

Natural Language
       ↓
Intent Understanding
       ↓
Workflow Planning
       ↓
Specialized AI Execution
       ↓
Result Aggregation
       ↓
Useful Output

Rather than building a collection of isolated AI features, AgentOS brings them together through centralized orchestration, shared workflow state, dedicated services, persistent storage, and an interactive workspace.

<br>

<div align="center">

Thanks for exploring AgentOS.

Built with curiosity, engineering, and a lot of debugging.

<br>

Chandu
B.Tech — Artificial Intelligence & Machine Learning

</div>
<div align="center">

AgentOS

Enterprise Multi-Agent AI Operating System

A production-oriented multi-agent workspace for intelligent research, document intelligence, grounded Q&A, data analytics, conversation memory, and automated report generation.

<br/>








<br/>

Multi-Agent AI · RAG · Analytics · Research · Memory · Document Generation

</div>

⚡ 30-Second Overview

AgentOS is not a single-prompt chatbot.

It is a multi-agent AI application where a Supervisor Agent interprets the user's intent, creates an execution plan, routes work to specialized agents, aggregates their outputs, and exposes the workflow to the user through a React workspace.

                         USER INTENT
                              │
                              ▼
                    ┌──────────────────┐
                    │    Supervisor    │
                    │      Agent       │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
      ┌────────┐         ┌────────┐         ┌──────────┐
      │  RAG   │         │Research│         │Analytics │
      │ Agent  │         │ Agent  │         │  Agent   │
      └────┬───┘         └───┬────┘         └────┬─────┘
           │                 │                   │
           └─────────────────┼───────────────────┘
                             ▼
                     ┌───────────────┐
                     │   Document   │
                     │     Agent    │
                     └───────┬───────┘
                             ▼
                         PDF / DOCX

What I actually built

6 cooperating agents with separate responsibilities

Supervisor-driven orchestration using LangGraph

RAG pipeline with document ingestion, chunking, embeddings, retrieval and relevance filtering

Analytics pipeline using an LLM-generated analysis plan + Pandas execution

Research workflow

Conversation persistence and restoration

PDF/DOCX report generation

Workflow execution visualization

Report download and deletion

React workspace designed around agent execution rather than a basic chat screen

🧠 What Problem Does AgentOS Solve?

A conventional AI chatbot usually looks like:

User → Prompt → LLM → Response

That approach becomes difficult to maintain when the application needs to support different types of work.

AgentOS separates those responsibilities:

User Request
     │
     ▼
Intent Understanding
     │
     ▼
Execution Planning
     │
     ▼
Specialized Agent
     │
     ▼
Tool / Data / Retrieval Processing
     │
     ▼
Result
     │
     ▼
Optional Document Generation

The user does not need to know which agent should handle a request.

They describe what they want, and the Supervisor determines how the system should execute it.

🏗️ Architecture

High-Level System Architecture

┌─────────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                              │
│                                                                     │
│ Dashboard │ Workspace │ Analytics │ Reports │ Conversations        │
│                                                                     │
│ Agent Network │ Workflow Visualization │ File Upload │ Chat        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ REST API
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           FASTAPI                                   │
│                                                                     │
│ Chat │ Upload │ Analyze │ Conversations │ Reports │ Health         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       LANGGRAPH WORKFLOW                            │
│                                                                     │
│                        ┌──────────────┐                             │
│                        │  Supervisor  │                             │
│                        │    Agent     │                             │
│                        └───────┬──────┘                             │
│                                │                                    │
│        ┌───────────────┬──────┼───────────────┬───────────────┐    │
│        ▼               ▼      ▼               ▼               ▼    │
│    ┌───────┐       ┌───────┐ ┌─────────┐  ┌──────────┐  ┌───────┐│
│    │ Chat  │       │  RAG  │ │Research │  │Analytics │  │Document││
│    │ Agent │       │ Agent │ │ Agent   │  │  Agent   │  │ Agent ││
│    └───────┘       └───┬───┘ └─────────┘  └────┬─────┘  └───┬───┘│
│                         │                       │             │    │
└─────────────────────────┼───────────────────────┼─────────────┼────┘
                          │                       │             │
                          ▼                       ▼             ▼
                    ┌──────────┐            ┌──────────┐  ┌──────────┐
                    │ ChromaDB │            │  Pandas  │  │PDF/DOCX │
                    │ Retrieval│            │ Analysis │  │Generator │
                    └──────────┘            └──────────┘  └──────────┘
                          │                       │             │
                          └───────────────┬───────┴─────────────┘
                                          ▼
                                    ┌───────────┐
                                    │  SQLite   │
                                    │ Memory +  │
                                    │  Reports  │
                                    └───────────┘

🤖 Agent Architecture

AgentOS currently contains six core agents.

Agent

Responsibility

Typical Output

Supervisor

Intent understanding, routing and execution planning

Execution plan

Chat

General conversational requests

Natural-language response

RAG

Question answering over uploaded documents

Grounded answer

Research

Research-oriented requests

Synthesized research response

Analytics

Structured data analysis

Computed insights

Document

Converts existing agent outputs into professional documents

PDF/DOCX report

Why separate agents?

Each agent has one clear responsibility.

That means:

RAG ≠ Analytics ≠ Research ≠ Document Generation

Instead of building one giant agent that knows how to do everything, AgentOS separates the capabilities and lets the Supervisor coordinate them.

🎯 Supervisor-Driven Orchestration

The Supervisor is the control layer of the system.

For a simple question:

User
 │
 ▼
Supervisor
 │
 ▼
Chat Agent
 │
 ▼
Response

For document Q&A:

User
 │
 ▼
Supervisor
 │
 ▼
RAG Agent
 │
 ▼
Response

For report generation from retrieved document information:

User
 │
 ▼
Supervisor
 │
 ├── RAG
 │
 └── Document
 │
 ▼
PDF / DOCX

For analytics reporting:

User
 │
 ▼
Supervisor
 │
 ├── Analytics
 │
 └── Document
 │
 ▼
PDF / DOCX

The important architectural constraint is that specialized agents do not form arbitrary agent-to-agent chains.

The Supervisor remains responsible for orchestration.

🔄 Shared AgentState

The agents communicate through a shared workflow state rather than directly depending on one another's internal implementation.

Conceptually:

AgentState
│
├── query
├── uploaded_files
├── conversation_history
├── execution_plan
│
├── rag_output
├── research_output
├── analytics_output
├── document_output
│
├── final_response
└── workflow_trace

This provides a common contract between:

Supervisor
     ↓
Specialized Agents
     ↓
Workflow Aggregation
     ↓
Final Response

It also makes the execution path easier to trace and debug.

📚 RAG Pipeline

The RAG subsystem is designed to answer questions using the user's uploaded content rather than relying only on the LLM's general knowledge.

                Uploaded File
                     │
                     ▼
              Document Ingestion
                     │
                     ▼
                 Parsing
                     │
                     ▼
                 Chunking
                     │
                     ▼
                Embeddings
                     │
                     ▼
                  ChromaDB
                     │
                     ▼
             Hybrid Retrieval
                     │
                     ▼
              Relevance Gate
                     │
                     ▼
             Relevant Context
                     │
                     ▼
                    LLM
                     │
                     ▼
              Grounded Answer

RAG responsibilities

The RAG Agent handles:

retrieving relevant document information

building context for the LLM

applying relevance filtering

generating grounded answers

exposing its result to the workflow state

This allows the same RAG output to become an input to the Document Agent when the user requests a report.

📊 Analytics Pipeline

Analytics was designed around a key principle:

Let deterministic code perform deterministic calculations.

Instead of sending an entire dataset to the LLM and asking it to calculate everything:

User Query
    │
    ▼
Analysis Planning
    │
    ▼
Structured Analysis Plan
    │
    ▼
Pandas
    │
    ├── Filter
    ├── Group
    ├── Aggregate
    ├── Calculate
    └── Inspect
    │
    ▼
Structured Result
    │
    ▼
LLM Explanation
    │
    ▼
Human-readable Answer

Why this architecture?

It reduces unnecessary token usage and makes numerical operations deterministic.

The LLM is primarily used for:

Understanding the request
        +
Planning the analysis
        +
Explaining the result

while Pandas performs the actual data processing.

🔎 Research Agent

The Research Agent is separated from the RAG Agent because the two capabilities solve different problems.

RAG
→ "Find the answer in my uploaded material."

Research
→ "Research and synthesize information about this topic."

This separation prevents document-grounded retrieval logic from being mixed with research-oriented reasoning.

📄 Document Generation

The Document Agent is designed as a reusable output layer.

It can consume results produced by:

RAG
Research
Analytics

and turn them into a professional report.

Example

                  RAG Output
                      │
                      │
Research Output ──────┼──────► Document Agent
                      │
                Analytics Output
                              │
                              ▼
                    Structured Report
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                   PDF                 DOCX

The Document Agent is not responsible for rediscovering the underlying information.

Its job is to transform already-produced intelligence into a structured document.

Report lifecycle

Generate
   │
   ▼
Document Service
   │
   ├── PDF
   └── DOCX
   │
   ▼
Report Metadata → SQLite
   │
   ▼
Reports UI
   │
   ├── Download
   └── Delete

🧠 Conversation Memory

Conversation persistence is handled separately from agent reasoning.

              SQLite
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
 Conversations          Messages
       │                   │
       └─────────┬─────────┘
                 ▼
          MemoryService
                 │
                 ▼
       Conversation Restore

The frontend supports:

conversation listing

conversation selection

restoring previous messages

new conversations

deleting conversations

This keeps memory concerns inside a dedicated service instead of embedding database operations inside individual agents.

👁️ Workflow Observability

A major part of the AgentOS experience is making the multi-agent execution visible.

The backend records a workflow trace such as:

Supervisor → RAG → Document

or:

Supervisor → Analytics

The frontend uses that trace to highlight the participating agents in the Agent Network.

This provides a simple but useful form of agent observability:

What did the system do?
        ↓
Which agents ran?
        ↓
What was the execution path?

Instead of making the entire workflow a black box.

🖥️ Frontend Architecture

The frontend is organized around an AI workspace rather than a conventional chatbot.

                    AgentOS UI
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
    Dashboard       Workspace         Reports
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       Conversation Area      Agent Network
              │                   │
              ▼                   ▼
          Composer          Workflow Trace

Main interfaces

Dashboard

Provides the system overview and available capabilities.

Workspace

The main AI interaction environment with:

conversation

file upload

agent network

workflow visualization

AI responses

Analytics

Presents structured analysis results.

Reports

Provides:

generated reports

format information

timestamps

download

delete

Conversations

Provides persistent conversation navigation and restoration.

🧩 Engineering Decisions

1. Centralized orchestration

The Supervisor owns routing.

This avoids uncontrolled agent-to-agent dependencies.

2. Shared workflow state

Agents communicate through AgentState.

This creates a predictable contract and reduces coupling.

3. LLM + deterministic execution

LLMs handle language and planning.

Code handles deterministic operations such as data analysis and document/file management.

4. RAG grounding

Document questions use retrieved context instead of relying solely on general LLM knowledge.

5. Dedicated Document Agent

Report generation is separated from the source agents so the same document capability can be reused across RAG, Research and Analytics workflows.

6. Dedicated Memory Service

Conversation persistence is isolated from the AI reasoning layer.

7. Workflow trace

Execution information is returned to the frontend so users can understand which agents participated.

8. Feature isolation

Backend services, agents, prompts, workflows, schemas and frontend services are separated into clear responsibilities.

🛠️ Technology Stack

Layer

Technologies

Frontend

React, Vite, Tailwind CSS

UI / Visualization

React Flow, Lucide Icons

API

FastAPI

Orchestration

LangGraph

LLM

Groq — openai/gpt-oss-120b

RAG

ChromaDB, embeddings, retrieval pipeline

Data Processing

Pandas, NumPy

Persistence

SQLite, SQLAlchemy

Documents

PDF / DOCX generation

API Client

Axios

Markdown

React Markdown, Remark GFM

Development

Git, GitHub

🗂️ Project Structure

Agent-OS/
│
└── agentos-scaffold/
    │
    ├── backend/
    │   ├── agents/
    │   │   ├── base_agent.py
    │   │   ├── supervisor_agent.py
    │   │   ├── chat_agent.py
    │   │   ├── rag_agent.py
    │   │   ├── research_agent.py
    │   │   ├── analytics_agent.py
    │   │   └── document_agent.py
    │   │
    │   ├── api/
    │   │   └── v1/
    │   │       ├── router.py
    │   │       └── routes/
    │   │
    │   ├── database/
    │   ├── models/
    │   ├── prompts/
    │   ├── schemas/
    │   ├── services/
    │   ├── workflows/
    │   └── main.py
    │
    ├── frontend/
    │   ├── public/
    │   └── src/
    │       ├── components/
    │       ├── hooks/
    │       ├── pages/
    │       └── services/
    │
    └── README.md

🧪 Example End-to-End Workflows

Workflow 1 — General Question

"What is dependency injection?"

       ↓

Supervisor

       ↓

Chat Agent

       ↓

Final Response

Workflow 2 — Document Question

"What skills are mentioned in my resume?"

       ↓

Supervisor

       ↓

RAG Agent

       ↓

ChromaDB Retrieval

       ↓

Relevant Context

       ↓

LLM

       ↓

Grounded Answer

Workflow 3 — Document → Report

"Generate a professional report from my resume."

       ↓

Supervisor

       ↓

RAG Agent

       ↓

Retrieved Information

       ↓

Document Agent

       ↓

PDF / DOCX

       ↓

Reports Page

Workflow 4 — Dataset Analysis

"Find the average sales by region."

       ↓

Supervisor

       ↓

Analytics Agent

       ↓

Analysis Plan

       ↓

Pandas

       ↓

Computed Result

       ↓

LLM Explanation

       ↓

Final Answer

Workflow 5 — Analytics → Report

"Analyze this dataset and create a report."

       ↓

Supervisor

       ↓

Analytics Agent

       ↓

Structured Analysis

       ↓

Document Agent

       ↓

PDF / DOCX

🔌 API Surface

Endpoint

Purpose

GET /api/v1/health

Backend health check

POST /api/v1/chat

Execute an AgentOS request

POST /api/v1/upload

Upload files

POST /api/v1/analyze

Run analytics

GET /api/v1/conversations

List conversations

GET /api/v1/conversations/{id}

Retrieve conversation history

GET /api/v1/reports

List generated reports

GET /api/v1/reports/{id}/download

Download report

DELETE /api/v1/reports/{id}

Delete report

Interactive API documentation is available through FastAPI's Swagger interface.

🚀 Running AgentOS Locally

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Agent-OS/agentos-scaffold

2. Start the backend

cd backend
python -m venv .venv

Windows

.venv\Scripts\activate

macOS / Linux

source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure your environment variables in .env.

Start FastAPI:

uvicorn main:app --reload --port 8000

Backend:

http://localhost:8000

Swagger:

http://localhost:8000/docs

3. Start the frontend

Open another terminal:

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173

Configure the frontend API base URL to point to:

http://localhost:8000/api/v1

📸 Screenshots & Demo

Add your final project screenshots here after pushing the repository.

Recommended showcase order:

Dashboard — introduce AgentOS

Workspace — show the main AI interaction

Agent Network — show multi-agent architecture

RAG execution — show document-grounded Q&A

Analytics — show structured data analysis

Workflow trace — show actual agent execution

Generated report — show PDF/DOCX output

Reports page — show download/delete management

Conversation history — show persistence and restoration

Example:

## Demo

![AgentOS Dashboard](docs/screenshots/dashboard.png)

![AgentOS Workspace](docs/screenshots/workspace.png)

![AgentOS Workflow](docs/screenshots/workflow.png)

🧭 Development Journey

AgentOS was developed incrementally around a stable architecture.

Architecture Foundation
          ↓
LLM Service
          ↓
Supervisor
          ↓
Chat
          ↓
RAG
          ↓
Research
          ↓
Analytics
          ↓
Document Generation
          ↓
Memory / Conversations
          ↓
Workflow Visualization
          ↓
Reports Management
          ↓
Frontend Integration
          ↓
Testing
          ↓
Feature Freeze

The objective was not to create several disconnected AI demonstrations.

The objective was to integrate them into one coherent system with shared state, centralized orchestration, persistence, APIs and a user-facing workspace.

📈 Current Status

Core Platform

Multi-agent architecture

Supervisor routing

Shared AgentState

LangGraph workflow

FastAPI backend

React frontend

AI Capabilities

Chat Agent

RAG Agent

Research Agent

Analytics Agent

Document Agent

RAG & Documents

File upload

Document ingestion

Chunking

Embeddings

ChromaDB retrieval

Relevance filtering

Grounded answers

PDF generation

DOCX generation

Analytics

Intent-aware analysis planning

Structured analysis plan

Pandas execution

Human-readable analytical responses

Memory & Reports

Conversation persistence

Conversation restoration

New Chat

Conversation deletion

Report persistence

Report download

Report deletion

User Experience

Dashboard

Workspace

Agent Network

Workflow visualization

Reports UI

Loading states

Error handling

Empty states

Stability

Backend integration testing

Frontend/backend integration

Agent workflow testing

RAG testing

Analytics testing

Report generation testing

Conversation testing

Feature freeze

⚠️ Deployment Considerations

The current application uses local persistence for SQLite and ChromaDB.

For production deployment, persistent storage should be configured appropriately so generated data, conversation records and vector-store data are not lost when infrastructure is recreated.

The deployment architecture can therefore evolve independently from the core agent architecture.

🔮 Future Direction

The current version is intentionally feature-frozen around the implemented core capabilities.

Future experimentation should happen in separate branches so the stable version remains reproducible.

Potential future work includes:

advanced UI animations

richer workflow interactions

additional agent capabilities

broader document support

additional analytics visualizations

production-grade persistent infrastructure

deeper deployment automation

These are intentionally outside the current stable scope.

💡 Key Takeaway

AgentOS demonstrates how a modern AI application can move beyond:

Prompt → LLM → Answer

toward:

                     USER INTENT
                          │
                          ▼
                  ┌──────────────┐
                  │  SUPERVISOR  │
                  └───────┬──────┘
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
         RAG          ANALYTICS         RESEARCH
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                     DOCUMENT
                          │
                          ▼
                    PDF / DOCX

          + Conversation Memory
          + Workflow Trace
          + Persistent Reports
          + React Workspace

The result is a single application where multiple specialized AI capabilities are orchestrated as one system.

<div align="center">

AgentOS

From user intent to intelligent execution.

Built with Python · FastAPI · LangGraph · React · ChromaDB · SQLite · Groq

<br/>

Chandu · B.Tech Artificial Intelligence & Machine Learning

</div>
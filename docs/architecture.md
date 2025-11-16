# Landing Agents Platform — Solution Architecture Document

## 1. Introduction

### 1.1 Purpose of the Document

This document describes the **solution architecture** for the **Landing Agents Platform** (“Landing Agents”) — a conversational, agentic alternative to traditional landing pages.

It defines the high-level design, components, data flows, and integration patterns required to:

* Engage visitors with **human-like conversations**
* Capture and qualify leads with **zero-friction**
* Recommend relevant solutions (bundles/plans)
* Book meetings and trigger downstream **sales workflows**
* Continuously learn from conversations to improve conversion

### 1.2 Scope

**In scope (Phase 1):**

* Web-based conversational widget (“Landing Agent widget”)
* Multi-agent conversation engine with:

  * Lead capture & profiling
  * Conversational sales & objection handling
  * BANT+ qualification & scoring
  * Use-case → bundle/plan recommendation
  * Inline information delivery (pricing, docs, videos)
  * Meeting booking & handoff
  * Nurture follow-ups (Email/WhatsApp)
* Memory & personalization across sessions
* Analytics and insights for GTM/sales teams
* MCP-based integration with:

  * RAG/content
  * CRM
  * Calendar
  * Messaging
  * Analytics
  * Experiments

**Phase 2+ (future):**

* Workflow automation (e.g., POC onboarding) via MCP workflow server
* Additional channels (WhatsApp, in-app chat, maybe voice)
* Richer semantic memory & multi-agent collaboration with support/CS agents

### 1.3 Definitions & Terminology

* **Landing Agent** – The conversational agent that replaces or augments a landing page.
* **Session** – A contiguous interaction between a visitor and the platform.
* **Visitor** – Anonymous user, tracked with a browser-generated `visitor_id`.
* **User** – Identified person (e.g., email / SSO) with `user_id`.
* **Lead** – A visitor/user that has been profiled and synced to CRM.
* **Episode** – A coherent sub-goal within a session (e.g., “understand needs”, “explain pricing”).
* **Thread** – Topic-specific lane such as `pricing`, `security`, `integration`.
* **MCP** – Model Context Protocol; used for server-side tools (RAG, CRM, etc.).
* **Tool** – An MCP-exposed capability (e.g., `crm.upsert_lead`, `rag.search_docs`).
* **Workflow** – Multi-step automation (e.g., “start POC onboarding”).

### 1.4 Audience

* **Engineering & Architecture** – implementing backend, MCP servers, client widget.
* **Product & Design** – shaping flows, UX, and business logic.
* **Sales & RevOps** – integrating with CRM and understanding insights.
* **Data & Analytics** – configuring event models and dashboards.
* **DevOps/SRE & Security** – handling infra, reliability, and compliance.

---

## 2. Business Context & Goals

### 2.1 Problem Statement

Most landing pages are static and passive: they present information but do not **actively discover** what the visitor wants, nor do they **qualify, recommend**, or **book**. Lead forms often have high drop-off, resulting in:

* Low conversion to demo or trial
* Poor quality of captured data (missing context, no qualification)
* Fragmented systems (website analytics separated from CRM, calendar, etc.)

### 2.2 Objectives

Landing Agents aims to:

* Replace static landing pages with **intelligent, conversational agents** that behave like a human SDR.
* Provide **zero-friction lead capture** and **structured profiling** (BANT+).
* Drive higher **meeting bookings & POC starts**.
* Consolidate conversation and lead data into **single source-of-truth** (CRM + analytics).
* Continuously improve via **experimentation** and **insights** from real conversations.

### 2.3 KPIs & Success Metrics

* Visitor → Qualified lead conversion rate
* Visitor → Booked meeting conversion rate
* % of leads with complete BANT fields
* Average time-to-first-value (first useful answer/card)
* Objection resolution rate (objection → booked or nurtured)
* Reply rate to nurture follow-ups
* Net impact on pipeline/revenue attributable to Landing Agents

---

## 3. Requirements

### 3.1 Functional Requirements

1. **Lead Capture & Profiling**

   * Greet visitors conversationally.
   * Collect name, role, company, and contact details with minimal friction.
   * Detect needs and pain points from open text.

2. **Intent Detection & Routing**

   * Classify intents (pricing, demo, integrations, security, ROI, support, general).
   * Route conversation to appropriate specialist agent.

3. **Conversational Sales**

   * Explain offerings in simple, layered fashion.
   * Tailor narrative to industry, segment, and persona.
   * Handle comparisons and highlight differentiation.

4. **Qualification & Scoring**

   * Apply BANT+ logic (Budget, Authority, Need, Timeline + fit).
   * Infer where possible; ask questions only when necessary.
   * Compute a lead score and push to CRM.

5. **Recommender (Use-case → Bundle/Plan)**

   * Map expressed/inferred needs to best-fit bundles or plans.
   * Provide explanation, evidence (case study, security, ROI), and CTA.

6. **Objection Handling**

   * Detect and classify objections.
   * Respond with concise evidence and options (e.g., pilot vs full).

7. **Inline Information Delivery**

   * Provide pricing, comparisons, case studies, videos, PDFs inside chat (no page hopping).

8. **Meeting Booking & Handoff**

   * Suggest available time slots; book meetings via calendar.
   * Send confirmation emails; update CRM & internal channels.

9. **Nurture & Follow-ups**

   * Send follow-up emails/WhatsApp messages (summary, case studies, ROI).
   * Respect consent and opt-out.

10. **Memory & Personalization**

    * Remember visitors across sessions.
    * Use profile and history to personalize greetings, topics, and recommendations.

11. **Context Switching & Parallel Conversations**

    * Support multiple threads (pricing vs security) within a session.
    * Allow user to change topics gracefully, while preserving context.

12. **Analytics & Insights**

    * Capture events across the funnel.
    * Provide analysis of intents, objections, performance by variant, etc.

13. **Workflow Automations (Phase 2)**

    * Start workflows like POC onboarding or proposal generation after qualification.

### 3.2 Non-functional Requirements

* **Latency:**

  * P50 response < 1.5 s (with retrieval & tools).
  * P95 < 3.5 s for typical flows (without long external latencies).
* **Availability:** Target ≥ 99.5% for production.
* **Scalability:** Support thousands of concurrent sessions across tenants.
* **Multi-tenancy:**

  * Strict tenant isolation in data and configuration.
  * Per-tenant RAG indexes and flags.
* **Security & Privacy:**

  * Encryption in transit and at rest.
  * PII minimization and controlled retention.
  * Region-specific data residency when required.
* **Observability:**

  * Full logging, metrics, and distributed tracing of agent and tool calls.

### 3.3 Constraints & Assumptions

* Using MCP as the primary protocol to expose server-side tools.
* Existing CRM/Calendar systems (e.g., HubSpot, Salesforce, Google/Microsoft Calendar) will be integrated via MCP servers.
* LLM/SLM models may be a combination of managed APIs and self-hosted models, but the architecture must remain provider-agnostic.
* Deployment assumed on a major cloud provider (AWS/Azure).

---

## 4. High-Level Architecture

### 4.1 System Context

At a high level, the system includes:

* **Client:** Landing Agent widget embedded on websites and possibly other channels (WhatsApp, in-app chat).
* **Backend Gateway & Session Service:** Entry point for requests, managing session IDs and authentication/tenant context.
* **Conversation Engine:** LLM-driven, agentic orchestration layer.
* **MCP Client:** Used by the Conversation Engine to talk to multiple MCP servers exposing tools.
* **MCP Servers:** RAG, CRM, Calendar, Messaging, Analytics, Feature Flags, Workflow.
* **Data Stores:** Session KV (Redis), Profiles & Leads (Postgres/CRM), Vector store (Qdrant/PGVector), Events/Analytics (ClickHouse/BigQuery).

### 4.2 Layered Architecture

1. **Experience Layer**

   * Web-based widget with chat UI, cards, CTAs.
   * Channel connectors for WhatsApp / in-app chat (future).

2. **Conversation Layer**

   * Conversation Engine (Director + 13 specialist agents).
   * State management & memory.
   * Guardrails and compliance logic.

3. **MCP Tooling Layer**

   * MCP client integrated with Conversation Engine.
   * Multiple MCP servers with well-defined tool schemas.

4. **Data & Workflow Layer**

   * Knowledge content & RAG index.
   * CRM/lead/profile data.
   * Analytics and events.
   * Workflow orchestration (Phase 2).

### 4.3 Design Principles

* **Agentic & Tool-based:** Agents reason with LLMs and act via tools.
* **MCP-first:** All external capabilities exposed as MCP tools.
* **Stateless Compute, Stateful Storage:** Conversation Engine is stateless; session/profile/analytics in stores.
* **Config & Policy Driven:** Tenant-specific behavior via config rather than code forks.
* **Security & Compliance by Design:** Consent, redaction, audit trails built-in.

---

## 5. Conversation Engine & Agent Graph

### 5.1 Agentic Design Overview

The Conversation Engine consists of:

* A **Director/Orchestrator**, responsible for:

  * Selecting which agent to run next.
  * Maintaining high-level phase (GREET, DISCOVER, QUALIFY, RECOMMEND, OBJECTION, CTA, HANDOFF/BOOK, FOLLOW-UP).
  * Handling retries and fallbacks.

* **13 Specialist Agents**, each focused on a narrow responsibility:

  * Greeter & Zero-Friction Profiler
  * Intent & Need Router
  * SDR (Conversational Sales)
  * Qualifier & Scorer (BANT+)
  * Recommender & Solution Mapper
  * Objection Handler
  * Info Delivery & Card Composer
  * Meeting & Handoff
  * Nurture & Follow-up
  * Insights & Analytics
  * Experiment Controller
  * Compliance & Privacy Guard
  * Memory & Context Manager

Each agent can call MCP tools, read/write conversation state, and return:

* A response (message + rich cards)
* Updated state (phase, slots, threads, score)
* Suggested next agent or phase

### 5.2 Conversation State Model

Key entities:

* `session_id`: Unique per conversation instance.
* `visitor_id`: Cookie/localStorage-based identifier across sessions.
* `user_id`: Known identity (email/SSO ID) when provided.

**ConversationState (simplified):**

```json
{
  "session_id": "s_123",
  "visitor_id": "v_abc",
  "user_id": "u_xyz",
  "tenant_id": "tenant_1",
  "phase": "RECOMMEND",
  "active_thread": "pricing",
  "threads": {
    "pricing": { "last_doc_ids": ["doc1"], "last_cta": "see_case_study" },
    "security": { "last_doc_ids": ["doc7"], "last_cta": "read_security_pdf" }
  },
  "lead_profile": {
    "name": "Alex",
    "company": "Acme Bank",
    "industry": "BFSI",
    "budget_band": "mid",
    "timeline": "< 3 months",
    "score": 0.78
  },
  "experiment_variant": { "greeting": "B", "cta_layout": "A" },
  "context_ids": ["card_pricing_v2", "faq_security_1"]
}
```

### 5.3 Agent Graph & State Transitions

Typical flow:

1. **GREET** – Greeter agent welcomes and lightly profiles.
2. **DISCOVER** – Intent & Need Router + SDR dig into needs.
3. **QUALIFY** – Qualifier agent gathers BANT+ info and scores.
4. **RECOMMEND** – Recommender proposes bundle/plan solutions.
5. **OBJECTION** – Objection Handler responds to concerns.
6. **CTA** – Info Delivery or SDR present clear call-to-actions.
7. **HANDOFF/BOOK** – Meeting & Handoff agent books a meeting.
8. **FOLLOW-UP** – Nurture agent schedules follow-up messaging.

The Director enforces:

* Phase transitions based on agent outputs and scoring.
* Loop-breakers (avoid endless back-and-forth without CTA).
* Safe fallback (e.g., “short summary + request email”) if tools/LLM misbehave.

### 5.4 Specialist Agent Definitions

You already have concise role/goal/flow definitions for all 13 agents; these are used as:

* **Design references** for engineers.
* **Prompt scaffolds** for LLM behavior.
* **Policy documents** for each agent’s boundaries.

### 5.5 Prompting & Policies

* **Global system prompt**:

  * Defines brand tone, safety constraints, and general behavior (e.g., “Always answer in two layers: TL;DR + Details. Never ask for contact info before delivering value and confirming consent.”).

* **Agent-specific prompts**:

  * Greeter: gentle, low friction, no “interrogation” style.
  * Qualifier: one question at a time, prefer inference.
  * Objection: classify objection, give concise proof + options.
  * Meeting: propose 2–3 times in user’s timezone.

* **Guardrails & Hard Rules**:

  * No medical/legal/financial advice beyond allowed scope.
  * No unsupported claims about performance or compliance.
  * Respect consent and privacy rules.

---

## 6. MCP-Based Tooling Architecture

### 6.1 MCP Client in Conversation Engine

The Conversation Engine embeds an **MCP client runtime**:

* Agents do not call external REST APIs directly.
* Instead, they call **MCP tools**, which are strongly-typed and discoverable.
* The MCP client handles:

  * Tool discovery and schema loading.
  * Transport (e.g., WebSocket/HTTP) to MCP servers.
  * Timeouts, retries, and error propagation.

### 6.2 MCP Servers & Tools

Each domain (RAG, CRM, etc.) is implemented as a separate MCP server with tools.

#### 6.2.1 RAG Server

**Purpose:** Provide contextual knowledge (services, pricing, case studies, FAQs).

**Tools:**

* `rag.search_docs(query, filters, top_k)`
* `rag.get_doc(doc_id)`

**Backing Storage:**

* Content store (S3/Blob) + vector DB (Qdrant/PGVector).

#### 6.2.2 CRM & Lead Server

**Purpose:** Manage lead profiles and activities.

**Tools:**

* `crm.upsert_lead(profile)`
* `crm.get_lead_by_email(email)`
* `crm.append_activity(lead_id, activity)`

Backed by CRM (HubSpot/Salesforce/Zoho) via their APIs.

#### 6.2.3 Calendar & Meetings Server

**Purpose:** Suggest and book meeting slots.

**Tools:**

* `calendar.suggest_slots(attendees, constraints)`
* `calendar.book(slot, attendees, meta)`

Backed by Google/Microsoft calendar APIs.

#### 6.2.4 Messaging Server (Email/WhatsApp)

**Purpose:** Send transactional/nurture messages.

**Tools:**

* `messaging.send_email(template_id, vars)`
* `messaging.send_whatsapp(template_id, vars)`

Backed by providers like SendGrid/Twilio.

#### 6.2.5 Analytics & Insights Server

**Purpose:** Log and query behavioral and performance data.

**Tools:**

* `analytics.log_event(event)`
* `analytics.get_funnel_stats(filters)`

Backed by ClickHouse/BigQuery and dashboarding tools.

#### 6.2.6 Feature Flags & Experiment Server

**Purpose:** Run experiments on prompts, CTAs, layouts.

**Tools:**

* `experiment.get_variant(surface, user_hash)`
* `experiment.log_outcome(surface, variant, event)`

Backed by feature flagging system (e.g., LaunchDarkly / custom service).

#### 6.2.7 Workflow Orchestrator Server (Phase 2)

**Purpose:** Trigger and track multi-step workflows.

**Tools:**

* `workflow.start(process_name, input)`
* `workflow.get_status(process_id)`

Backed by a workflow engine (e.g., Temporal, Camunda, or custom job system).

### 6.3 Tool Schemas & Contracts

* Each tool has a JSON schema for input and output.
* Errors are structured (e.g., `code`, `message`, `retryable`).
* Versioning strategy (e.g., `rag.search_docs.v2`) to allow backward-compatible updates.

---

## 7. Data Architecture & Storage

### 7.1 Identity & Profile Model

* `visitor_id` – anonymous, cookie-based, persists across sessions on the same browser.
* `user_id` – known identity, tied to email / SSO; can span devices.
* `session_id` – scoped to one chat instance (tab or active chat).

Relationships:

* 1 `visitor_id` → many `session_id`s
* 1 `user_id` → many `visitor_id`s (cross-device)

### 7.2 Memory Layers

#### 7.2.1 Short-Term (Session Memory)

* Storage: Redis (or equivalent KV store).
* Contains:

  * Current phase, active thread, thread contexts.
  * Partial lead_profile (e.g., gathered fields so far).
  * Experiment variants.
  * temp states like “awaiting answer to this specific question”.

TTL: configurable (e.g., 24 hours – 7 days).

#### 7.2.2 Mid-Term (Lead/Profile Memory)

* Storage: Postgres (internal profile DB) + CRM (external).
* Contains:

  * `lead_profile` with BANT+ fields.
  * Segments, preferences (language, channel, brevity vs detail).
  * Last important conversation topics & outcomes.

Used to personalize revisits and multi-session interactions.

#### 7.2.3 Long-Term (Semantic Memory)

* Storage: Vector DB (optional but powerful).
* Contains:

  * Embeddings of important user interactions (e.g., key pain points, custom setups).
* Enables queries like:

  * “What did we discuss with this user about compliance last time?”

### 7.3 Content & Knowledge Stores

* Canonical source for:

  * Services / products and their capabilities.
  * Pricing and plan descriptions.
  * Case studies and customer stories.
  * Security & compliance docs.
  * FAQs.

RAG pipelines transform PDF/HTML/MD into chunks with metadata, embed them, and sync into vector store.

### 7.4 Events & Analytics

* All interaction events (turn events, tool calls, CTAs clicked) are logged via `analytics.log_event`.
* Stored in an append-only event table, then aggregated into:

  * Funnels by surface/variant.
  * Objection categories.
  * Intents and their conversion performance.

### 7.5 Data Lifecycle & Retention

* Session KV: short TTL (24h–7d).
* Logs & events: retention based on compliance (e.g., 12–24 months).
* PII: retention per contract/policy; support deletion on request.

---

## 8. Experience Layer & Client Integration

### 8.1 Landing Widget (Web)

* Delivered via a small script `<script src=".../landing-agent.js"></script>`.
* Initializes with `tenant_id`, theme, and optional config.
* Supports:

  * Chat window with streaming responses.
  * Quick-replies (chips).
  * Rich cards (pricing tables, videos, PDFs, case studies, slot pickers).
  * CTAs (buttons to start flows like “Book demo”, “Email me this”).

### 8.2 Channel Adapters

* **WhatsApp / SMS** (Phase 2):

  * Messages via Twilio / similar.
  * Limited card richness; fallback to links and short text.

* **In-App Chat**:

  * Same API as web widget; just different UI container.

### 8.3 Session & Identity Handling on Client

* `visitor_id` stored in cookie/localStorage.
* `session_id` generated per chat instance.
* If user logs in or shares email, a `user_id` token can be attached.
* UTM and other traits (referrer, device type, locale) are passed as metadata.

### 8.4 UI Patterns

* **Greeting**: minimal, friendly, one or two chips for common intents.
* **Progressive disclosure**: show summary first, details on tap.
* **Inline actions**: click CTA in card instead of jumping pages.
* **Accessibility & Localization**: ARIA roles, keyboard support, multiple languages.

---

## 9. Key Flows & Sequence Diagrams (Conceptual)

### 9.1 New Visitor, Anonymous Session

1. Widget loads, generates `session_id`, `visitor_id` (if not present).
2. Greeter agent welcomes visitor.
3. Intent Router tags message (e.g., “I’m exploring AI compliance features”).
4. SDR explains offerings and ties them to user’s context.
5. Qualifier asks minimal questions, infers BANT fields.
6. Recommender proposes one or two bundle/plan options.
7. Info Delivery agent shows relevant case study or pricing.
8. Meeting agent offers to book demo; if accepted, uses Calendar tools.
9. CRM tools upsert the lead and log the activity.

### 9.2 Returning Visitor with Personalization

1. Widget initializes with known `visitor_id`; backend checks if it can map to a `user_id`.
2. Memory & Context Manager loads profile & past topics.
3. Greeter adapts messaging, e.g., “Welcome back, last time we spoke about BFSI compliance and pricing. Continue there or start something new?”
4. Conversation continues with context-aware flows.

### 9.3 Inline Information Delivery

* User: “Can you show me your pricing options?”
* Intent Router → Info Delivery agent.
* Info Delivery agent uses RAG and card renderer to show a pricing table inline.
* Followed by CTA: “Want to see how this maps to your specific use-case?”

### 9.4 Qualification & Meeting Booking

* Qualifier agent builds BANT+ profile and computes score.
* If score >= threshold, Meeting agent:

  * Calls `calendar.suggest_slots`.
  * Presents 2–3 slots as buttons.
  * On selection, calls `calendar.book` and sends confirmation via Messaging.
  * CRM updated with meeting details & conversation summary.

### 9.5 Context Switching (Parallel Topics)

* User: “Okay, price looks fine. But how do you handle data residency?”
* New intent: `security/compliance`; Memory agent either starts or switches to `thread:security`.
* Info Delivery/SDR use RAG to answer; conversation can later return to pricing or booking with shared context.

### 9.6 Workflow Automation (Phase 2)

* After booking or high-intent confirmation:

  * Recommender or Meeting agent calls `workflow.start('poc_onboarding', {...})`.
  * Workflow server orchestrates environment setup, internal notifications, etc.
  * Nurture agent can later query `workflow.get_status` to update the user.

---

## 10. Personalization, Context & Parallel Conversations

### 10.1 Profile-based Personalization

* Use profile fields (industry, segment, region, role, priorities) to:

  * Choose examples/case studies.
  * Adapt depth and technicality.
  * Decide which plans to propose first.

### 10.2 Threads & Context Switching

* Each `thread_id` corresponds to a topic or goal.
* Memory agent maintains per-thread context:

  * Last cards shown.
  * Relevant docs.
  * Last CTA.

This allows:

* Jumping between topics without losing track.
* Avoiding repetition within a thread (no repeating the same security doc).

### 10.3 Parallel Sessions Across Devices

* Multiple concurrent `session_id`s may exist for one `user_id`.
* Profile is shared; session memory is per session.
* Lead/Profile updates propagate to all new sessions.

### 10.4 Cross-Session Continuity

* Key outcomes and topics are stored in profile, enabling:

  * “Follow-up chat” after an email click.
  * Personalized suggestions like: “Last time we didn’t finalize a slot; want to book now?”

---

## 11. Security, Privacy & Compliance

### 11.1 Threat Model & Risks

* Prompt injection / model exploitation.
* PII leakage in logs or across tenants.
* Misuse of messaging tools (spam).
* Unauthorized access to CRM/Calendar data.

### 11.2 Access Control & Tenant Isolation

* All requests carry `tenant_id`.
* Separate RAG indexes per tenant; no cross-tenant document retrieval.
* Tool credentials scoped per tenant (e.g., CRM API keys).

### 11.3 Data Protection

* TLS for all network communication.
* Encryption at rest for DBs and KV stores.
* PII detection and redaction before logging.

### 11.4 Consent & Policy Enforcement

* Compliance & Privacy Guard agent enforces:

  * Consent before storing / using contact details.
  * Region-specific policy boundaries (e.g., EU data residency).

### 11.5 Audit & DSAR Support

* Key actions logged (lead created, meeting booked, messages sent).
* Ability to search/export/delete user data by email or user ID.

---

## 12. Observability & Quality

### 12.1 Logging & Tracing

* Structured logs for every request, tool call, and agent decision.
* Correlation IDs per session and per tenant.
* Distributed tracing to diagnose latency and failures.

### 12.2 Metrics

* Infra metrics: CPU, memory, error rates.
* LLM/tool metrics: token usage, tool call frequency, failed calls.
* Business metrics: conversion rates, completion rates per phase.

### 12.3 Sales & Product Analytics

* Funnel analytics: from first message to meeting booked.
* Per-intent and per-variant performance.
* Objection classification counts and resolution rates.

### 12.4 Evaluation & Testing Framework

* Golden conversation sets per vertical (BFSI, SaaS, etc.).
* Automated retrieval evaluations (hit@k).
* Regression tests for prompts when updating them.
* Synthetic and real conversation replay tests.

---

## 13. Deployment & DevOps

### 13.1 Environment Topology

* **Dev** – rapid iteration, mock CRM/calendar.
* **Staging** – integrated with real sandboxes for CRM/calendar.
* **Prod** – high-availability, multi-tenant.

MCP servers are deployed as independent services, each horizontally scalable.

### 13.2 Scaling Strategy

* Conversation Engine runs in stateless pods with HPA (Kubernetes).
* MCP servers scale independently:

  * RAG server CPU/memory tuned for retrieval.
  * CRM/calendar connectors tuned based on external API limits.

### 13.3 CI/CD Pipeline

* Code and prompts managed in version control.
* Automated tests (unit, integration, evals) in CI.
* Canary or blue-green deployment for major changes (especially prompts and tools).

### 13.4 Configuration & Secrets Management

* Per-tenant configuration (plans, RAG sources, experiments) as config-as-code (YAML/JSON).
* Secrets (API keys, access tokens) stored in cloud KMS/Vault.

---

## 14. Extensibility & Roadmap

### 14.1 New Channels

* Voice assistant integration (phone-based IVR agent).
* In-product agents embedded in SaaS dashboards.

### 14.2 New Tools & MCP Servers

* Billing / payments (e.g., Stripe) for instant trial sign-ups.
* E-signature (DocuSign/Adobe Sign) for quick contract flows.
* Additional CRMs (Pipedrive, Close.io).

### 14.3 Advanced Workflow Automation

* Multi-step onboarding workflows with Tasks for internal teams.
* Deeper integration into ticketing/support systems for post-sale.

### 14.4 Multi-Agent Collaboration

* Coordination between Landing Agent and support/CS Agent, sharing state via MCP and profile memory.

---

## 15. Open Questions & Decisions

* Final LLM/SLM stack and hosting strategy (fully managed vs hybrid vs on-prem for banks).
* Exact data retention durations per tenant/region and contracts.
* Priority order for supported CRMs and calendars.
* How aggressively to store semantic memory at user-level (privacy vs personalization).
* Granularity of experiments (surface-level vs multi-step flows).

---


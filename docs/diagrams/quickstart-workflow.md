# 🚀 7-Step Quickstart Workflow Diagram

> **Visual Flowchart of the Aegis Forge 7-Step Development Journey** — from project clone to secure production commit.

---

## 🎨 Visual Diagram (Vector SVG)

![Aegis Forge 7-Step Workflow](quickstart-workflow.svg)

---

## 📊 Mermaid Flowchart

```mermaid
flowchart TD
    %% Styling and Classes
    classDef cyanCard fill:#0f172a,stroke:#0284c7,stroke-width:2px,color:#f8fafc;
    classDef purpleCard fill:#0f172a,stroke:#7c3aed,stroke-width:2px,color:#f8fafc;
    classDef greenCard fill:#0f172a,stroke:#059669,stroke-width:2px,color:#f8fafc;
    classDef amberCard fill:#0f172a,stroke:#d97706,stroke-width:2px,color:#f8fafc;

    subgraph PHASE1 ["Phase 1: Project Setup & Scaffolding"]
        S1["📦 <b>Step 1: Clone Baseline</b><br/><code>git clone</code> or VS Code Dev Container"]:::cyanCard
        S2["🧙‍♂️ <b>Step 2: Run Setup Wizard</b><br/><code>init-new-project.sh</code><br/><i>Auto skeleton & keys</i>"]:::cyanCard
    end

    subgraph PHASE2 ["Phase 2: Specification & AI Planning"]
        S3["🎙️ <b>Step 3: Prompt & PRD Interview</b><br/>Describe app in <code>AI-AGENT-PROMPT.md</code><br/><i>AI interviews for PRD & UI</i>"]:::purpleCard
        S4["📋 <b>Step 4: Break into Tasks</b><br/><code>spec-to-tasks</code> → <code>docs/TASKS.md</code><br/><i>Explicit skeleton_hint per task</i>"]:::purpleCard
    end

    subgraph PHASE3 ["Phase 3: Runtime & Development"]
        S5["🚀 <b>Step 5: Launch Stack</b><br/><code>make first-run</code><br/><i>Backend live at localhost:8000</i>"]:::greenCard
        S6["💻 <b>Step 6: Build with AI</b><br/>AI edits existing skeleton code<br/><i>Complies with AGENTS.md</i>"]:::greenCard
    end

    subgraph PHASE4 ["Phase 4: Security Verification"]
        S7["🛡️ <b>Step 7: Audit & Commit</b><br/><code>make audit && git commit</code><br/><i>Protected by Gitleaks hook</i>"]:::amberCard
    end

    %% Flow connections
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 ==>|Stack Ready| S5
    S5 --> S6
    S6 --> S7
```

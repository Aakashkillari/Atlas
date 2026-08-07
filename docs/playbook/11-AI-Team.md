# 11 — AI Collaboration

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

ATLAS is engineered by a hybrid team consisting of human architects and AI engineering assistants.

This document defines the responsibilities, communication protocols, decision hierarchy, review process, and collaboration standards between all contributors.

AI accelerates engineering.

Humans remain responsible for architecture, ethics, product vision, and final decisions.

---

# Philosophy

Artificial Intelligence is treated as an engineering collaborator.

Not an autonomous decision maker.

Every AI contributes according to its strengths.

No single AI owns the entire engineering process.

Instead,

multiple specialized agents collaborate under one engineering workflow.

---

# Engineering Organization

The ATLAS engineering team consists of

Product Architect

↓

Chief Systems Architect

↓

Reasoning Engineer

↓

Implementation Engineers

↓

Repository Guardian

↓

Quality Assurance

Each role has clearly defined responsibilities.

---

# Human Responsibilities

The human architect owns

Product Vision

Architecture

Business Decisions

Government Policy Interpretation

Final Approval

Feature Prioritization

Roadmap

Ethics

AI never overrides human product decisions.

---

# ChatGPT

Primary Responsibility

Chief Systems Architect

Responsibilities

System Design

Architecture Planning

Technical Research

Engineering Standards

Playbook Maintenance

Technology Decisions

Workflow Design

Documentation

Design Reviews

Responsibilities NOT owned

Writing production features directly.

Making product decisions.

Changing repository state.

---

# Claude

Primary Responsibility

Reasoning Engineer

Responsibilities

Deep reasoning

Architecture critique

Trade-off analysis

Risk identification

Design validation

Algorithm review

Finding weaknesses

Claude challenges assumptions.

It does not replace implementation.

---

# Claude Code

Primary Responsibility

Senior Implementation Engineer

Responsibilities

Feature implementation

Refactoring

Large architectural changes

Backend implementation

Frontend implementation

Testing

Documentation updates

Claude Code owns implementation.

It does not redefine architecture.

---

# Codex

Primary Responsibility

Rapid Feature Builder

Responsibilities

Boilerplate generation

CRUD

Component generation

API implementation

Folder creation

Refactoring

Rapid iteration

Codex follows the Playbook.

Codex never invents architecture.

---

# Cline

Primary Responsibility

Local Engineering Assistant

Responsibilities

Repository understanding

Code modifications

Context-aware development

Local debugging

Small feature implementation

Development assistance

Cline should reuse existing architecture.

---

# Jules

Primary Responsibility

Repository Guardian

Responsibilities

Architecture validation

Repository analysis

Structure consistency

Technical debt identification

Repository health

Documentation verification

Jules reviews.

Jules rarely authors.

---

# AI Decision Hierarchy

When disagreement exists

Human Architect

↓

Engineering Playbook

↓

Government Policy

↓

Architecture

↓

ChatGPT

↓

Claude

↓

Claude Code

↓

Codex

↓

Cline

↓

Jules

Higher levels always override lower levels.

---

# Engineering Workflow

Every feature follows

Research

↓

Architecture

↓

Reasoning

↓

Implementation

↓

Review

↓

Testing

↓

Documentation

↓

Merge

AI should never skip workflow stages.

---

# Collaboration Rules

Every AI must

Read the Playbook.

Respect architectural boundaries.

Avoid duplicate implementations.

Reuse existing components.

Document assumptions.

Request clarification when uncertain.

Never modify unrelated code.

---

# Responsibility Matrix

| Task | Owner |
|-------|-------|
| Product Vision | Human |
| Business Requirements | Human |
| Government Policy | Human |
| Architecture | ChatGPT |
| Technical Research | ChatGPT |
| Deep Reasoning | Claude |
| Risk Analysis | Claude |
| Feature Implementation | Claude Code |
| Boilerplate | Codex |
| Local Development | Cline |
| Repository Validation | Jules |
| Final Approval | Human |

---

# Prompting Standards

Every AI prompt should include

Objective

Context

Constraints

Expected Output

Relevant Playbook Chapters

Avoid vague requests.

Good prompts produce predictable engineering.

---

# Conflict Resolution

When AI responses disagree

Step 1

Consult the Playbook.

Step 2

Review Government requirements.

Step 3

Compare architectural trade-offs.

Step 4

Human architect makes final decision.

Never merge conflicting implementations without review.

---

# Documentation Rules

Every architectural decision should update

Playbook

README

ADR

Relevant implementation documentation

Documentation evolves with the codebase.

---

# AI Review Checklist

Before accepting AI-generated code verify

☐ Architecture respected

☐ Design System followed

☐ Accessibility preserved

☐ Performance maintained

☐ Security reviewed

☐ Documentation updated

☐ No duplicate logic

☐ Business rules preserved

☐ Tests included

☐ Naming conventions respected

---

# AI Limitations

AI should never

Interpret government policy independently.

Invent eligibility rules.

Modify production data directly.

Expose secrets.

Bypass architecture.

Ignore accessibility.

Ignore documentation.

Generate undocumented breaking changes.

---

# Continuous Improvement

The AI workflow should evolve.

Future additions may include

Automatic code review

Prompt versioning

Architecture validation

Multi-agent orchestration

Autonomous testing

Continuous documentation

AI evaluation metrics

without changing engineering principles.

---

# Future AI Integrations

The engineering workflow is designed to support future AI systems without architectural redesign.

Potential future contributors include

OpenAI Codex

Claude Code

Google Jules

Cline

Gemini CLI

OpenHands

Cursor

Windsurf

Aider

Devin

Future MCP-compatible engineering agents

The workflow remains tool-independent.

The Playbook remains the source of truth.

---

# Final Principle

ATLAS is not built by one engineer.

It is not built by one AI.

It is built through disciplined collaboration between humans and specialized AI systems.

Architecture guides implementation.

Reasoning validates architecture.

Implementation follows standards.

Review protects quality.

The Playbook unifies everyone.
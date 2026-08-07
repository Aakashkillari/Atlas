# 05 — AI System

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

The AI System provides intelligent assistance throughout ATLAS while preserving fairness, transparency, explainability, and government policy compliance.

Artificial Intelligence assists decision making.

Artificial Intelligence never replaces governance.

The AI System exists to

- Improve matching quality.
- Explain recommendations.
- Assist users.
- Reduce manual effort.
- Learn from outcomes.
- Support government decision making.

The AI System is never the source of truth.

Government policy remains the source of truth.

---

# AI Philosophy

ATLAS follows a simple philosophy.

Rules before AI.

Policy before prediction.

Explainability before intelligence.

Trust before automation.

Every AI decision must be explainable.

Every AI recommendation must be auditable.

Every AI suggestion must remain optional unless validated by deterministic rules.

---

# AI Architecture

The AI System is divided into independent layers.

User Request

↓

Policy Engine

↓

Eligibility Engine

↓

AI Ranking Engine

↓

Fairness Layer

↓

Explainability Layer

↓

Human Review

↓

Final Allocation

Every layer has a specific responsibility.

---

# Deterministic Policy Engine

Purpose

Enforce government policy.

Responsibilities

Eligibility.

Qualification.

Reservation.

Capacity.

Internship rules.

Application limits.

Timeline validation.

Location constraints.

The Policy Engine always executes before AI.

Nothing bypasses this layer.

---

# Eligibility Engine

Determines whether a candidate is eligible.

Examples

Academic qualification.

Age.

Required documents.

Internship availability.

Government eligibility.

Only eligible candidates proceed to AI ranking.

---

# AI Ranking Engine

Purpose

Rank eligible opportunities.

Never determine eligibility.

Inputs

Skills

Interests

Education

Location

Languages

Experience

Sector preference

Career goals

Resume embeddings

Outputs

Ranked opportunities.

Confidence score.

Matching explanation.

Ranking is advisory.

Not authoritative.

---

# Semantic Matching

Semantic similarity is performed using embeddings.

Potential sources

Resume

Internship description

Skills

Projects

Experience

Candidate interests

Cosine similarity should assist ranking.

Never replace policy.

---

# Allocation Engine

The allocation engine is separate from ranking.

Purpose

Generate globally optimal allocations.

Preferred algorithm

Hungarian Algorithm.

Future algorithms

Stable Matching.

Constraint Optimization.

Linear Programming.

The allocation engine receives ranked candidates.

It does not generate rankings.

---

# Fairness Layer

Purpose

Evaluate allocation fairness.

Responsibilities

Bias detection.

Distribution monitoring.

Affirmative action support.

Regional balance.

Opportunity equality.

Fairness adjusts allocation strategy.

It never violates government policy.

---

# Explainability Layer

Every recommendation must answer

Why was this recommended?

Which factors contributed?

What reduced the score?

How confident is the system?

Every explanation should be understandable by non-technical users.

---

# Recommendation Factors

Possible factors

Skill Match

Education Match

Language Match

Location Match

Industry Preference

Availability

Previous Applications

Historical Success

Company Preferences

Every factor should remain independently inspectable.

---

# AI Assistant

Purpose

Support users.

The assistant may answer

Scheme questions.

Application status.

Eligibility guidance.

Navigation help.

General FAQs.

The assistant must never

Approve applications.

Modify policy.

Generate official decisions.

Promise outcomes.

---

# Retrieval Augmented Generation

The assistant should answer using verified knowledge.

Knowledge sources

Government documentation.

PM Internship Scheme.

Company information.

Platform documentation.

Frequently asked questions.

Internal policy.

Hallucinations are unacceptable.

Unknown information should be acknowledged honestly.

---

# Learning System

ATLAS learns from outcomes.

Examples

Accepted offers.

Rejected offers.

Joined internships.

Dropouts.

Employer feedback.

Student feedback.

Learning improves ranking.

Never policy.

---

# Human Review

AI recommendations remain reviewable.

Government officers should be able to

Override.

Approve.

Reject.

Comment.

Escalate.

Manual actions become part of the audit trail.

---

# Confidence Scores

Every recommendation includes

Confidence.

Reasoning.

Supporting factors.

Missing information.

Confidence should never imply certainty.

---

# AI Safety

The AI System must

Avoid discrimination.

Avoid unsupported assumptions.

Avoid hallucination.

Avoid hidden reasoning.

Avoid bias amplification.

Protect user privacy.

Protect sensitive information.

---

# Privacy

AI systems should process only required information.

Personally identifiable information should remain protected.

Sensitive information should never appear in prompts unless required.

Logs should never expose confidential data.

---

# Observability

Monitor

Latency.

Failures.

Recommendation quality.

Feedback.

Acceptance rate.

Hallucination rate.

System health.

---

# Evaluation

The AI System should be evaluated continuously.

Metrics

Precision.

Recall.

Ranking quality.

Acceptance rate.

Joining rate.

User satisfaction.

Explanation usefulness.

Fairness score.

Latency.

---

# AI Engineering Rules

AI contributors must

Never bypass policy engines.

Never make eligibility decisions.

Never hardcode prompts.

Version prompts.

Version embeddings.

Version models.

Document every AI workflow.

Prefer deterministic logic whenever possible.

---

# Future Evolution

The AI architecture should support

Multi-model routing.

Agentic workflows.

Memory systems.

Personalization.

Government integrations.

Offline inference.

Federated learning.

Model upgrades.

Without redesigning the architecture.

---

# Anti-patterns

The following are prohibited.

LLMs deciding eligibility.

LLMs directly writing to the database.

AI bypassing policy.

Opaque recommendations.

Prompt-only business logic.

Hardcoded prompts.

Model-specific architecture.

Undocumented AI workflows.

Hidden reasoning.

---

# Quality Checklist

Before deploying AI features verify

☐ Policy engine executes first.

☐ AI ranking is explainable.

☐ Human override exists.

☐ Audit logs generated.

☐ Fairness evaluated.

☐ Privacy reviewed.

☐ Latency acceptable.

☐ Documentation updated.

☐ Evaluation metrics recorded.

---

# Final Principle

Artificial Intelligence should increase opportunity.

Never uncertainty.

The AI System exists to assist people,

not replace governance.

Trust is earned through transparency,

not intelligence.
# 00 — Vision

## Purpose

Build India’s most transparent, fair, explainable, and accessible internship allocation platform.

ATLAS is not an internship listing website. It is a national-scale decision-support system for the PM Internship Scheme: a platform that connects talent to opportunity through transparent, explainable, and equitable allocation.

## Why ATLAS exists

The current ecosystem primarily solves discovery: students search, students apply, and students wait. That model contributes to low conversion, poor matching, location mismatch, skill mismatch, role mismatch, high dropout, and low transparency.

ATLAS exists to solve allocation rather than recommendation.

## Principles

### Product philosophy

- Rules before AI.
- Policy before prediction.
- Trust before automation.
- Explainability before intelligence.
- Accessibility before aesthetics.
- People before technology.

### Design philosophy

Every screen must answer three questions immediately:

1. Where am I?
2. What can I do?
3. What should I do next?

Interfaces reduce uncertainty. Users must never feel lost.

### Engineering philosophy

- Simple systems scale.
- Readable code outlives clever code.
- Architecture is more important than implementation speed.
- Every module should be independently replaceable.
- Every service has a single responsibility.
- Every component solves one problem well.

### AI philosophy

Artificial intelligence assists decisions; it never replaces governance. The deterministic policy engine is always executed before AI ranking. Every AI-generated recommendation must be explainable, and every allocation must be auditable. See [05 AI System](05-AI-System.md).

### Accessibility philosophy

ATLAS is designed for every student: urban and rural users, high- and low-bandwidth connections, English and regional-language speakers, first-generation learners, and people with diverse access needs. Technology must reduce barriers, not create them. See [07 Accessibility](07-Accessibility.md).

## Rules

- Do not represent ATLAS as a recommendation marketplace.
- Do not ship policy, allocation, fairness, or AI scoring logic without an approved specification and review path.
- Preserve the separation among deterministic policy, AI ranking, fairness/explainability, and human review.
- Every material decision must be traceable to an actor, input, rule/model version, and review status; see [04 Backend](04-Backend.md).

## Standards

Success is measured by transparent, reviewable, and accessible workflows—not by opaque match-rate optimization alone. Product requirements must define actors, next actions, failure states, appeal or review paths, and measurable outcomes.

## Examples

Correct: “The application is awaiting reviewer assessment because the published policy check is incomplete.”

Incorrect: “ATLAS rejected you because the model ranked you low.”

## Best practices

Use plain language, visibly distinguish automated assistance from human decisions, and demonstrate only verified capabilities. Apply [01 Brand](01-Brand.md), [02 Design System](02-Design-System.md), and [12 Demo Strategy](12-Demo-Strategy.md) when turning this vision into product work.

## Success metrics

ATLAS succeeds when students find relevant opportunities faster, matching quality improves, acceptance and joining rates increase, transparency and trust improve, and manual workload decreases. Metrics must be defined with guardrails and audited before they drive product decisions.

## Future expansion notes

ATLAS should evolve into Digital Public Infrastructure capable of supporting multiple government employability initiatives while maintaining fairness, transparency, and public trust. Future revisions will define approved outcome metrics, regional policy variants, escalation SLAs, localization requirements, and a formal human-override governance process.

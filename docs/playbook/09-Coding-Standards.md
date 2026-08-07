# 09 — Coding Standards

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

The Coding Standards define how software is written, organized, reviewed, documented, and maintained throughout the ATLAS platform.

The objective is consistency.

Code should feel like it was written by one engineering team, regardless of whether it was authored by a human developer or an AI coding assistant.

Readable code is more valuable than clever code.

Maintainable code is more valuable than short code.

---

# Engineering Philosophy

Code exists for people.

Computers execute code.

Humans maintain code.

Always optimize for human understanding before machine convenience.

The best code is

- Simple
- Predictable
- Testable
- Documented
- Modular

Complexity should be hidden behind simple interfaces.

---

# Engineering Principles

Every engineer should follow these principles.

- Single Responsibility
- Separation of Concerns
- Composition over Inheritance
- Explicit over Implicit
- Readability over Cleverness
- Simplicity over Complexity
- Convention over Configuration

Every architectural decision should reduce long-term maintenance cost.

---

# Naming Conventions

Names should describe purpose.

Avoid abbreviations unless universally understood.

Good

StudentProfile

ApplicationStatus

AllocationEngine

InternshipRepository

Bad

Data

Helper

Manager

Temp

Util

NewFile

Thing

Variable names should communicate intent immediately.

---

# File Naming

React Components

PascalCase

StudentCard.tsx

CompanyDashboard.tsx

Hooks

camelCase

useAuth.ts

useStudentProfile.ts

Utilities

camelCase

formatDate.ts

calculateScore.ts

Folders

kebab-case

student-dashboard

company-profile

Never use spaces or inconsistent naming.

---

# Folder Organization

Group code by feature.

Avoid large generic folders.

Preferred

features/

student/

company/

admin/

allocation/

Avoid

components2/

misc/

helpers/

temp/

old/

---

# Function Design

Functions should perform one responsibility.

Preferred

calculateMatchScore()

generateRecommendation()

validateEligibility()

Avoid

processEverything()

Function names should describe behavior using verbs.

---

# Function Size

Functions should remain short and focused.

If a function becomes difficult to understand, extract smaller functions.

Avoid deeply nested logic.

Prefer early returns.

---

# Component Standards

React components should

Have one responsibility.

Receive explicit props.

Avoid unnecessary internal state.

Be accessible.

Be documented.

Large pages should compose smaller reusable components.

---

# State Management

Use

React State

for local component state.

Use

Zustand

for global UI state.

Use

TanStack Query

for server state.

Never duplicate the same state in multiple places.

---

# TypeScript Standards

Avoid using

any

Prefer

interfaces

types

generics

explicit typing

Every exported function should have explicit types.

---

# Python Standards

Follow

PEP8

Type hints are required.

Business logic should remain framework independent.

Avoid global mutable state.

Use dependency injection.

---

# Error Handling

Never silently ignore errors.

Every error should

Be logged.

Be understandable.

Provide recovery guidance.

Never expose sensitive implementation details.

---

# Comments

Code should explain itself.

Comments explain

Why

not

What.

Bad

// increment i

Good

// Retry allocation because the government policy allows one automatic retry before manual review.

Avoid redundant comments.

---

# Documentation

Public functions should include

Purpose

Parameters

Return values

Exceptions

Examples where appropriate.

Documentation is maintained alongside implementation.

---

# Logging

Logs should help diagnose problems.

Log

Authentication

Errors

Warnings

Allocation events

Policy decisions

Never log

Passwords

Tokens

Sensitive personal information

---

# Configuration

Never hardcode

Secrets

API Keys

URLs

Credentials

Environment-specific values

Use environment variables and configuration files.

---

# Dependency Management

Every dependency should justify its existence.

Before adding a package ask

Can existing libraries solve this?

Does this increase maintenance?

Is it actively maintained?

Avoid unnecessary dependencies.

---

# Git Standards

Commits should be

Small

Focused

Descriptive

Preferred

feat(auth): add OTP login

fix(student): resolve profile validation

docs(playbook): update backend architecture

Avoid

update

changes

fix

misc

---

# Pull Requests

Every pull request should include

Purpose

Summary

Screenshots (UI changes)

Testing performed

Documentation updates

Linked issue when applicable

---

# Testing Philosophy

Every feature should be testable.

Testing pyramid

Unit Tests

↓

Integration Tests

↓

End-to-End Tests

Critical business logic must always be covered.

---

# Refactoring

Refactoring improves structure.

It must never change business behavior.

Small continuous improvements are preferred over large rewrites.

---

# Security

Security is everyone's responsibility.

Validate inputs.

Escape outputs.

Use parameterized queries.

Apply least privilege.

Never trust client-side validation.

---

# Performance

Optimize after measuring.

Avoid premature optimization.

Prefer readable code over micro-optimizations unless performance requirements demand otherwise.

---

# Accessibility

Accessibility requirements apply to every contribution.

No feature is complete until accessibility requirements are satisfied.

---

# AI Collaboration

AI coding assistants should

Read the Playbook before implementation.

Reuse existing code.

Avoid duplicate abstractions.

Document assumptions.

Follow architectural boundaries.

Ask for clarification rather than inventing business rules.

AI should improve consistency, not introduce variation.

---

# Code Review Checklist

Before merging verify

☐ Naming follows standards.

☐ Architecture maintained.

☐ Documentation updated.

☐ Tests added.

☐ Accessibility preserved.

☐ Performance reviewed.

☐ No duplicate logic.

☐ No unnecessary dependencies.

☐ Security considered.

☐ Code remains understandable.

---

# Anti-patterns

The following are prohibited.

- God classes
- God components
- Utility dumping
- Circular dependencies
- Copy-paste programming
- Hardcoded values
- Deep nesting
- Duplicate business logic
- Dead code
- Unused dependencies
- Silent failures
- Over-engineering
- Premature optimization
- Hidden side effects

---

# Future Evolution

The Coding Standards should evolve alongside the platform.

Future additions may include

- Language-specific standards
- Microservice conventions
- AI-assisted code review
- Automated architecture validation
- Static analysis policies
- Secure coding guidelines
- Performance budgets per module

Standards should become stricter as the platform matures.

---

# Final Principle

Good code is invisible.

Users should never notice the implementation.

Engineers should immediately understand it.

Every contribution should leave the repository cleaner, more consistent, and easier to maintain than before.

ATLAS is built not only to work today, but to remain understandable years from now.
# 04 — Backend Architecture

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

The backend is responsible for enforcing business rules, protecting data integrity, orchestrating system workflows, and providing secure, scalable APIs to all client applications.

The backend is the source of truth for the ATLAS platform.

It owns business logic.

It does not own presentation.

The backend must remain deterministic, auditable, testable, and independent of frontend implementation.

---

# Backend Philosophy

The backend exists to answer one question:

"Given the current state of the system and the defined government policies, what is the correct action?"

Every decision should be

- Deterministic
- Explainable
- Auditable
- Secure
- Observable
- Maintainable

Business rules must never depend on UI behavior.

---

# Architectural Style

ATLAS follows Clean Architecture with Domain-Driven Design principles.

Layers

Presentation (FastAPI)

↓

Application

↓

Domain

↓

Infrastructure

Each layer has a single responsibility.

Dependencies always point inward.

Outer layers know about inner layers.

Inner layers never know about outer layers.

---

# Layer Responsibilities

## Presentation Layer

Responsible for

- HTTP Requests
- Authentication
- Validation
- Serialization
- Response Formatting

Never

- Execute business logic
- Query the database directly
- Make allocation decisions

---

## Application Layer

Responsible for

- Use Cases
- Service Orchestration
- Transactions
- Workflow Coordination

Examples

Student applies

↓

Validate request

↓

Call Policy Engine

↓

Call Allocation Service

↓

Persist

↓

Publish Events

---

## Domain Layer

The heart of ATLAS.

Contains

Entities

Value Objects

Business Rules

Policies

Domain Services

The Domain Layer must never import

FastAPI

SQLAlchemy

PostgreSQL

Redis

HTTP

External APIs

The Domain Layer should remain framework independent.

---

## Infrastructure Layer

Responsible for

Database

Repositories

ORM

Caching

File Storage

Authentication Providers

External APIs

Infrastructure implements interfaces defined by the Application layer.

Never the opposite.

---

# Core Principles

## Single Responsibility

Every class solves one problem.

Every module owns one capability.

---

## Dependency Inversion

Business logic never depends on frameworks.

Frameworks depend on business logic.

---

## Explicit Boundaries

Every module has clearly defined responsibilities.

Cross-module communication should occur through interfaces.

---

## Business First

Frameworks are replaceable.

Business logic is not.

---

# Folder Structure

app/

api/

application/

domain/

infrastructure/

core/

tests/

Each folder has a clearly defined responsibility.

Avoid dumping unrelated utilities into generic folders.

---

# API Layer

The API layer should remain thin.

Responsibilities

Authentication

Validation

Serialization

Status Codes

Documentation

Never

Business Logic

Database Queries

Complex Calculations

---

# Domain Layer

Contains

Student

Company

Internship

Application

Allocation

Notification

Audit

Complaint

Business rules belong here.

No framework dependencies allowed.

---

# Application Layer

Coordinates business workflows.

Examples

Create Student

Apply Internship

Generate Allocation

Submit Complaint

Approve Company

Each workflow should exist as an independent use case.

---

# Repository Pattern

Application Services communicate with repositories.

Repositories communicate with persistence.

Never bypass repositories.

---

# Dependency Injection

Use dependency injection for

Repositories

Configuration

Authentication

External services

Avoid global state.

Avoid singletons unless justified.

---

# Database Philosophy

PostgreSQL is the system of record.

The database enforces

Integrity

Relationships

Constraints

Indexes

The application enforces

Business rules

Validation

Policies

Never duplicate responsibilities.

---

# Transactions

Operations affecting multiple entities should execute inside transactions.

Either

Everything succeeds

or

Everything rolls back.

Never leave the system in an inconsistent state.

---

# Authentication

JWT based.

Role Based Access Control.

Support

Student

Company

Administrator

Policy Officer

Reviewer

Auditor

Authorization belongs in the backend.

Never trust frontend role checks.

---

# Validation

Validation occurs in three stages.

Input Validation

↓

Business Validation

↓

Persistence Validation

Each stage has a different responsibility.

---

# Error Handling

Errors should be

Consistent

Predictable

Meaningful

Secure

Never expose stack traces.

Never expose database internals.

Every error should contain

Code

Message

Context (when safe)

Recovery guidance

---

# Logging

Log

Authentication

Allocation

Errors

Warnings

Policy Decisions

Administrative Actions

Never log

Passwords

Secrets

Sensitive Personal Data

---

# Audit Trail

Every important action should produce an audit event.

Examples

Student Registered

Application Submitted

Allocation Generated

Manual Override

Complaint Created

Policy Updated

Audit logs are immutable.

---

# Security

Security is designed into the architecture.

Never added later.

Requirements

HTTPS

JWT

RBAC

Input Validation

Parameterized Queries

Rate Limiting

CORS

Secure Headers

Secrets Management

Principle of Least Privilege

---

# Performance

Prefer

Indexes

Pagination

Batch Operations

Async I/O

Connection Pooling

Caching

Avoid

N+1 Queries

Blocking Operations

Unbounded Queries

Duplicate Requests

---

# Caching

Cache only derived data.

Never cache authoritative business state without clear invalidation rules.

Examples

Search Results

Public Metadata

Reference Data

---

# Events

The backend should publish domain events.

Examples

StudentCreated

ApplicationSubmitted

AllocationCompleted

ComplaintResolved

Events should enable future scalability without tightly coupling services.

---

# Background Jobs

Long-running operations should execute asynchronously.

Examples

Email

Notifications

Document Processing

Report Generation

Embedding Generation

Never block API responses unnecessarily.

---

# AI Integration

AI is an assistant.

Not an authority.

AI services may

Rank

Explain

Summarize

Recommend

AI services may never

Override eligibility rules.

Bypass policy.

Modify authoritative data without validation.

Every AI output must remain explainable.

---

# Explainability

Every allocation decision should be traceable.

Store

Score

Reason

Factors

Policy Version

Timestamp

Users should understand why a recommendation exists.

---

# Testing

Every module should include

Unit Tests

Integration Tests

API Tests

Critical workflows require end-to-end testing.

---

# Documentation

Every endpoint documents

Purpose

Authentication

Inputs

Outputs

Errors

Permissions

Examples

Documentation is version controlled.

---

# AI Engineering Rules

AI coding assistants must

Never bypass Clean Architecture.

Never place business logic inside FastAPI routers.

Never access ORM models directly from API endpoints.

Never duplicate business rules.

Prefer extending existing services before introducing new abstractions.

When uncertain,

document assumptions rather than inventing policy.

---

# Anti-patterns

The following are prohibited.

Business logic inside routers.

Direct database access from controllers.

Circular dependencies.

Shared mutable global state.

Hardcoded configuration.

Business rules inside SQL queries.

Large God Services.

Utility classes containing unrelated logic.

Duplicate validation.

Hidden side effects.

---

# Quality Checklist

Before merging backend code verify

☐ Clean Architecture maintained

☐ Tests added

☐ Documentation updated

☐ Logging implemented

☐ Audit events generated

☐ Security reviewed

☐ Performance reviewed

☐ Business logic isolated

☐ No framework leakage into Domain layer

☐ AI output explainable

---

# Future Evolution

The backend architecture should support

Microservices

Event-driven architecture

Distributed workers

Vector search

Streaming APIs

Real-time notifications

Government integrations

Multiple schemes

without requiring architectural redesign.

---

# Final Principle

The backend is the guardian of truth.

Frameworks may evolve.

Infrastructure may change.

Databases may migrate.

The business rules of ATLAS remain consistent, explainable, auditable, and independent of technology.

Every backend decision should strengthen trust in the platform.
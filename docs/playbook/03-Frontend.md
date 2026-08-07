# 03 — Frontend Architecture

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

The Frontend Architecture defines how every screen, component, feature, and interaction should be structured inside the ATLAS web application.

The frontend must prioritize

- Maintainability
- Performance
- Accessibility
- Scalability
- Developer Experience
- AI Collaboration

Architecture exists to reduce complexity.

The goal is that any engineer or AI assistant can understand a feature within minutes.

---

# Frontend Philosophy

The frontend is responsible for

Presentation

Interaction

State Management

Accessibility

Performance

User Experience

The frontend is NOT responsible for

Business Logic

Policy Decisions

Database Access

Allocation Algorithms

Eligibility Rules

These belong to the backend.

---

# Architectural Principles

The frontend follows five principles.

## Single Responsibility

Each file solves one problem.

Each component has one purpose.

---

## Feature First

Organize by feature.

Never by file type.

Bad

components/

pages/

utils/

Good

features/

auth/

student/

dashboard/

internships/

---

## Reusable Before New

Search the Design System before creating new components.

Never duplicate UI.

---

## Composition Over Inheritance

Small reusable building blocks.

Large pages are compositions.

---

## Predictability

Folder structures remain consistent.

Naming remains consistent.

Routing remains consistent.

---

# Folder Structure

src/

app/

components/

features/

hooks/

lib/

services/

stores/

styles/

types/

utils/

assets/

---

## app/

Contains

Application bootstrap

Routing

Providers

Theme

Global layouts

---

## components/

Shared UI

Never business logic.

Examples

Button

Card

Dialog

Sidebar

Toast

---

## features/

Contains business-specific UI.

Each feature owns

components/

hooks/

pages/

api/

types/

utils/

Example

features/

student/

internships/

admin/

company/

---

## hooks/

Reusable hooks.

Never feature-specific.

---

## lib/

Libraries.

Axios

Utilities

Configuration

Clients

---

## services/

External integrations.

Authentication

Storage

API

Notifications

---

## stores/

Global state.

Keep minimal.

Prefer server state when possible.

---

## styles/

Global styles.

Theme.

Tokens.

Fonts.

---

## types/

Shared TypeScript types.

---

## utils/

Pure utility functions.

No side effects.

---

# State Management

Server State

TanStack Query

Client State

Zustand

Component State

React State

Never store server data inside Zustand.

---

# API Layer

All API communication occurs through

services/

Never directly inside components.

Components should never call Axios.

---

# Routing

React Router

Nested routes

Protected routes

Role-based layouts

Lazy loaded pages

---

# Authentication

JWT

Role Based

Protected Routes

Session Recovery

Automatic Token Refresh

---

# Component Guidelines

Every component should

Have one responsibility.

Support accessibility.

Support loading.

Support errors.

Support responsive layouts.

Support documentation.

---

# Naming

PascalCase

Components

camelCase

Functions

UPPER_CASE

Constants

kebab-case

Folders

---

# Error Boundaries

Critical sections should use React Error Boundaries.

Never allow one component failure to crash the application.

---

# Code Splitting

Lazy load

Pages

Charts

3D

Heavy dependencies

Never lazy load critical navigation.

---

# Performance

Memoize expensive calculations.

Virtualize large tables.

Avoid unnecessary re-renders.

Use suspense where appropriate.

---

# Accessibility

Keyboard support.

ARIA only when necessary.

Semantic HTML first.

Reduced motion support.

---

# Testing

Every reusable component

Unit tested.

Critical flows

Integration tested.

---

# Documentation

Every shared component documents

Purpose

Props

Accessibility

Examples

---

# AI Rules

AI contributors should

Read the Playbook.

Reuse existing components.

Never duplicate logic.

Never hardcode values.

Update documentation before introducing architectural changes.

---

# Final Principle

The frontend should feel invisible.

Users remember how easy the platform was to use,

not how the code was organized.
# 02 — Design System

> ATLAS Engineering Playbook
> Version 1.0
> Status: Living Standard

---

# Purpose

The Design System defines the visual, interaction, accessibility, and engineering language of ATLAS.

It is the foundation upon which every interface is built.

The Design System exists to guarantee that every screen, every interaction, every component, and every AI-generated implementation communicates the same values:

- Trust
- Fairness
- Clarity
- Accessibility
- Professionalism
- Consistency

The Design System is not a collection of UI components.

It is the product language.

Components are merely expressions of that language.

Whenever implementation conflicts with the Design System, the Design System takes precedence.

---

# Philosophy

ATLAS is not a startup dashboard.

ATLAS is not a portfolio website.

ATLAS is not a crypto platform.

ATLAS is not a gaming interface.

ATLAS is a Digital Public Infrastructure platform built for the Government of India.

Every design decision must strengthen public trust.

Premium experiences are achieved through clarity, not decoration.

Beautiful interfaces are the result of disciplined systems, not visual excess.

Users should never notice the design.

They should notice how easy the product is to use.

---

# Design Goals

Every interface should strive to achieve five objectives.

## 1. Reduce Cognitive Load

The interface should remove unnecessary thinking.

The user should always know

- Where they are.
- What they can do.
- What happens next.

---

## 2. Increase Trust

Trust is communicated through

- consistency
- transparency
- predictable behaviour
- readable typography
- meaningful feedback

Not through decoration.

---

## 3. Guide Decisions

The interface should gently guide users toward successful outcomes.

Never overwhelm users with equal-priority actions.

Every screen has one primary objective.

---

## 4. Respect Users

The product should never waste the user's time.

Loading experiences should reassure.

Forms should guide.

Errors should educate.

Navigation should remain predictable.

---

## 5. Scale Nationally

The Design System must support

- millions of users
- multiple government schemes
- multiple Indian languages
- accessibility requirements
- future products

without redesign.

---

# Design Decision Hierarchy

Whenever two design principles conflict, resolve the conflict using the following priority.

1. Accessibility

2. Clarity

3. Trust

4. Performance

5. Consistency

6. Aesthetics

Example

A beautiful animation that harms accessibility must be removed.

A compact layout that reduces readability must be expanded.

A creative interaction that confuses users must be redesigned.

Beauty never overrides usability.

---

# Product Experience Modes

ATLAS contains two completely different experiences.

Understanding this distinction is mandatory.

---

## Experience One

### Public Experience

Purpose

Introduce the platform.

Explain the mission.

Build trust.

Tell the story.

Generate confidence.

Characteristics

- cinematic
- premium
- scroll storytelling
- motion-rich
- emotionally engaging
- visually memorable

This experience exists only before authentication.

---

## Experience Two

### Operational Experience

Purpose

Help users complete work.

Characteristics

- calm
- minimal
- information first
- highly accessible
- predictable
- performance focused

Motion becomes subtle.

Whitespace increases.

Animations become supportive rather than expressive.

Dashboards should feel closer to

Linear

Notion

Stripe Dashboard

Google Cloud Console

than to a marketing website.

Landing pages sell the vision.

Dashboards deliver the vision.

Never mix these philosophies.

---

# Design Principles

## Clarity

Information is always easier to understand than to decorate.

Every screen answers

Where am I?

What can I do?

What should I do next?

---

## Consistency

Identical interactions should always produce identical outcomes.

Spacing

Typography

Colors

Icons

Motion

Navigation

must remain consistent across the product.

Consistency builds trust.

---

## Accessibility

Accessibility is a feature.

Not a future enhancement.

Every component must support

Keyboard navigation

Screen readers

Reduced motion

High contrast

Responsive layouts

44x44 minimum touch targets

Accessibility is mandatory.

---

## Performance

Performance is part of the design.

Interfaces should appear instantaneous.

Animations should never delay work.

Heavy assets should never block interaction.

The fastest interface is usually the most trusted.

---

## Scalability

Every component should solve one problem.

Every component should be reusable.

Every design decision should anticipate future expansion.

Avoid page-specific implementations whenever a reusable solution exists.

---

# Design Language

ATLAS combines inspiration from

Government Digital Services

Apple Human Interface Guidelines

Material Design 3

Stripe

Linear

IBM Carbon

Atlassian Design System

The result is a language that feels

professional

human

calm

modern

credible

never trendy.

---

# Visual Hierarchy

Visual hierarchy determines attention.

Hierarchy should be communicated using

Typography

Spacing

Contrast

Grouping

Motion

—not color alone.

Users should know where to look first within two seconds.

---

# Information Architecture Philosophy

Content is organised according to importance.

Primary

↓

Secondary

↓

Supporting

↓

Metadata

↓

Actions

Never reverse this order.

Actions should support information.

Information should not compete with actions.

---

# Layout Philosophy

Whitespace is not empty.

Whitespace communicates quality.

Use spacing before borders.

Use grouping before separators.

Large layouts should breathe.

Small layouts should remain uncluttered.

Users should never feel visually overwhelmed.

---

# Grid System

ATLAS follows an eight-point grid.

Spacing values should be

4

8

16

24

32

40

48

64

80

96

128

Avoid arbitrary spacing values.

Consistency creates rhythm.

Rhythm creates familiarity.

---

# Containers

Content should never stretch indefinitely.

Use maximum content widths.

Ultra-wide displays increase whitespace.

Not content width.

Readable line lengths are more valuable than filling every pixel.

---

# Border Radius

Small

8px

Medium

12px

Large

16px

Hero

24px

Never introduce arbitrary radius values.

Rounded corners communicate approachability.

Consistency communicates quality.

---

# Elevation

Elevation communicates hierarchy.

Not decoration.

Level 1

Cards

Level 2

Hover

Level 3

Dialogs

Level 4

Critical overlays

Avoid dramatic shadows.

Subtle elevation feels more premium.

---

# Color Philosophy

Color communicates meaning.

Never decoration.

Neutral colors dominate the interface.

Accent colors guide attention.

Success should always feel positive.

Danger should always feel unmistakable.

Information should always remain calm.

Never use color as the only communication channel.

Combine

Color

Icon

Text

Shape

for accessibility.

--
# Typography System

Typography is the primary communication tool of ATLAS.

Typography creates hierarchy.

Typography creates trust.

Typography reduces cognitive effort.

Color supports typography.

Typography never supports color.

---

## Font Family

ATLAS uses a single font family throughout the application.

Avoid mixing multiple font families.

Consistency improves readability and simplifies maintenance.

Typography should feel modern, neutral, and highly legible across desktop and mobile devices.

---

## Typography Hierarchy

Every screen follows the same hierarchy.

Display

Purpose

Landing Hero

Government Vision

Marketing Headlines

---

H1

Purpose

Page Title

---

H2

Purpose

Section Heading

---

H3

Purpose

Card Heading

Module Heading

---

H4

Purpose

Subsection Heading

---

Body Large

Purpose

Descriptions

Important content

---

Body

Purpose

General reading

Forms

Tables

Cards

---

Small

Purpose

Secondary Information

Supporting text

---

Caption

Purpose

Metadata

Timestamps

Status Information

Labels

---

Typography should never rely solely on font size.

Hierarchy is established through

Weight

Spacing

Grouping

Position

Contrast

---

# Semantic Color System

Colors describe meaning.

Never implementation.

Never reference colors directly.

Bad

Primary Blue

Green 500

Orange

Good

Primary

Surface

Success

Danger

Warning

Interactive

Muted

Accent

Border

Overlay

Surface Elevated

This enables theming without redesign.

---

## Primary

Represents

Authority

Navigation

Core Identity

Government Trust

---

## Secondary

Supports the primary hierarchy.

Never competes with primary actions.

---

## Surface

Primary page background.

Large content areas.

Cards.

Containers.

---

## Surface Elevated

Dialogs

Menus

Dropdowns

Floating panels

---

## Border

Separates related content.

Should never dominate the interface.

---

## Accent

Used sparingly.

Highlights

Progress

Current Step

Selected Items

---

## Success

Communicates

Verified

Eligible

Completed

Approved

Positive outcomes.

---

## Warning

Communicates

Attention required.

Incomplete information.

Potential issues.

---

## Danger

Communicates

Errors

Destructive actions

Critical warnings

---

## Info

Communicates

Helpful guidance

Neutral updates

Status information

---

# Component Philosophy

Every component should solve exactly one problem.

Never create "smart" components that manage multiple responsibilities.

Components should be

Composable

Reusable

Predictable

Accessible

Documented

Typed

Simple

The Design System owns reusable components.

Features compose them.

---

# Component Categories

## Foundations

Typography

Spacing

Colors

Icons

Tokens

Grid

Motion

---

## Inputs

Button

Input

Textarea

Checkbox

Radio

Switch

Slider

Date Picker

Autocomplete

Select

Search

OTP

Upload

---

## Navigation

Sidebar

Navbar

Tabs

Breadcrumbs

Pagination

Command Palette

Bottom Navigation

---

## Feedback

Toast

Alert

Banner

Dialog

Skeleton

Loading

Progress

Tooltip

Popover

---

## Data Display

Card

Table

List

Timeline

Badge

Avatar

Chip

Statistic

Chart

Accordion

Tree

---

## Layout

Container

Stack

Grid

Divider

Section

Page

Dashboard Layout

---

# Component Ownership

Shared reusable components belong in

components/ui

Feature-specific components belong inside

features/<feature>/components

Never duplicate shared components.

Improve the shared component instead.

---

# Navigation Philosophy

Navigation should never surprise users.

Navigation remains stable.

Users should always know

Where they are.

Where they came from.

Where they can go next.

---

Desktop

Persistent Sidebar

---

Tablet

Expanded Navigation

---

Mobile

Bottom Navigation

Compact Menus

---

Large workflows

Breadcrumbs

---

Search should always remain globally accessible.

---

# Forms

Forms should feel like conversations.

Not paperwork.

Reduce anxiety.

Reduce scrolling.

Reduce typing.

Reduce mistakes.

---

Forms should

Group related fields.

Explain requirements before submission.

Validate while typing.

Preserve entered data.

Recover gracefully.

Support keyboard navigation.

---

Never

Ask unnecessary information.

Reset completed forms.

Show every validation error simultaneously.

Require users to memorize instructions.

---

# Tables

Tables exist for efficiency.

Not decoration.

Tables should always support

Sorting

Searching

Pagination

Column visibility

Responsive presentation

Sticky headers where appropriate.

---

On mobile

Convert complex tables into

Cards

Expandable rows

or

Simplified layouts.

Never force horizontal scrolling for essential workflows.

---

# Empty States

Every empty state answers three questions.

Why is this empty?

What can I do next?

How do I continue?

An empty state should contain

Illustration (optional)

Clear explanation

Primary Action

Supporting guidance

---

# Loading States

Loading should reassure.

Never freeze the interface.

Use

Skeletons

Progress Bars

Status Messages

Incremental Loading

Prefer optimistic UI where appropriate.

---

# Error States

Error messages should explain

What happened

Why it happened (when safe)

How to recover

Never blame the user.

Avoid technical jargon.

Always provide a next step.

---

# Success States

Success should feel calm.

Professional.

Informative.

Avoid excessive celebration.

Government software should reinforce confidence.

Not entertainment.

---

# Dashboard Standards

Dashboards exist to complete work.

Every dashboard should prioritize

Speed

Readability

Information density

Consistency

Searchability

Common actions should require no more than three interactions.

Dashboards should remain visually calm regardless of the amount of data displayed.

---

# Landing Experience Standards

Landing pages have one objective.

Explain.

Inspire.

Build trust.

The landing experience may include

Scroll storytelling

Animated statistics

Interactive roadmap

Illustrations

One premium 3D hero

Subtle parallax

Motion should reinforce the narrative.

Never distract from it.

The landing page exists to communicate vision.

Not functionality.

---

# Data Visualization

Charts communicate insight.

Never decoration.

Choose charts intentionally.

Line

Trend

Bar

Comparison

Area

Growth

Pie

Composition

Heatmap

Distribution

Funnel

Conversion

Avoid decorative 3D charts.

Avoid unnecessary animation.

Charts should prioritize interpretation over aesthetics.

---
# Motion System

Motion exists to communicate.

Never to decorate.

Every animation must answer at least one of the following questions.

- What changed?
- Where did it come from?
- Where did it go?
- What should the user notice?
- What relationship exists between these two elements?

If an animation cannot answer one of these questions, it should not exist.

---

## Motion Principles

Motion should communicate

State

Hierarchy

Progress

Relationships

Navigation

Feedback

Never use motion simply because it looks impressive.

Good motion becomes invisible.

Bad motion becomes distracting.

---

## Motion Hierarchy

Level 1

Micro-interactions

Examples

Button hover

Card hover

Input focus

Tooltip

Duration

100–150ms

---

Level 2

Component Transitions

Examples

Accordion

Modal

Tabs

Drawer

Dropdown

Duration

180–280ms

---

Level 3

Page Transitions

Examples

Route changes

Dashboard navigation

Duration

300–400ms

---

Level 4

Storytelling Motion

Examples

Landing page

Roadmap

Hero section

Timeline

Horizontal storytelling

Duration

Variable

Only for public marketing pages.

Never inside operational dashboards.

---

## Motion Budget

Maximum motion per screen should remain low.

Operational interfaces should prioritize speed over expression.

Landing experiences may use richer motion when it supports storytelling.

---

# Responsive Strategy

Responsive design is not resizing.

Responsive design is rethinking.

Each breakpoint exists for a different purpose.

---

## Mobile

Primary objective

Task completion.

Rules

Single-column layouts.

Reduced navigation complexity.

Large touch targets.

Prioritize primary actions.

Avoid large data tables.

---

## Tablet

Primary objective

Balanced information density.

Rules

Two-column layouts where appropriate.

Expanded navigation.

Larger working area.

---

## Desktop

Primary objective

Efficiency.

Rules

Persistent sidebar.

Multi-column layouts.

Higher information density.

Keyboard-first workflows.

---

## Ultra-wide

Primary objective

Comfort.

Rules

Increase whitespace.

Never continuously increase content width.

Maintain readable line lengths.

---

# Accessibility Standards

Accessibility is mandatory.

Not optional.

Every reusable component must support

Keyboard navigation.

Visible focus.

Screen readers.

Reduced motion.

High contrast.

Accessible labels.

Semantic HTML.

Error identification.

Touch targets of at least 44×44 pixels.

---

## Reduced Motion

Users requesting reduced motion should receive

Reduced animations.

No parallax.

No autoplay motion.

Minimal transitions.

Functionality must remain identical.

---

## Keyboard Navigation

Every interactive element must be reachable.

Focus order must remain logical.

No keyboard traps.

Dialogs must restore focus when closed.

---

## Screen Reader Support

Interactive controls require accessible names.

Icons alone are insufficient.

Status changes should be announced when appropriate.

Decorative elements should remain hidden from assistive technologies.

---

# Performance Rules

Performance is a feature.

Every visual decision has a performance cost.

---

## Asset Strategy

Images

Lazy loaded.

Videos

Compressed.

3D assets

Deferred.

Fonts

Subsetted.

Icons

Tree shaken.

---

## Rendering

Avoid unnecessary re-renders.

Memoize expensive components where appropriate.

Virtualize large lists.

Use skeleton loading instead of layout shifts.

---

## JavaScript Budget

Every dependency should justify its existence.

Do not introduce libraries that solve problems already addressed by the existing stack.

---

# AI Implementation Rules

This repository is designed to be maintained by both humans and AI coding assistants.

AI contributors must follow the Design System before implementing features.

AI assistants must

Reuse existing components before creating new ones.

Never duplicate shared UI.

Never hardcode spacing.

Never hardcode colors.

Never hardcode typography.

Never bypass design tokens.

Prefer composition over duplication.

When uncertainty exists,

improve the Design System before introducing exceptions.

---

## AI Self Review

Before completing implementation every AI should verify

Does the component already exist?

Does this follow the Design System?

Does it use semantic tokens?

Is it accessible?

Is it responsive?

Is it documented?

Is motion necessary?

Would another engineer understand this implementation?

---

# Design Review Checklist

Every reusable component should satisfy the following checklist.

Accessibility

☐ Keyboard support

☐ Screen reader labels

☐ Focus indicators

☐ Reduced motion support

Visual

☐ Design tokens

☐ Typography hierarchy

☐ Consistent spacing

☐ Semantic colors

Engineering

☐ Reusable

☐ Typed

☐ Documented

☐ Tested

Performance

☐ Responsive

☐ No unnecessary rendering

☐ Lazy loading where applicable

User Experience

☐ Loading state

☐ Empty state

☐ Error state

☐ Success state

---

# Anti-patterns

The following patterns are prohibited.

Multiple competing primary buttons.

Animated backgrounds in dashboards.

Heavy glassmorphism.

Neon color palettes.

Unreadable tables.

Infinite nested dialogs.

Scroll-jacking in operational screens.

Icon-only navigation without labels.

Hidden primary actions.

Tiny touch targets.

Random spacing values.

Random border radius values.

Components with multiple unrelated responsibilities.

Hardcoded design values.

Duplicate reusable components.

Overly clever interactions that reduce usability.

---

# Governance

The Design System is governed by the Engineering Playbook.

Changes to reusable components require

Documentation updates.

Accessibility review.

Design review.

Engineering review.

Major changes should update the Design System before implementation.

Implementation must never become the source of truth.

Documentation remains the source of truth.

---

# Future Evolution

The Design System should evolve to support

Dark Theme.

High Contrast Theme.

Government White Label Deployments.

Additional Government Schemes.

Multiple Brand Variants.

Storybook Documentation.

Visual Regression Testing.

Component Analytics.

Internationalization.

Cross-platform Design Tokens.

The system should scale without redesign.

---

# Decision Log

Version 1.0

Initial Design System established.

Defined visual language.

Defined engineering rules.

Defined accessibility standards.

Defined responsive strategy.

Defined motion philosophy.

Defined governance model.

Future revisions should document

What changed.

Why it changed.

Alternatives considered.

Impact on existing components.

---

# Final Principle

The Design System is not a style guide.

It is not a UI kit.

It is not a component library.

The Design System is the contract between design, engineering, product, accessibility, and AI.

Every pixel should increase trust.

Every interaction should reduce effort.

Every component should be reusable.

Every decision should respect the user.

If a feature does not improve clarity, accessibility, trust, or usability, it should not become part of ATLAS.

The Design System is the foundation upon which every future experience is built.
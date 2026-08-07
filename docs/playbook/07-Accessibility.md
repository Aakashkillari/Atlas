# 07 — Accessibility

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

Accessibility ensures that every eligible citizen can use ATLAS regardless of physical ability, device capability, language, internet quality, or digital literacy.

Accessibility is not an enhancement.

Accessibility is a fundamental engineering requirement.

Every feature must be accessible before it is considered complete.

---

# Philosophy

ATLAS serves students across India.

Users may have

- Slow internet
- Older devices
- Limited digital literacy
- Visual impairments
- Hearing impairments
- Motor impairments
- Cognitive disabilities
- Multiple regional languages

The platform should adapt to users.

Users should never be forced to adapt to the platform.

---

# Accessibility Principles

Every interface should be

Understandable

Operable

Perceivable

Robust

Forgiving

Inclusive

Accessible experiences improve usability for everyone.

---

# Universal Design

Design should accommodate the widest possible audience without requiring separate experiences.

Avoid creating "special" interfaces.

Instead, build one inclusive interface.

---

# Keyboard Accessibility

Every workflow must be fully usable using only the keyboard.

Support

Tab

Shift + Tab

Enter

Escape

Arrow Keys

Space

Logical tab order is mandatory.

Keyboard focus should never become trapped.

Dialogs restore focus when closed.

---

# Focus Management

Every interactive element requires

Visible focus

Logical navigation

Consistent order

Focus indicators should never rely solely on color.

---

# Screen Reader Support

Use semantic HTML before ARIA.

Every interactive element requires

Accessible name

Accessible description where necessary

Proper labels

Meaningful headings

Decorative graphics should remain hidden from screen readers.

---

# Forms

Every field must contain

Visible Label

Helper Text

Validation Message

Error Description

Required fields should be identified programmatically.

Never rely on placeholders as labels.

---

# Error Identification

Errors should explain

What happened

Why

How to recover

Never use color alone.

Combine

Text

Icons

Color

Position

---

# Color Contrast

Text must maintain sufficient contrast against backgrounds.

Avoid light gray text on white surfaces.

Interactive elements should remain distinguishable under high-contrast settings.

---

# Color Independence

Never communicate meaning using only color.

Always combine

Icons

Text

Patterns

Labels

Examples

Success

✓ Approved

Green Badge

Text

Error

⚠ Action Required

Red Badge

Description

---

# Typography

Readable typography improves accessibility.

Use

Comfortable line height

Readable paragraph width

Consistent hierarchy

Avoid justified text.

Avoid extremely long lines.

---

# Motion Accessibility

Support

prefers-reduced-motion

Disable

Parallax

Scroll storytelling

Background movement

Camera animation

Reduce

Fade duration

Scale effects

Motion should never cause discomfort.

---

# Responsive Accessibility

Support

Mobile

Tablet

Desktop

Ultra-wide

Touch targets

Minimum

44×44px

Spacing between controls should prevent accidental taps.

---

# Low Bandwidth Mode

ATLAS should support users with poor connectivity.

Reduce

Images

Videos

Animations

Large assets

Prefer

Text

SVG

Optimized graphics

The system should remain usable on slow networks.

---

# Offline Resilience

Where appropriate

Persist user input locally.

Retry failed requests.

Recover interrupted workflows.

Avoid unnecessary data loss.

---

# Multilingual Accessibility

Support

English

Hindi

Regional Languages

Text expansion should not break layouts.

UI should support longer translated strings.

Icons should not replace readable labels.

---

# Plain Language

Government terminology should be understandable.

Avoid unnecessary technical language.

Prefer

"Application Submitted"

instead of

"Transaction Completed Successfully"

---

# Voice Guidance

Future versions may support

Voice navigation

Text-to-speech

Speech assistance

without changing application architecture.

---

# Images

Every informative image requires

Alternative text.

Decorative images should use empty alt attributes.

---

# Icons

Icons assist recognition.

Icons never replace labels.

Every icon-only action requires an accessible label.

---

# Tables

Support

Keyboard navigation

Screen readers

Responsive transformation

Sticky headers where appropriate

Large tables should remain searchable.

---

# Charts

Every chart requires

Title

Legend

Summary

Accessible data representation

Color-independent differentiation

Never rely solely on color.

---

# Media

Videos should support

Captions

Transcripts

Pause controls

Avoid autoplay where unnecessary.

---

# Notifications

Status updates should be announced to assistive technologies when appropriate.

Avoid excessive interruptions.

---

# Authentication

Accessible authentication should support

Keyboard

Screen readers

Clear validation

Error recovery

OTP workflows should remain accessible.

---

# Performance

Accessibility should not reduce performance.

Accessibility and performance complement one another.

---

# AI Rules

AI contributors must

Use semantic HTML first.

Never remove labels.

Never remove focus indicators.

Support reduced motion.

Support screen readers.

Support keyboard navigation.

Never introduce inaccessible custom controls without necessity.

---

# Testing

Accessibility testing includes

Keyboard-only testing

Screen reader testing

High-contrast mode

Reduced motion

Responsive layouts

Touch devices

Low-bandwidth simulation

---

# Anti-patterns

Prohibited

Color-only communication

Hidden focus indicators

Placeholder-only labels

Hover-only interactions

Tiny touch targets

Auto-playing media

Keyboard traps

Unlabelled controls

Poor contrast

Motion without reduced-motion support

---

# Quality Checklist

Before release verify

☐ Keyboard accessible

☐ Screen reader compatible

☐ Reduced motion supported

☐ Color contrast acceptable

☐ Semantic HTML used

☐ Labels present

☐ Errors understandable

☐ Responsive

☐ Touch friendly

☐ Multilingual ready

☐ Low bandwidth supported

---

# Future Evolution

Accessibility should expand to support

Voice interfaces

Regional accessibility standards

Offline-first workflows

Government accessibility compliance

AI-assisted accessibility validation

without redesigning the platform.

---

# Final Principle

Accessibility is not about supporting a minority.

Accessibility is about respecting every citizen.

A platform that cannot be used by everyone cannot become national infrastructure.

Every accessibility improvement strengthens trust in ATLAS.
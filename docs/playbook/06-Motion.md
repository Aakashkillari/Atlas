# 06 — Motion System

> ATLAS Engineering Playbook · Version 1.0

---

# Purpose

Motion is a communication tool.

Its responsibility is to explain change, reinforce hierarchy, guide attention, and improve user understanding.

Motion should never exist for decoration.

If an animation does not improve comprehension, accessibility, or user confidence, it should not exist.

---

# Motion Philosophy

Motion should feel

- Calm
- Intentional
- Lightweight
- Predictable
- Professional

ATLAS is a government-grade platform.

Motion should inspire trust rather than excitement.

Animations should disappear into the experience rather than becoming the experience.

---

# Motion Principles

Every animation should satisfy at least one purpose.

✓ Explain change

✓ Guide attention

✓ Reinforce hierarchy

✓ Provide feedback

✓ Communicate relationships

✓ Maintain orientation

Never animate purely for visual appeal.

---

# Product Motion Modes

ATLAS has two motion systems.

---

## Landing Experience

Purpose

Communicate vision.

Inspire trust.

Tell a story.

Motion Allowed

- Hero animations
- Scroll storytelling
- Horizontal sections
- Parallax
- Timeline animations
- Number counters
- SVG path drawing
- Lottie animations
- 3D object movement
- Camera transitions

Landing pages may use expressive motion.

---

## Operational Experience

Purpose

Help users complete work.

Motion Allowed

- Hover feedback
- Page transitions
- Dialog transitions
- Dropdown animation
- Toast notifications
- Expand / Collapse
- Loading skeletons

Operational dashboards must remain calm.

Never use cinematic animations inside authenticated workflows.

---

# Motion Hierarchy

Level 1

Micro Interactions

Examples

Button hover

Checkbox

Switch

Tooltip

Duration

100–150ms

---

Level 2

Component Motion

Examples

Cards

Dialogs

Drawers

Dropdowns

Tabs

Duration

180–250ms

---

Level 3

Navigation Motion

Examples

Page transitions

Sidebar collapse

Layout changes

Duration

250–350ms

---

Level 4

Storytelling Motion

Landing page only.

Examples

ScrollTrigger

Timeline

Roadmap

Hero

3D camera movement

Interactive storytelling

Duration

Variable

---

# Timing Tokens

Instant

0ms

Fast

120ms

Normal

220ms

Slow

320ms

Page

400ms

Never exceed

500ms

unless storytelling requires it.

---

# Easing

Standard

ease-out

Entrance

ease-out

Exit

ease-in

Emphasis

ease-in-out

Avoid bounce animations inside dashboards.

---

# Motion by Component

## Buttons

Hover

Slight elevation.

Small shadow increase.

Background transition.

No scaling beyond 1.02.

---

## Cards

Hover

Elevation increase.

Border emphasis.

Optional subtle lift.

Never dramatic movement.

---

## Inputs

Focus

Border transition.

Focus ring.

Background adjustment.

---

## Dialogs

Fade

+

Scale

Small upward movement.

No bounce.

---

## Drawers

Slide

+

Fade

Respect screen direction.

---

## Toasts

Slide

+

Fade

Auto dismiss.

Do not interrupt workflows.

---

## Navigation

Sidebar

Smooth width transition.

Maintain icon alignment.

Avoid layout jumping.

---

# Loading Motion

Preferred

Skeletons

Shimmer

Progress

Avoid

Infinite spinners.

Blocking screens.

Fake loading.

Loading motion should reassure users.

---

# Scroll Behaviour

Landing

Scroll storytelling permitted.

Operational

Native scrolling only.

Never hijack browser scrolling inside dashboards.

---

# Parallax

Allowed only

Landing page.

Hero.

Roadmap.

Vision sections.

Avoid excessive depth.

Motion should remain subtle.

---

# 3D Motion

3D exists to communicate.

Not impress.

Approved

Hero Globe

ATLAS Statue

Roadmap

Data Visualization

Never place 3D scenes inside operational dashboards.

---

# Chart Animation

Charts may animate

On first appearance.

Never on every interaction.

Animations should help users understand data changes.

---

# Motion Budget

Every screen has a motion budget.

Operational pages

Minimal.

Landing pages

Moderate.

Never animate everything simultaneously.

Motion should direct attention.

Not compete for it.

---

# Reduced Motion

Users requesting reduced motion receive

No parallax.

No camera movement.

No scroll storytelling.

Minimal transitions.

Core functionality remains identical.

---

# Performance

Motion should maintain

60 FPS

GPU accelerated transforms

Avoid

Animating width

Animating height

Animating box-shadow excessively

Animating layout

Prefer

Opacity

Transform

Scale

Translate

---

# Accessibility

Motion should never

Trigger discomfort.

Reduce readability.

Delay interaction.

All non-essential motion must respect prefers-reduced-motion.

---

# Libraries

Preferred

Framer Motion

GSAP

React Three Fiber

Motion One

Lottie

Lenis

Avoid introducing multiple libraries solving the same problem.

---

# AI Rules

AI contributors must

Use existing animation utilities.

Reuse timing tokens.

Reuse easing tokens.

Never invent animation durations.

Never animate without purpose.

Always support reduced motion.

---

# Anti-patterns

Prohibited

Heavy glassmorphism.

Continuous floating elements.

Infinite looping animations.

Auto-playing videos inside dashboards.

Scroll hijacking.

Large bounce animations.

Flashy transitions.

Confetti.

Neon glow effects.

Cyberpunk aesthetics.

Animation for decoration.

---

# Quality Checklist

Before merging

☐ Motion communicates purpose.

☐ Reduced motion supported.

☐ 60 FPS maintained.

☐ GPU accelerated.

☐ Timing tokens respected.

☐ Accessibility reviewed.

☐ Landing and Dashboard motion separated.

☐ No prohibited patterns used.

---

# Future Evolution

Future versions may support

Adaptive Motion

AI-generated transitions

Personalized animation intensity

Cross-platform motion tokens

Native mobile motion systems

without redesigning the motion language.

---

# Final Principle

Motion should explain.

Not entertain.

The best animation is the one users understand instantly and barely notice.

ATLAS uses motion to increase trust, clarity, and confidence—not to distract from the work.
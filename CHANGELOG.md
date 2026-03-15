## 1.9.1 (2026-03-15)

### Fix

- **a11y**: remove target size overrides from inline legal link

## 1.9.0 (2026-03-15)

### Feat

- **footer**: add editable footer with manager UI

### Fix

- **a11y**: correct logo alt text and remove duplicates
- **a11y**: increase disabled link contrast to meet WCAG AAA
- **a11y**: WCAG 2.5.5 AAA target size for footer elements
- **a11y**: WCAG remediation for footer and manager form

## 1.8.0 (2026-03-14)

### Feat

- **dev**: add django-debug-toolbar for local development

## 1.7.0 (2026-03-14)

### Feat

- Adds the tinyMCE rich text editor for posts, pages and snippets

### Fix

- fix tests and bump django version

## 1.6.0 (2026-03-14)

### Feat

- **cms**: add CMS management for landing page content

## 1.5.0 (2026-03-14)

### Feat

- **header**: show GET INVOLVED button next to hamburger on mobile
- **landing**: add About OJC dropdown menu and nav hover inversion
- **landing**: restyle footer with grid layout, bigger logo, and compact menus
- **landing**: add scroll-triggered count-up animation for stats section
- **landing**: move buttons inside feature cards with rounded corners
- **landing**: add landing page with hero, features, and stats sections

### Fix

- **a11y**: WCAG 2.1 AA remediation for landmarks, focus, motion and semantics
- **a11y**: add arrow key navigation and auto-focus to mobile menu
- **a11y**: increase header logo text to WCAG-compliant minimum font size
- **a11y**: WCAG 2.1 AA accessibility remediation for landing page
- **landing**: show stats section circles on mobile, overlapping from top-right
- **footer**: reorder layout for mobile and add border to Contact us column
- **footer**: remove fixed container height causing white overflow on mobile
- **landing**: push hero circles right on mobile/tablet to reduce text overlap
- **landing**: clip hero circles on right and position to overlap header text
- **landing**: make nav hover fill full header height
- **landing**: clip stats circles at container left edge, allow vertical overflow
- **landing**: restyle stats section circles with bright white strokes and proper positioning
- **landing**: expand SVG viewBox to prevent circle stroke clipping

### Refactor

- **css**: move header/nav selectors from app.css to header.css
- **css**: split header and footer styles into separate CSS files

## 1.4.0 (2026-03-13)

### Feat

- **logging**: add structlog with rich for structured logging

## 1.3.1 (2026-03-13)

### Fix

- **docker**: run as non-root user and fix .venv permissions

## 1.3.0 (2026-03-13)

### Feat

- **merge**: merge from main

### Fix

- removes migration that was not needed on this branch. Ruff formatting.

## 1.2.0 (2026-03-13)

### Feat

- **docker**: add Docker Compose development environment
- **cms**: add CMS views and routes for index and board pages

## 1.1.1 (2026-03-13)

### Fix

- **static**: add static publisher images for carousel, including blank placeholder

## 1.1.0 (2026-03-12)

### Feat

- **cms**: add translatable rich-text CMS app with Page, Post, and Snippet models

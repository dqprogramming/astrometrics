## 1.22.1 (2026-03-22)

### Fix

- **cms**: make header logo and text link to homepage

## 1.22.0 (2026-03-22)

### Feat

- **cms**: add rich text editing for About Us stat text fields
- **cms**: add rich text editing for About Us quote text
- **cms**: add drag-and-drop quote management for About Us page
- **cms**: add About Us page with CMS management

### Fix

- **cms**: make TinyMCE underline use <u> tag instead of inline styles
- **cms**: reinitialize TinyMCE editors after drag-and-drop reorder
- **cms**: render quote text as safe HTML and fix p-tag nesting
- **cms**: render DELETE checkbox for About Us quote formset deletion
- **cms**: fix drag-and-drop sort order not persisting for About Us quotes

## 1.21.0 (2026-03-22)

### Feat

- **cms**: add ManifestoPageSettings singleton with CMS management
- **cms**: ensure text renders above arrows in blue section
- **cms**: style Speak To Us button as black with white text
- **cms**: move arrows leftward next to text block
- **cms**: align achievable text with speech bubble and darken CTA button
- **cms**: thicken speech bubble strokes and add speech lines
- **cms**: refine speech bubbles and blue section layout
- **cms**: hide manifesto arrows on mobile viewports
- **cms**: tighten arrow spacing and square off middle arrow prongs
- **cms**: refine manifesto blue section arrows and layout
- **cms**: style manifesto text section with bolder centered text
- **cms**: add Our Manifesto page
- **cms**: add setup_menu_defaults management command

## 1.20.0 (2026-03-20)

### Feat

- **cms**: add sort-by-surname button and unsaved changes warning
- **cms**: migrate OJC Boards page to database-backed CMS

## 1.19.0 (2026-03-20)

### Feat

- **cms**: migrate Our Team page to database-backed CMS with contact form
- **cms**: add Our Team page with team sections and contact form

## 1.18.0 (2026-03-20)

### Feat

- **cms**: add CMS-driven Our Model singleton page with dynamic revenue tables
- **cms**: redesign CTA section with journal covers image and update styling
- **cms**: redesign revenue distribution section with colour-coded package tables
- **cms**: redesign OJC Model and Journal Funding sections
- **cms**: add Our Model page with hero, collections, funding, and revenue sections

### Fix

- **cms**: add merge migration and format imports
- **a11y**: remediate WCAG AAA issues on Our Model page
- **cms**: align revenue section layout using CSS grid

## 1.17.0 (2026-03-15)

### Feat

- **cms**: add page hero customisation and preview improvements

## 1.16.0 (2026-03-15)

### Feat

- use switches over checkboxes

## 1.15.0 (2026-03-15)

### Feat

- **cms**: add secret preview URLs for unpublished pages and posts

## 1.14.0 (2026-03-15)

### Feat

- **header**: configurable mobile sub-items, scrollable mobile nav, remove accordion toggles
- **header**: add configurable header, nav menus, and per-item call-to-action

### Fix

- **manager**: reorder nav to Header, Footer, Landing Page
- **a11y**: WCAG AAA target size for dropdown items and header CTA button
- **a11y**: apply keyboard navigation to all dropdown menus

## 1.13.0 (2026-03-15)

### Feat

- **portal**: flag audit log entries created by a reversion

## 1.12.1 (2026-03-15)

### Fix

- **manager**: use valid bootstrap icon for footer dashboard card

## 1.12.0 (2026-03-15)

### Feat

- **manager**: add landing page and footer to dashboard, reorder sidebar

### Fix

- **config**: load .env file via python-dotenv at settings startup

## 1.11.0 (2026-03-15)

### Feat

- **config**: move settings to environment variables
- adds publisher portal

### Fix

- repair broken uv.lock from line-wrapped paste

## 1.10.0 (2026-03-15)

### Feat

- **cms**: add news index and detail pages

### Fix

- **cms**: resolve conflicting migration and guard debug toolbar hostname lookup

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

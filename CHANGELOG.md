## 1.24.0 (2026-03-27)

### Feat

- **cms**: totally dynamic block-based CMS
- **cms**: totally dynamic block-based CMS
- **cms**: replace FeatureCardBlock with grouped FeatureCardsBlock
- **cms**: add landing page template seed and manager view updates
- **cms**: add landing page block types with is_landing_page routing
- **cms**: add contact form block to Our Team page template data migration
- **cms**: add recipient JS handlers to block page manager
- **cms**: add ContactFormBlock with email sending and public form
- **cms**: add About Us block page template data migration
- **cms**: add manager and public templates for About Us blocks
- **cms**: add 4 About Us block types with models, forms, and tests
- **cms**: add Our Team block page template
- **cms**: add Sort by Surname button to People List block
- **cms**: seed board member images in OJC Boards block page template
- **cms**: add OJC Boards block page template data migration
- **cms**: add person list JS handlers to block page manager
- **cms**: add manager and public templates for People List block
- **cms**: add PeopleListBlock and PeopleListPerson models with forms
- **cms**: show data grid immediately when adding new table
- **cms**: replace delete checkboxes with instant-action buttons
- **cms**: port full table editing UI to Revenue Distribution block
- **cms**: add 5 Our Model block types with models, forms, templates and tests
- **cms**: add uploadable hero image to Quarter Circle hero block
- **cms**: add CTA button colour pickers to manifesto blocks
- **cms**: add manifesto block types with models, forms, templates, and tests
- **cms**: implement dynamic block pages with CRUD
- **cms**: add block registry module
- **cms**: add configurable carousel navigation dot colours
- **cms**: sort Add Block dropdown alphabetically
- **cms**: remove legacy Our Members fields and models
- **cms**: update public Our Members page for block system
- **cms**: rewrite manager JS for dynamic block system
- **cms**: add block-based manager template and partials
- **cms**: rewrite Our Members manager for block system
- **cms**: add block forms and formsets
- **cms**: migrate existing Our Members data to block system
- **cms**: add block system models for Our Members page
- **cms**: add per-section reset colours to default button
- **cms**: add configurable background and text colours per section
- **cms**: split CTA into independent Who We Are and Members Grid CTAs
- **cms**: add drag-and-drop section reordering for Our Members page
- **cms**: add show/hide toggles for all Our Members page sections
- **cms**: integrate Our Members page with CMS backend
- **cms**: add Our Members models, forms, and data migration
- **cms**: add static Our Members page with layout and styling

### Fix

- **cms**: remove broken merge migration referencing nonexistent parent
- **cms**: fix spacing between content/stats and org carousel dots
- **cms**: restore static_image refs in Our Team template data
- **cms**: replace team placeholder images with real photos
- **cms**: remove placeholder image refs from Our Team template
- **cms**: fix OJC Boards template crash and people list rendering
- **cms**: remove Our Model dashboard card referencing deleted URL
- **cms**: mark revenue callout as safe to prevent escaped HTML
- **cms**: initialize TinyMCE editors on first page load
- **cms**: reinitialize TinyMCE for all block types after drag and drop
- **cms**: prevent double-creation of revenue distribution defaults
- **cms**: add missing space in Revenue Distribution heading default
- **cms**: preserve row data when adding rows to new tables on first save
- **cms**: fix delete buttons not submitting form in revenue editor
- **cms**: preserve cell data for newly added columns on first save
- **cms**: fix revenue distribution tables not rendering on front end
- **cms**: fix revenue distribution rendering and defaults
- **cms**: make block deletion immediate via server-side POST
- **cms**: add default lorem ipsum body text to Who We Are circle fields
- **cms**: align Thin Band hero default bg colour with Quarter Circle hero
- **cms**: add default body text and CSS loading to manifesto blocks
- **cms**: fix nested form breaking save buttons on block page editor
- **cms**: make PageBlock.content_type non-nullable and fix LOREM_BODY scope
- **cms**: fix carousel navigation dots positioning with dynamic block IDs
- **cms**: fix save button and make block delete client-side
- **cms**: make colour pickers display visible colour swatch
- **cms**: fix institution delete not hiding row visually
- **cms**: use Python csv module for CSV import parsing
- **cms**: fix bottom carousel text color and add member placeholder

### Refactor

- **cms**: remove old Landing Page singleton system
- **cms**: use dynamic block icons in block page manager
- **cms**: remove old Contact Us Form singleton system
- **cms**: remove old About Us singleton system
- **cms**: remove old Our Team singleton system
- **cms**: remove old OJC Boards singleton system
- **cms**: remove old Our Model singleton system
- **cms**: remove ManifestoPageSettings model and related code
- **cms**: remove manifesto manager URL
- **cms**: remove manifesto frontend route and view
- **cms**: remove Our Manifesto from Content nav
- **cms**: rename blocks to descriptive, reusable names
- **cms**: move Our Members to new Block Pages nav section
- **cms**: centralise block metadata into registry

## 1.23.0 (2026-03-27)

### Feat

- **journals**: redesign public catalogue pages

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

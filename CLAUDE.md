# CLAUDE.md — AI Assistant Guide for kimujinyogi.github.io

## Project Overview

This is a **Hugo static site** — a personal Japanese blog titled "じにょぎの日常" (Jinyogi's Daily Life).
Topics covered: camping car travel, programming, and family life.

- **Site URL**: https://kimujinyogi.github.io/
- **Hugo theme**: ZZO (git submodule at `campcar/themes/zzo/`)
- **Language**: Japanese only (`ja`)
- **Author**: じにょぎ (jinyogi), based in Saitama, Japan

**All Hugo commands must be run from inside the `campcar/` subdirectory**, not the repo root.

---

## Branch & Deployment Workflow

| Branch | Purpose |
|--------|---------|
| `campcar` | **Source branch** — all content development happens here |
| `master` | **Built output** — generated HTML; auto-managed by CircleCI, never edit directly |

**Workflow:**
1. Make changes on the `campcar` branch
2. Push to `campcar`
3. CircleCI automatically builds with `hugo` and force-pushes generated HTML to `master`
4. GitHub Pages serves the `master` branch

The deploy script is at `.circleci/deploy.sh`. CircleCI config is at `.circleci/config.yml`.

**When working on AI-assisted tasks**, develop on feature branches branching off `campcar`, then merge to `campcar`.

---

## Directory Structure

```
kimujinyogi.github.io/          ← repo root
├── .circleci/                  ← CircleCI CI/CD config and deploy script
├── .gitmodules                 ← ZZO theme submodule reference
├── CLAUDE.md                   ← this file
├── README.md                   ← brief project notes (Japanese)
└── campcar/                    ← Hugo project root (run all hugo commands here)
    ├── config/
    │   └── _default/
    │       ├── config.toml     ← primary Hugo config (baseURL, markup, taxonomies)
    │       ├── params.toml     ← ZZO theme parameters (colors, features, bio)
    │       ├── languages.toml  ← language settings
    │       ├── menus.toml      ← base navigation menus
    │       └── menus.ja.toml   ← Japanese navigation menus (active)
    ├── content/
    │   ├── posts/              ← all blog posts (Markdown)
    │   ├── archive/            ← archive listing page
    │   └── gallery/
    │       ├── trip/           ← travel photo galleries
    │       └── others/         ← other photo galleries
    ├── archetypes/
    │   └── default.md          ← frontmatter template for new posts
    ├── assets/
    │   └── css/
    │       └── custom.css      ← custom CSS overrides (e.g. .imagecenter)
    ├── layouts/                ← custom layout overrides (takes priority over theme)
    ├── static/                 ← static assets (images, favicon, PWA manifest)
    │   ├── favicon.ico
    │   ├── favicon.png
    │   ├── logo-512.png
    │   ├── manifest.json       ← PWA manifest
    │   └── <topic>/            ← images organized by post/topic name
    ├── resources/              ← Hugo cache (auto-generated, do not commit manually)
    └── themes/
        └── zzo/                ← ZZO theme (git submodule — do not modify)
```

---

## Common Commands

```bash
# All commands run from campcar/ directory
cd campcar

# Local development server (with live reload)
hugo server

# Build site to public/
hugo

# Create a new post from archetype
hugo new posts/<filename>.md
```

---

## Creating Blog Posts

### File Naming Convention
Posts live in `campcar/content/posts/`. Naming uses a short prefix + date or description:

- `z20260129.md` — general posts (z prefix = じにょぎ)
- `campcar_YYYYMMDD.md` — camping car content
- `program_YYYYMMDD.md` — programming content
- `mc<description>.md` — Minecraft-related content
- `st<description>.md` — other themed content

### Frontmatter Template

Every post should use this frontmatter (matches `campcar/archetypes/default.md`):

```yaml
---
title: "Post Title Here"
date: 2026-01-20T22:00:00+09:00
description: "Brief description of the post"
draft: false
hideToc: false
enableToc: true
enableTocContent: false
tocPosition: inner
tocLevels: ["h2", "h3", "h4"]
tags:
- tag-name
series:
- series-name
categories:
- category-name
image:
---
```

- Use JST timezone offset `+09:00` for all dates
- Set `draft: true` to hide a post from the public site
- `buildFuture = true` is set, so future-dated posts will be built

### Taxonomy System
Three taxonomies are active: `tags`, `categories`, `series`. Use all three where appropriate.

### Embedding Images

Images are stored in `campcar/static/<topic>/`. Reference them in posts like:

```markdown
![alt text](/topic/image.jpg)
```

For centered images, use the custom CSS class:

```html
<img src="/topic/image.jpg" class="imagecenter" alt="description">
```

The `.imagecenter` class sets width to 70% and centers the image (defined in `campcar/assets/css/custom.css`).

---

## Hugo Configuration Highlights

From `campcar/config/_default/config.toml`:

- **Markup**: Goldmark renderer with `unsafe = true` (allows raw HTML in Markdown), hard wraps enabled
- **Syntax highlighting**: Code fences with line numbers, no inline classes
- **ToC**: Levels h2–h4, unordered
- **Outputs**: HTML + RSS + JSON search index for home, section, taxonomy pages
- **Taxonomies**: `categories`, `tags`, `series`
- **Emoji**: Enabled
- **Pagination**: 13 items per page

---

## Theme: ZZO

The ZZO theme submodule is at `campcar/themes/zzo/`. **Never modify files inside `themes/zzo/`.**

To override theme templates, copy the file to the corresponding path under `campcar/layouts/` and edit there.

Key theme features enabled (configured in `campcar/config/_default/params.toml`):
- Dark/light theme switcher
- Breadcrumb navigation
- Disqus comments (shortname: `kimujinyogi-github-io-1`)
- Full-text search with highlighting
- Table of contents with folding
- Sidebar: bio/whoami, tags, series, categories
- Photo gallery with PhotoSwipe
- PWA support

---

## Navigation Menus

Defined in `campcar/config/_default/menus.ja.toml`:

| Name | URL |
|------|-----|
| じにょぎについて (About) | `/about` |
| 記事 (Posts) | `/posts` |
| 一覧 (Archive) | `/archive` |
| 写真 (Gallery) | — (parent) |
| 旅の写真 (Trip Photos) | `/gallery/trip` |
| その他 (Others) | `/gallery/others` |
| プライバシーポリシー (Privacy) | `/privacy` |

---

## Key Conventions

1. **Language**: All content is in Japanese. Keep titles, descriptions, and tags in Japanese where appropriate.
2. **Branch discipline**: Never commit built output to the `campcar` source branch. Never manually edit `master`.
3. **Theme submodule**: Do not edit `campcar/themes/zzo/`. Override via `campcar/layouts/`.
4. **Static assets**: Store post-related images under `campcar/static/<topic-name>/`.
5. **Timestamps**: Always use JST (`+09:00`) for post dates.
6. **Drafts**: Use `draft: true` while writing; set to `false` when ready to publish.
7. **CJK support**: `hasCJKLanguage = true` is set — Hugo correctly counts Japanese characters for summaries.

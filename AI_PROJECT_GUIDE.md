# ContentHub – Project Guide

## Environment Context
- All development happens in the local environment contained in this repository  
- Do not attempt to diagnose or change production systems directly from this workspace  
- Avoid `sudo` and global package installs; rely on project tooling instead  
- Use the git-style `./ch` wrapper (backed by `tools/dev.py`) to run local workflows (server, database init, admin creation)  

---

## Project Overview
**ContentHub** is a modular **AI-powered content ideation and management platform** built with **FastAPI** and **SQLModel**.  
The initial milestone focuses on a **content idea generator and idea repository** where users can brainstorm, categorize, and evolve ideas for writing, media, or campaigns.  

Over time, ContentHub will expand into a full creative workspace with **AI-assisted brainstorming**, **tagging**, **content pipelines**, and **workflow modules** that integrate seamlessly without modifying the core stack.  

---

## Technology Stack
- **Backend:** FastAPI application packaged under `app/`  
- **Database:** SQLite (SQLModel ORM) stored at `data/contenthub.db`  
- **Frontend:** Jinja2 templates rendered by FastAPI with vanilla CSS and progressive JS enhancements  
- **AI Layer:** OpenAI (or local LLM) integration for generating and organizing ideas  
- **Authentication:** Session-based login (with optional OAuth support planned)  
- **CLI Tooling:** Typer-based developer commands in `tools/dev.py`  

---

## Modular Architecture Vision
The platform is structured for **atomic modularity** — each creative capability should live in its own self-contained module.  

Each module must:
- Define routes, templates, and static assets under `app/modules/<module_name>/`  
- Contain a minimal service layer for business logic and persistence  
- Register dependencies and background tasks independently  
- Ship with documentation in `docs/plans/<module_name>_*.md` following the feature process  

The **core idea management** and **AI suggestion** modules will serve as reference implementations for future modules.  

---

## Repository Layout (Target)

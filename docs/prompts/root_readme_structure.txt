```text
TASK
Create or rewrite the main README.md in the repository root to an excellence-level standard.
This README is the authoritative entry point and must represent the repository as a
production-grade, portfolio-quality data engineering system.

GENERAL RULES
- Write with a senior engineering, audit-ready tone
- No marketing language, no filler text, no emojis
- README.md is the single source of truth; link to deeper docs, do not duplicate them
- Assume the reader is a senior engineer, architect, or recruiter
- Prefer explicit examples and evidence over narrative explanation

STRUCTURE (MANDATORY)

1. TITLE & VALUE PROPOSITION
- Repository name
- One-sentence value proposition describing:
  * the problem solved
  * the target user
  * the outcome
- Explicit non-goals / out-of-scope items

2. PROJECT OVERVIEW
- What this system does, end-to-end
- Why it exists (design intent)
- Target personas (e.g. Data Engineer, Reviewer, Maintainer)
- Current status (e.g. Stable / In Progress) and intended usage

3. SYSTEM ARCHITECTURE
- High-level system description (Source → Bronze → Silver → Gold)
- Explanation of Medallion layering and responsibilities
- Run-based execution model (run_id, determinism, idempotency)
- Artifact lifecycle and storage locations
- Reference architecture diagram (link or ASCII, optional but preferred)

4. REPOSITORY STRUCTURE
- Curated tree of key directories only
- Short explanation of each:
  * src/
  * artifacts/
  * tmp/
  * docs/
  * tests/
- Explicit note on what must never be committed (e.g. tmp outputs, secrets)

5. EXECUTION MODEL (SINGLE SOURCE OF TRUTH)
- Entry points for pipeline execution
- Canonical commands:
  * load_1_bronze_layer.py
  * load_2_silver_layer.py
  * load_3_gold_layer.py
- Expected behavior of each step
- Idempotency and re-run behavior

6. QUICK START (REPRODUCIBLE)
- Prerequisites (OS, Python version, tools)
- Environment setup steps
- Minimal commands to execute a full end-to-end run
- Explicit description of expected outputs and where to find them

7. CONFIGURATION & SECRETS
- Configuration strategy (env vars, config files)
- .env.example usage
- Secrets handling rules (never committed)
- Default assumptions and override behavior

8. DATA QUALITY & GOVERNANCE
- Data quality checks per layer
- Schema and contract assumptions
- Handling of breaking vs additive changes
- PII/GDPR considerations (if applicable)
- Lineage and metadata tracking approach

9. OBSERVABILITY & OPERATIONS
- Logging strategy
- Run tracing via run_id
- Error handling and failure modes
- Backfill and recovery strategy
- Performance and scalability notes

10. TESTING STRATEGY
- Test types (unit, integration, pipeline)
- What is tested at which layer
- How to run tests locally
- Definition of Done for changes

11. ARCHITECTURE DECISIONS
- Reference ADR system
- Link to ADR index
- Rule for when an ADR must be added or updated

12. AGENTIC / PROMPT-BASED ANALYSIS (IF PRESENT)
- Purpose of agent-based analysis
- Where prompts live (docs/prompts)
- Where analysis outputs are written (tmp/prompt_analysis)
- Explicit note that outputs are non-versioned

13. CONTRIBUTION & REVIEW
- How to review this repository
- Golden path for understanding the system
- Branching and commit expectations
- Quality gates for pull requests

14. ROADMAP
- Short, explicit list of next steps
- Link to issues or planned work if available

15. LICENSE & LEGAL
- License reference
- Data usage or sample data disclaimer

QUALITY BAR
- A senior engineer must be able to run the system without clarification
- A reviewer must be able to assess architecture quality in under 5 minutes
- No section may contradict another
- All commands and paths must match the actual repository structure
```

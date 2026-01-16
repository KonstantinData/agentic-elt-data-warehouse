TASK
Define and enforce excellence-level requirements for README.md files in
docs/adr/ and all other documentation sub-sections (layer READMEs, artifacts, tmp, prompts).

These READMEs are NOT introductions. They are operational and architectural
control documents that support audits, reviews, and long-term maintenance.

GENERAL PRINCIPLES
- Assume senior engineers and auditors as readers
- No onboarding tone, no repetition of root README
- Each README has a single, clearly defined responsibility
- Every README must answer: “Why does this exist and how is it used?”
- Content must be precise, factual, and verifiable
- Prefer contracts, rules, and invariants over narrative explanation

GLOBAL REQUIREMENTS (APPLY TO ALL SECTION READMEs)
- Explicit scope: what this section covers and what it does not
- Stable terminology aligned with the root README
- Clear ownership of decisions and responsibilities
- Links to upstream and downstream documentation
- No duplicated content; reference instead
- Markdown only, deterministic structure

================================================================
ADR README REQUIREMENTS (docs/adr/README.md)
================================================================

PURPOSE
- Acts as the governance entry point for all architecture decisions
- Explains how decisions are recorded, evaluated, and evolved

MANDATORY CONTENT
1. Role of ADRs in this repository
   - Why ADRs exist
   - What types of decisions require an ADR
   - What explicitly does NOT require an ADR

2. ADR Lifecycle
   - Status definitions (Proposed, Accepted, Superseded, Deprecated)
   - Rules for modifying or superseding ADRs
   - Immutability guarantees for accepted ADRs

3. ADR Index Contract
   - Reference to 0000-adr-index.md as the single index
   - Rule: all ADRs must be registered there
   - Naming and numbering scheme (monotonic, never reused)

4. Decision Authority
   - Who can approve ADRs
   - How disagreements are resolved
   - What happens if no decision is made

5. Change Discipline
   - Requirement to update ADRs on architectural change
   - Consequences of violating ADR consistency

QUALITY BAR
- An external reviewer can understand governance without reading any ADR
- ADR process is unambiguous and enforceable

================================================================
ADR TEMPLATE REQUIREMENTS (docs/adr/template.md)
================================================================

MANDATORY SECTIONS
- Context
- Decision
- Alternatives Considered
- Consequences
- Trade-offs
- Status
- Date

RULES
- No future tense in accepted ADRs
- Decisions must be falsifiable and specific
- Alternatives must be real, not strawmen
- Consequences must include operational and maintenance impact

================================================================
LAYER READMEs (e.g. bronze/, silver/, gold/)
================================================================

PURPOSE
- Define the contract of the layer, not the implementation details

MANDATORY CONTENT
1. Layer Responsibility
   - What problems this layer solves
   - What problems it explicitly does not solve

2. Input Contract
   - Expected inputs
   - Assumptions and invariants
   - Handling of missing or invalid data

3. Output Contract
   - Guarantees provided by this layer
   - Stability expectations for downstream layers

4. Quality Gates
   - Checks enforced in this layer
   - Failure behavior (block, warn, continue)

5. Idempotency & Re-runs
   - Re-run behavior
   - Backfill expectations

QUALITY BAR
- Another engineer can replace the implementation without violating contracts

================================================================
ARTIFACTS README (artifacts/README.md)
================================================================

PURPOSE
- Explain the artifact model and lifecycle

MANDATORY CONTENT
- Artifact types and purpose
- Directory layout rules
- Retention policy
- Versioning strategy
- Relationship to run_id
- What is reproducible vs ephemeral

RULE
- Artifacts are outputs, never inputs

================================================================
TMP / EPHEMERAL OUTPUT READMEs (tmp/, tmp/prompt_analysis/)
================================================================

PURPOSE
- Prevent accidental misuse or versioning

MANDATORY CONTENT
- Explicit statement: non-versioned, non-authoritative
- Lifecycle and cleanup expectations
- Relationship to reproducibility
- Why these outputs exist

RULE
- No business logic must ever depend on tmp outputs

================================================================
PROMPTS / AGENT READMEs (docs/prompts/, src/agents/)
================================================================

PURPOSE
- Document control logic, not LLM behavior

MANDATORY CONTENT
- Role of prompts/agents in the system
- Separation of concerns (system vs working prompts)
- Determinism and audit limitations
- Where outputs are written and why
- Explicit non-goals (e.g. not a source of truth)

================================================================
CROSS-CUTTING QUALITY RULES
================================================================

- Every README must declare:
  * Scope
  * Guarantees
  * Non-goals
- No README may redefine architecture already decided in ADRs
- If a README conflicts with an ADR, the ADR wins
- README content must survive team turnover

DEFINITION OF DONE
- A senior reviewer can assess correctness and intent without running code
- A maintainer can change internals without breaking documented contracts
- An auditor can trace decisions, responsibilities, and boundaries

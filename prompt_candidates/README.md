# Prompt Candidates: Deterministic Column Matching

This directory contains a modular system for deterministic column matching, designed to be domain-agnostic and SME-friendly.

---

## Files

### 1. `system_prompt_template.md` (Generic, Reusable)

The core system prompt framework that works for any domain. It defines:

- **Decision Framework:** Step-by-step process for matching columns (STEP 1-5)
- **Hard Constraints:** Rules that eliminate invalid matches mechanically (data type, cardinality, hierarchy)
- **Semantic Judgment Framework:** How to analyze column meaning deterministically
- **Confidence Scoring:** How to assign confidence scores based on signal evidence
- **Tiebreaker Rules:** Priority order for selecting between similar candidates
- **Match History Integration:** How previous decisions inform current ones
- **Output Requirements:** Format for results and quality checks

**Key Design:** Contains injection points marked `[DOMAIN-SPECIFIC ... INSERTED HERE]` where domain constraints are plugged in.

**Do NOT modify this file for domain-specific rules.** It stays generic so it can be reused for other domains.

---

### 2. `domain_constraints_pension_insurance.md` (Domain-Specific, SME-Friendly)

Domain expertise encoded as structured constraints. SME can modify this file without touching the template.

Contains:

- **Domain Context & Terminology:** Industry definitions
- **Data Type Compatibility Matrix:** What types can match what
- **Cardinality & Hierarchy Constraints:** Population rate rules + hierarchy matching rules
- **Implicit Context Rules:** Domain conventions (e.g., "Amount" = monthly, "Sex" = primary)
- **Tiebreaker Priority Order:** How to resolve ambiguous matches
- **Known Patterns & Manual Matches:** Auto-match patterns SME approves
- **Known False Positives:** Pairs to always reject
- **Unmatched Column Guidance:** Why some columns won't match (expected)
- **Match History:** Verified, rejected, and ambiguous matches (grows over time)

**How SME Updates This File:**

See SECTION 9: SME Modification Guide for step-by-step instructions.

Examples:
- Add new hierarchy level → Edit SECTION 3 Rule 3.3
- Add implicit context rule → Create SECTION 4 Rule 4.X
- Change tiebreaker priority → Edit SECTION 5
- Record verified match → Add to SECTION 8 Verified Matches

---

## How to Use: Generate a Complete Prompt

### Step 1: Start with Template
Copy `system_prompt_template.md` as your base prompt.

### Step 2: Inject Domain Constraints
Replace these injection points with content from `domain_constraints_pension_insurance.md`:

| Injection Point in Template | Replace With | From Domain File |
|---|---|---|
| `[DOMAIN-SPECIFIC RULES INSERTED HERE]` (in PART 2, Constraint Type 2 Rule 3) | Domain Hierarchy Constraints | SECTION 3 Rule 3.3 |
| `[DOMAIN-SPECIFIC IMPLICIT RULES INSERTED HERE]` (in PART 3, Step 2) | All implicit context rules | SECTION 4 All Rules (4.1-4.4) |
| `[DOMAIN-SPECIFIC TIEBREAKER PRIORITY ORDER INSERTED HERE]` (in PART 5) | Priority order list | SECTION 5 Priority Order |
| `[MATCH_HISTORY_VERIFIED]` | Verified matches | SECTION 8 Verified Matches |
| `[MATCH_HISTORY_REJECTED]` | Rejected matches | SECTION 8 Rejected Matches |
| `[MATCH_HISTORY_AMBIGUOUS]` | Ambiguous cases | SECTION 8 Ambiguous Cases |

### Step 3: Pass to LLM
Give the completed prompt (with all injections filled) to Claude or your LLM with the column metadata.

---

## Example: Generate Pension/Insurance Prompt

**Using the files in this directory:**

Template injection points and domain file sources:

```markdown
# PART 2: HARD CONSTRAINTS
## CONSTRAINT TYPE 2: Cardinality & Population Alignment
...
## Rule 3: Domain Hierarchy Constraints

[INSERT: domain_constraints_pension_insurance.md SECTION 3 Rule 3.3]
→ Defines Primary vs. Secondary vs. Contingent matching rules

# PART 3: SEMANTIC JUDGMENT FRAMEWORK
## Step 2: Apply Implicit Context Rules

[INSERT: domain_constraints_pension_insurance.md SECTION 4 All Rules]
→ Defines "Amount"=monthly, "Sex"=primary, "Current"=authoritative, etc.

# PART 5: TIEBREAKER RULES

[INSERT: domain_constraints_pension_insurance.md SECTION 5 Priority Order]
→ Defines: Exact Match > Freshness > Population Alignment > Sample Values > Domain Priority

# PART 6: MATCH HISTORY INTEGRATION
## Verified Match History

[INSERT: domain_constraints_pension_insurance.md SECTION 8 Verified Matches]
→ Initially empty; grows with each SME-verified match

[INSERT: domain_constraints_pension_insurance.md SECTION 8 Rejected Matches]
[INSERT: domain_constraints_pension_insurance.md SECTION 8 Ambiguous Cases]
```

---

## Workflow: Test & Iterate

### Run 1: Initial Testing
1. Generate prompt by injecting domain constraints into template
2. Run with column_matcher agent
3. Record matches: ✓ Correct, ✗ Incorrect, ? Uncertain

### Run 2: Add Match History
1. SME reviews matches from Run 1
2. Confirmed matches → Add to SECTION 8 Verified Matches
3. Rejected/ambiguous matches → Add to SECTION 8 Rejected or Ambiguous
4. Regenerate prompt with updated match history
5. Re-run agent; expect higher consistency and fewer false positives

### Run 3+: Iterative Refinement
1. If non-determinism persists: Check which specific matches vary
2. Add/refine implicit context rules (SECTION 4)
3. Adjust tiebreaker priority if needed (SECTION 5)
4. Retest; track convergence

---

## Design Principles

### 1. **Determinism Through Constraint Reduction**
Hard constraints eliminate invalid candidates mechanically, reducing LLM decision variance. By the time semantic judgment is needed, there's often only one candidate.

### 2. **Auditability**
Every match decision can be traced to:
- A hard constraint (type, cardinality, hierarchy)
- A semantic judgment rule (implicit context, domain meaning)
- A tiebreaker rule (priority order)
- A match history entry (previous verification)

### 3. **Generalizability**
The template applies to any domain. Only domain_constraints file changes. This allows reuse across domains without template modification.

### 4. **SME-Friendly**
Domain expert can modify constraints without prompt engineering knowledge. Clear sections, examples, and modification guide.

### 5. **Learnable**
Match history grows with each SME review, reducing variance over time. Verified patterns inform future runs.

---

## Critical Implementation Notes

### Hard Constraints Are Not Optional
- Type mismatch → Automatic rejection (no semantic judgment)
- Cardinality mismatch → Automatic rejection
- Hierarchy mismatch → Automatic rejection

The LLM must apply these as elimination rules, not scoring factors.

### Semantic Judgment Is Scoped
LLM does NOT:
- Compare name similarity
- Make up domain meaning
- Negotiate tiebreakers
- Override hard constraints

LLM DOES:
- Confirm domain meaning matches (given constraint candidates)
- Identify hierarchy level from name
- Apply implicit context rules (given)
- Score semantic match strength (given candidates)

### Confidence Scores Reflect Evidence, Not Intuition
Score assignments must cite:
- Which hard constraints passed (type, cardinality, hierarchy)
- Which semantic signals aligned (domain meaning, implicit context)
- Which tiebreaker rule applied (if needed)

Avoid high scores without multiple confirming signals.

### 1:1 Constraint Is Enforced Post-LLM
- LLM produces candidate rankings for each input column
- Assignment algorithm (greedy or Hungarian) enforces 1:1 matching
- Optional: Build second validation step that checks 1:1 constraint automatically

---

## Next Steps

1. **Test:** Use these files to generate a complete prompt for your column_matcher agent
2. **Run:** Execute with your test data; record results
3. **Evaluate:** Which matches were correct? Which varied? Which failed?
4. **Refine:** Update domain_constraints.md based on findings
5. **Iterate:** Regenerate prompt, retest, track convergence

Once stable with pension/insurance, the same template can be reused for other domains by creating new domain_constraints files.

---

## Questions & Support

**Template unclear?** → Refer to PART 1 Decision Framework and PART 2-5 rules with examples.

**Domain rules not capturing my domain?** → Edit domain_constraints.md; see SECTION 9 SME Modification Guide.

**Prompt too long?** → You can condense by removing detailed examples (keep rules); inject match history only after Run 1.

**Want to add new domain?** → Copy domain_constraints_pension_insurance.md, rename, update SECTIONS 1-5, reuse system_prompt_template.md.


# DOMAIN CONSTRAINTS: PENSION/INSURANCE
## Structure for Easy SME Updates

This file defines domain-specific rules that inject into the generic system prompt template.
**SME:** Modify this file to add/refine rules. Do NOT modify the system_prompt_template.md.

---

# SECTION 1: DOMAIN CONTEXT & TERMINOLOGY

## Industry
Pension and insurance policy administration (retirement benefits, annuities, contingent beneficiaries)

## Core Entities
- **Member/Annuitant/Participant:** Person covered by the policy (primary beneficiary)
- **Beneficiary:** Person who receives benefits (primary or contingent)
- **Contingent/Secondary Beneficiary:** Receives benefits if primary dies (hierarchical: 1st, 2nd, 3rd)
- **Policy/Scheme:** Insurance policy or pension scheme
- **Annuity:** Regular periodic payment (assumed monthly unless otherwise stated)

## Key Relationships
- Primary beneficiary ≠ Contingent beneficiary (different hierarchy levels)
- Secondary beneficiary = 1st Contingent beneficiary (SAME position, different naming convention)
- Tertiary beneficiary = 2nd Contingent beneficiary (SAME position)
- All amounts are assumed monthly unless explicitly stated otherwise

---

# SECTION 2: DATA TYPE COMPATIBILITY MATRIX

This matrix defines which input column types can match which reference column types.

| Reference Type | Input Can Match From | Notes | Examples |
|---|---|---|---|
| date | date, mixed (if date-like) | Format differences OK (YYYY-MM-DD vs DD/MM/YYYY) | "Date of Birth" input → "Primary Date Of Birth" reference |
| numeric | numeric, mixed (if numeric-like) | Includes amounts, counts, identifiers as numbers | "Monthly Benefit" input → "Primary Amount" reference |
| text | text, mixed (if text-like) | Includes categories, names, codes | "Sex" input → "Primary Gender" reference |
| identifier (text pattern) | identifier only | Specific patterns: "1B_C10001-1" format | "UniqueID" input → "Record ID" reference |
| empty | empty ONLY | Do NOT match empty to populated | "All Empty Column" input → "Escalation Group Name" reference |

**Application Rule:** Before considering semantic meaning, reject any type-incompatible pair.

---

# SECTION 3: CARDINALITY & HIERARCHY CONSTRAINTS

## Rule 3.1: Population Rate Alignment

| Reference Population | Input Must Have | Exception | Example |
|---|---|---|---|
| 1.0 (fully populated) | ≥0.95 OR domain rule allows | Sparse contingent fields CAN match if primary field fully populated (different entity) | "Sex" (fully populated) ↔ "1st Contingent Sex" (sparse) = OK (different entity) |
| 0.35-0.40 (sparse) | 0.25-0.50 (similar) | None | "Secondary Gender" (0.347) ↔ "1st Contingent Gender" (varies) = OK if similar rates |
| 0.0 (empty) | 0.0 (both empty) | None | "2nd Contingent Sex" (empty) ↔ empty reference only |

**Key Insight:** Population sparsity often signals a different hierarchical level, not a mismatch. Use hierarchy rules to validate.

---

## Rule 3.2: Uniqueness Constraints

| Reference Uniqueness | Input Must Match | Reason |
|---|---|---|
| all_unique (e.g., Record ID, Unique Life ID) | all_unique | Identifiers can't match non-unique columns |
| high_cardinality (>1900 unique out of 1999 rows) | >50% unique | High-variance fields match high-variance |
| low_cardinality (2-10 unique) | <50% unique | Constant/categorical patterns match |

**Application:** If reference column has all_unique, reject input columns with any duplicates.

---

## Rule 3.3: Domain Hierarchy Constraints (CRITICAL)

This is the most important rule for deterministic matching in pension/insurance.

### Hierarchy Levels (Priority Order)

```
LEVEL 1 (Primary): Primary beneficiary / Member / Annuitant
  - Prefix: "Primary" OR no prefix (implies primary)
  - Cardinality: Typically fully populated (1.0)
  - Examples: "Sex", "Date of Birth", "Primary Gender", "Primary Amount"

LEVEL 2 (Secondary): First contingent beneficiary / Secondary beneficiary
  - Prefix: "Secondary" OR "1st Contingent" OR "1st Annuitant / Beneficiary"
  - Cardinality: Typically sparse (0.30-0.40 population)
  - Examples: "Secondary Gender", "1st Contingent Date of Birth"

LEVEL 3 (Tertiary): Second contingent beneficiary
  - Prefix: "2nd Contingent" OR "Tertiary"
  - Cardinality: Very sparse (<0.01 population)
  - Examples: "2nd Contingent Date of Birth"

LEVEL 4 (Quaternary): Third contingent beneficiary
  - Prefix: "3rd Contingent"
  - Cardinality: Extremely sparse
  - Examples: "3rd Contingent Date of Birth"
```

### Hierarchy Matching Rules

| Rule | Meaning | Examples |
|---|---|---|
| **Same Level Must Match** | If input is "Secondary X", reference must be "Secondary X" or equivalent | Input "Secondary Gender" → Reference "Secondary Gender" ✓ |
| **Level Cannot Cross** | Input level CANNOT match reference of different level | Input "Secondary Gender" → Reference "Primary Gender" ✗ |
| **Equivalent Names Cross Levels** | "Secondary" = "1st Contingent" = "1st Annuitant/Beneficiary" (all Level 2) | Input "1st Contingent Date of Birth" → Reference "Secondary Date of Birth" ✓ |
| **No Primary→Contingent** | Primary fields CANNOT match any contingent fields | Input "Sex" → Reference "Secondary Gender" ✗ (unless "Sex" is already scoped to contingent) |
| **Contingent Count Must Align** | "1st Contingent" ≠ "2nd Contingent" ≠ "3rd Contingent" | Input "1st Contingent Sex" → Reference "2nd Contingent Sex" ✗ |

### Hierarchy Rule Application

Before semantic matching, verify hierarchy alignment:

1. Extract hierarchy prefix from input column name
2. Determine expected hierarchy level
3. Check if reference column matches that level
4. If mismatch → REJECT (hard constraint violation)

**Example Decision Tree:**

```
Input: "1st Contingent Annuitant / Beneficiary Date of Birth"
  → Hierarchy: "1st Contingent" = Level 2 (Secondary)

Candidates:
  A. Reference "Secondary Date of Birth" (Level 2) → PASS hierarchy rule
  B. Reference "Primary Date of Birth" (Level 1) → FAIL hierarchy rule (cross-level)
  C. Reference "2nd Contingent Date of Birth" (Level 3) → FAIL hierarchy rule (wrong contingent count)

Result: Only A passes hard constraints; evaluate semantic match for A only
```

---

# SECTION 4: IMPLICIT CONTEXT RULES

These rules clarify ambiguous meanings without requiring SME interpretation.

## Rule 4.1: Frequency Convention

**If column name includes "Amount" but no frequency modifier → assume MONTHLY**

| Input Name Pattern | Implicit Meaning | Reference Match |
|---|---|---|
| "Benefit", "Amount", "Monthly Benefit" | Monthly payment | Reference "Primary Amount" (assumed monthly) |
| "Annual Benefit" | Yearly payment | Reference must explicitly be annual OR divide by 12 |
| "Total Benefit", "Total Current Monthly Benefit" | Sum across all beneficiaries | Reference "Total Current Monthly Benefit" |
| "Lump Sum", "Cash Refund" | One-time payment | Only match reference lump sum fields |

**Application:** When scoring "Current Monthly Benefit" ↔ "Primary Amount", note: "implicit context (monthly) aligns with reference convention"

---

## Rule 4.2: Temporal State Convention

**If column includes temporal qualifier, rank by recency:**

| Temporal Qualifier | Authority Level | Matching Priority |
|---|---|---|
| "Current" (no other temporal marker) | Most authoritative | HIGHEST (1st choice) |
| "At Commencement" (historical state at policy start) | Baseline reference | MEDIUM (2nd choice) |
| "To Be Purchased" (future state) | Planned but not in effect | LOWEST (3rd choice, avoid unless no alternative) |
| No temporal marker (just "Form of Annuity") | Assume current state | HIGH (treat as "Current") |

**Example Application:**
- Input: "Form of Annuity to Be Purchased"
- Candidates: "Form of Annuity" (current) OR "Original Form of Annuity at Commencement" (historical)
- Decision: Choose "Form of Annuity" (current is more authoritative than future)

---

## Rule 4.3: Role/Identity Convention

**If column name has no role prefix, assume PRIMARY role:**

| Input Name | Implicit Meaning | Why |
|---|---|---|
| "Sex" | Primary sex (member's sex) | No "Secondary" prefix = primary |
| "Date of Birth" | Primary DOB | No "1st Contingent" prefix = primary |
| "Amount" | Primary benefit amount | No hierarchy prefix = primary |
| "Gender" | Primary gender | Same as "Sex"; no prefix = primary |

**Application:** When matching "Sex" (no prefix), can only match reference "Primary Gender" (not "Secondary Gender"), unless context explicitly scopes to contingent.

---

## Rule 4.4: Attribute Mapping

**Common column names that represent the same domain concept:**

| Domain Concept | Equivalent Names | Preferred Match |
|---|---|---|
| Gender | Sex, Gender | Either (semantic match) |
| Benefit Amount | Amount, Benefit, Monthly Benefit, Annual Benefit | Amount (if no frequency modifier, assume monthly) |
| Date of Birth | DOB, Date of Birth, Birth Date | Date of Birth (preferred) |
| Status | Status, Participant Status, Current Status | Status (clearest) |
| Beneficiary Identifier | Record ID, Unique ID, Life ID, Policy ID | Match by uniqueness pattern, not name |
| Form Type | Form of Annuity, Annuity Form, Type | Form of Annuity (preferred) |
| Death Flag | Deceased Flag, Death Indicator, Deceased Indicator | Deceased Flag (preferred) |
| Relationship | Relationship, Relation, Relationship to Participant | Relationship (with hierarchy context) |

**Application:** When input name is synonym, match to preferred reference name if available.

---

# SECTION 5: TIEBREAKER PRIORITY ORDER

When multiple reference columns pass hard constraints with similar semantic match scores (within ±0.05), apply tiebreakers in this priority order:

### Priority Order (Apply in Sequence, Stop at First Match)

1. **Exact Name Match or Clear Synonym (HIGHEST)**
   - Example: Input "Sex" + Reference "Primary Gender" (exact synonym)
   - Score boost: +0.05

2. **Data Freshness / Temporal State**
   - Rank: Current > Historical > Future
   - Example: "Form of Annuity" > "Original Form of Annuity at Commencement" > "Form of Annuity to Be Purchased"
   - Score boost: +0.04

3. **Population Rate Alignment**
   - Prefer reference columns with population rates close to input population rate
   - Example: Sparse input (0.39 pop) matches sparse reference (0.35 pop) over fully populated reference (1.0 pop)
   - Score boost: +0.03

4. **Sample Value Overlap**
   - Prefer reference columns whose sample values align with input sample values
   - Example: Input sample values [M, F] align with reference sample values [Male, Female] = strong match
   - Example: Input sample values [1842.05, 125.26] match reference sample values exactly = perfect overlap
   - Score boost: +0.02

5. **Domain Importance / Field Priority**
   - Core fields rank higher than supplementary fields
   - Example: "Record ID" > "Pricing Group", "Primary Amount" > "Mortality Flag"
   - Score boost: +0.01

6. **Hierarchy Completeness (LOWEST)**
   - Prefer matching complete hierarchy levels (e.g., both "Primary Gender" and "Primary Amount" match) over partial
   - Score boost: +0.005

**Application Example:**

```
Input: "Amount" (numeric, fully populated, sample: 1842.05, 125.26)
Candidates after semantic judgment:
  A. "Primary Amount" (numeric, 1.0 pop, sample: 1842.05, 125.26) → Semantic: 0.98
  B. "Secondary Amount" (numeric, 1.0 pop, sample: 1155.44, 78.57) → Semantic: 0.75

Tiebreaker not needed (0.98 >> 0.75)
Result: Match A ("Primary Amount") with confidence 0.98

---

Input: "Form of Annuity to Be Purchased" (text, fully populated)
Candidates after semantic judgment:
  A. "Form of Annuity" (current form) → Semantic: 0.78
  B. "Original Form of Annuity at Commencement" (historical form) → Semantic: 0.77

Difference: 0.01 (within ±0.05 tolerance → apply tiebreaker)
Tiebreaker Rule: Data Freshness → "Current" > "Historical"
Result: Select A ("Form of Annuity") with confidence 0.78
```

---

# SECTION 6: KNOWN PATTERNS & MANUAL MATCHES

SME-verified patterns that can be recognized without full constraint evaluation.

## 6.1: Pattern Mappings (Auto-Match if Both Conditions Met)

| Input Pattern | Reference Pattern | Confidence | Conditions |
|---|---|---|---|
| "UniqueID" OR "Unique ID" with pattern "C\d+" | "Unique Life ID" with pattern "C\d+" | 0.98 | Population rate both 1.0, unique count match |
| Record ID with pattern "1B_C\d+" | Record ID with same pattern | 0.99 | All unique, population 1.0 |
| "Sex" (text, 2-3 values: M/F/U) | "Primary Gender" (text, same values) | 0.95 | Population both 1.0, value overlap |
| "Date of Birth" (date format) | "Primary Date of Birth" (date format, same sample dates) | 0.96 | Population both 1.0, date range match |
| "Current Monthly Benefit" (numeric, sample ~1800-3000) | "Primary Amount" (numeric, same sample) | 0.97 | Population both 1.0, sample values match exactly |

**Application:** If input exactly matches pattern and all conditions met → immediate match with given confidence (skip semantic judgment).

## 6.2: Known False Positives (Always Reject)

| Input Column | Reference Column | Reason |
|---|---|---|
| "Offered Lump Sum - Retirement" | Any non-lump-sum field | Different concept (offer vs. actual amount) |
| "Union or Non-Union" | Any benefit field | Union status ≠ benefit amount |
| "Salaried or Hourly Status" | Any demographic field | Employment status ≠ demography |
| "Duplicate Participant" | Any reference field | Flag for data quality, not domain match |
| "Special Inflation Benefit Indicator" | "Form of Annuity" | Different concepts (benefit adjustment vs. structure) |

**Application:** If input/reference pair listed → immediate rejection (confidence = 0.0, no match).

---

# SECTION 7: UNMATCHED COLUMN GUIDANCE

Some input columns may not have reference equivalents. This is expected and valid.

## Expected Unmatched Input Columns

| Input Column | Why No Match | Category |
|---|---|---|
| "Participant Status Category: Retiree" | Constant value column (only value: "Retiree"); reference "Status" has multiple values | Data quality signal; skip |
| "Duplicate Participant" | Flag for data integrity; not a domain column | Metadata, not domain |
| "# of Duplicates for each ID" | Meta-count, not domain data | Metadata, not domain |
| "Offered Lump Sum - Retirement" | Offer flag (availability), not actual data | Different domain concept |
| "Offered Lump Sum - TV Window" | Offer flag, not actual data | Different domain concept |
| "Union or Non-Union" | Employment classification (reference has no equiv) | Domain boundary |
| "Salaried or Hourly Status" | Employment classification | Domain boundary |
| "Contingent Annuitant Flag" | Indicator that contingents exist (reference has structure, not flag) | Implicit in contingent columns |
| "Number of Contingent Annuitants / Beneficiaries" | Count of contingents; reference structure implies this | Implicit in column structure |
| "Ultimate Monthly Benefit" | Conditional/scenario benefit (not current); reference tracks current | Different temporal scope |
| "SSLI or SS Supplement End Date" | Social Security supplement (reference focuses on pension, not SS) | Partial domain overlap |
| "Certain Period End Date" | Rare variant of annuity structure; reference "End Date" general | Partial domain overlap |

**Application Rule:** Do NOT force matches for columns in this list. Leave them unmatched, note reason as "No equivalent reference column for [domain concept]".

## Expected Unmatched Reference Columns

| Reference Column | Why No Input Match | Category |
|---|---|---|
| "Pricing Group" | Input provides no equivalent; constant value (all 0) | Administrative, not domain |
| "Primary/Secondary/etc. Base Mortality Flag" | Input has no mortality modeling; reference is actuarial | Technical calculation, not input data |
| "Primary/Secondary/etc. Mortality Scalar Flag" | Input has no mortality modeling | Technical calculation, not input data |
| "Primary/Secondary/etc. Mortality Improvement Flag" | Input has no mortality modeling | Technical calculation, not input data |
| "Escalation Group Name" | Input has no escalation groups; reference is empty anyway | Administrative, not domain |
| "Pop-up Amount", "Cash Refund As of Date", "Cash Refund Amount", "Death Benefit", "Guaranteed Months" | Input has no equivalent fields for these special provisions | Pension-specific provisions not in input |

**Application Rule:** Do NOT attempt to match input columns to these reference columns. These are output/calculated columns, not input mappings.

---

# SECTION 8: MATCH HISTORY

This section is populated by the system after SME verification. Initially empty.

## Verified Matches (SME-Approved)

*[To be populated as matches are verified]*

Example format:
```
- Input: "Sex" → Reference: "Primary Gender"
  | Confidence: 0.95 | Population: Input(1.0)↔Ref(1.0) | Type: text↔text | Verified: True
  | SME Note: "Confirmed; sex/gender are synonyms"

- Input: "Current Monthly Benefit" → Reference: "Primary Amount"
  | Confidence: 0.97 | Population: Input(1.0)↔Ref(1.0) | Type: numeric↔numeric | Verified: True
  | SME Note: "Sample values match exactly; implicit context (monthly) aligns"
```

## Rejected Matches (SME-Approved Rejections)

*[To be populated as needed]*

Example:
```
- Input: "Offered Lump Sum - Retirement" ≠ Reference: "Primary Amount"
  | Reason: "Different concepts; 'Offered' is flag/availability, 'Amount' is actual value"
```

## Ambiguous Cases (Flagged for SME Review)

*[To be populated when model produces variant outputs]*

Example:
```
- Input: "Form of Annuity to Be Purchased"
  | Candidates: ["Form of Annuity" (current), "Original Form of Annuity at Commencement" (historical)]
  | Model Default: "Form of Annuity (0.78)" but "Original Form (0.77)" close behind
  | SME Decision: "Choose 'Form of Annuity' (current form is authoritative; future state not in force)"
  | Applied Rule: Tiebreaker Rule #2 (Data Freshness)
```

---

# SECTION 9: SME MODIFICATION GUIDE

When updating this file:

1. **Add new hierarchy levels?**
   - Edit SECTION 3 Rule 3.3, add to "Hierarchy Levels (Priority Order)"
   - Update hierarchy matching rules table

2. **Add new implicit context rules?**
   - Edit SECTION 4, add new Rule 4.X
   - Include domain concept, convention, and examples

3. **Change tiebreaker priority?**
   - Edit SECTION 5, reorder "Priority Order (Apply in Sequence)"
   - Include score boost rationale

4. **Add known patterns?**
   - Edit SECTION 6.1, add row to pattern mappings
   - Include conditions that trigger automatic match

5. **Add false positives to avoid?**
   - Edit SECTION 6.2, add row to known false positives
   - Always include reasoning

6. **Update match history?**
   - Edit SECTION 8 after SME verification
   - Use provided format for consistency

7. **Add new unmatched column reasons?**
   - Edit SECTION 7, add row explaining why no match
   - Categorize as Data Quality, Metadata, Domain Boundary, or Partial Overlap

---

# REFERENCE: Injection Points in System Prompt Template

These sections of this file are injected into the generic system prompt template:

| System Prompt Section | Injection Point | Domain File Source |
|---|---|---|
| PART 2: Hard Constraints → Constraint Type 2 Rule 3 | Domain Hierarchy Constraints | SECTION 3 Rule 3.3 |
| PART 3: Semantic Judgment → Step 2 | Apply Implicit Context Rules | SECTION 4 All Rules |
| PART 5: Tiebreaker Rules | Tiebreaker Priority Order | SECTION 5 Priority Order |
| PART 6: Match History | Verified/Rejected/Ambiguous | SECTION 8 All Subsections |

**To generate prompt:** Use domain_constraints.md SECTION 3, 4, 5, and 8 to populate the generic template.


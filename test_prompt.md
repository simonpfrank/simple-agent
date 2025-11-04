# THE TASK OVERVIEW
* You are a data expert specialized in column matching. You are able to see patterns easily and detect anomalies.
* You may be an expert in a specific domain, in which case you will be provided domain context.
* Your task is to match input columns to reference columns based on their metadata, names, data types, and patterns.

Analyze the column information carefully and classify matches with confidence scores between 0.0 and 100.

## IMPORTANT RULES:
- You can only match one input column to one reference column (1:1 matching)
- If there is no good match, do not force a match
- Use MULTIPLE SIGNALS to validate matches, not just name similarity

## MATCHING FACTORS (in order of importance):
1. Sample values alignment (strong indicator when values match or have obvious pattern)
2. Data type compatibility (must be compatible)
3. Column name semantics (consider domain-specific terminology)
4. Data patterns and formats
5. Population rates and data quality
6. Business context and domain knowledge

### MULTI-SIGNAL MATCHING:
A strong match should have 3+ signals aligning:
- ✓ Sample values match or clearly related (e.g., M/F vs Male/Female)
- ✓ Data types compatible (both dates, both identifiers, both text)
- ✓ Semantic meaning similar (considering domain context)
- ✓ Patterns align (ID formats, date formats, etc.)
- ✓ 100% populated columns with all unique values are more likely to match other unique identifier columns

## CONFIDENCE SCORING GUIDELINES:
- 0.95-100: Multiple strong signals (values + types + semantics + domain)
- 0.85-0.94: Strong semantic match with confirming signals
- 0.70-0.84: Good match but some uncertainty (e.g., no sample values to confirm)
- 0.60-0.69: Weak match, review recommended
- <0.60: Do not suggest as match

Be conservative with confidence scores. Only assign high confidence (>0.9) when you have multiple confirming signals.

# IMPORTANT ABOUT COLUMN NAMES:
When you see column names in parentheses (e.g., "UniqueID (Unique ID)"), use the ACTUAL FIELD NAME (shown first, before parentheses) in your JSON response.
The name in parentheses is a cleaned/readable version for context only.
For example, if you see:
- UniqueID (Unique ID): text

# TASK DETAIL
* You are an expert actuary and understand all terms related to pensions and insurance.
* Match columns for pension/insurance data.

## PENSION/INSURANCE DATA HELPFUL INFORMATION:

### Beneficiary Hierarchy Equivalences:
- secondary beneficiary = 1st contingent beneficiary (SAME position)
- tertiary beneficiary = 2nd contingent beneficiary (SAME position)
- primary beneficiary ≠ contingent beneficiary (DIFFERENT positions)

### Common Terminology:
- Policy/Scheme = Insurance policy or pension scheme
- Member/Annuitant = Person covered by the policy
- Beneficiary = Person who receives benefits
- Contingent = Backup/conditional beneficiary
- Vesting = Entitlement to benefits
- Commutation = Lump sum payment

## Description of the data
- The reference data is lists of pension policies, which have a primary and secondary beneficiary.
- There may be record ids which refer to the row and there may be policy ids which refer to the policy or both, record ids are unique,
    policy ids can be unique or multiples
- The data is likely to contain general details such as zip code/post code, State/County policy holder's status, data of birth
- Some companies refer to non primary beneficiaries as contingent annuitant.
- Sometimes pension amount can be referred to as benefit amount
 - in many cases the column names contain a lot of words to describe the column precisely but the pattern can be reversed
    - e.g.
        - {adjectives or hierarchy for the data} {words to describe what the column contains}
    - so try to identify what it contains, then who it what is it refering to for the column
    - Example
        - reference column is secondary gender so the second person who benefits
        - this may match to  1st Contingent Annuitant / Beneficiary Sex in the following way
            - the column contains sex or gender information (at the end of the column name)
            - 1st contigent Annuitant / Beneficiary is the 1st person after the primary who recieves a benefit therefore secondary beneficiary so secondary gender

## PRIORITY REFERENCE COLUMNS TO MATCH IF POSSIBLE:
- Record ID,
- Unique Life ID,
- Status,
- State,
- Zipcode,
- Primary Gender,
- Primary Date of Birth,
- Secondary Gender,
- Secondary Date of Birth,
- Form of Annuity,
- Start Date,
- End Date,
- Primary Amount,
- Secondary Amount,
- Pop-up Amount,
- Cash Refund As of Date,
- Cash Refund Amount,
- Death Benefit,
- Guaranteed Months


## REFERENCE COLUMNS NOT TO MATCH:
- If a reference column is all 0 or all blank or all None ignore it, don't try to match it
### Ignore the following reference columns:
- Primary Base Mortality Flag,
- Primary Mortality Scalar Flag,
- Primary Mortality Improvement Flag,
- Secondary Base Mortality Flag,
- Secondary Mortality Scalar Flag,
- Escalation Group Name Secondary Mortality Improvement Flag

## MANUAL MATCHES (HIGH CONFIDENCE - FOLLOW THESE):
- None derived yet

## SUCCESSFUL PATTERNS IN THIS DOMAIN:
- None derive yet

## KNOWN FALSE POSITIVES (DO NOT MATCH):
- None derived yet


Please match the input columns to the reference columns and return the result in the specified JSON format.

## REFERENCE COLUMN METADATA:
```JSON
{
"file_type": "reference",
"total_columns": 27,
"total_rows": 1999,
"columns": [
{
"name": "Record ID",
"clean_name": "Record ID",
"data_type": "text",
"category": "identifier",
"description": "Identifier column: Fully populated, all values unique, consistent format",
"population_percent": 100,
"unique_count": 1999,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1B_C10001-1",
"1B_C10001-2",
"1B_C10001-3",
"1B_C10001-4",
"1B_C10002-1"
],
"characteristics": [
"fully_populated",
"all_unique",
"high_cardinality",
"consistent_pattern"
]
},
{
"name": "Unique Life ID",
"clean_name": "Unique Life ID",
"data_type": "text",
"category": "identifier",
"description": "Identifier column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 1443,
"total_count": 1999,
"pattern": "AAA999",
"sample_values": [
"C10001",
"C10002",
"C10003",
"C10004",
"C10005"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "Status",
"clean_name": "Status",
"data_type": "text",
"category": "category",
"description": "Category column: Fully populated",
"population_percent": 100,
"unique_count": 2,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"Pensioner",
"Beneficiary"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "State",
"clean_name": "State",
"data_type": "text",
"category": "category",
"description": "Category column: Well populated, consistent format",
"population_percent": 0.9974987493746873,
"unique_count": 52,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"FL",
"CA",
"TX",
"WA",
"RI"
],
"characteristics": [
"consistent_pattern"
]
},
{
"name": "Zipcode",
"clean_name": "Zipcode",
"data_type": "mixed",
"category": "general",
"description": "General column: Well populated, consistent format",
"population_percent": 0.9974987493746873,
"unique_count": 1329,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"34202",
"90706",
"77056",
"77325",
"98723"
],
"characteristics": [
"partially_numeric",
"consistent_pattern"
]
},
{
"name": "Pricing Group",
"clean_name": "Pricing Group",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, constant value, numeric values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"0"
],
"characteristics": [
"fully_populated",
"constant_value",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Primary Gender",
"clean_name": "Primary Gender",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated",
"population_percent": 100,
"unique_count": 2,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"Male",
"Female"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "Primary Date of Birth",
"clean_name": "Primary Date Of Birth",
"data_type": "date",
"category": "date",
"description": "Date column: Fully populated, date values, consistent format",
"population_percent": 100,
"unique_count": 453,
"total_count": 1999,
"pattern": "YYYY-MM-DD",
"sample_values": [
"1950-11-15 00:00:00",
"1933-08-15 00:00:00",
"1927-01-15 00:00:00",
"1931-10-15 00:00:00",
"1967-09-15 00:00:00"
],
"characteristics": [
"fully_populated",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "Primary Base Mortality Flag",
"clean_name": "Primary Base Mortality Flag",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated",
"population_percent": 100,
"unique_count": 34,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1W[1500- 2250)PM",
"1B[0- 750)BF",
"1W[1500- 2250)BF",
"1W[750- 1500)PF",
"1M[0- 750)PM"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "Primary Mortality Scalar Flag",
"clean_name": "Primary Mortality Scalar Flag",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 2,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1_NonDisabled",
"2_Disabled"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "Primary Mortality Improvement Flag",
"clean_name": "Primary Mortality Improvement Flag",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 8,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1WM",
"1BF",
"1WF",
"1MM",
"1MF"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "Secondary Gender",
"clean_name": "Secondary Gender",
"data_type": "text",
"category": "general",
"description": "General column: Sparse",
"population_percent": 0.3471735867933967,
"unique_count": 3,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"Female",
"Male"
],
"characteristics": [
"sparse"
]
},
{
"name": "Secondary Date of Birth",
"clean_name": "Secondary Date Of Birth",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, date values, consistent format",
"population_percent": 0.3471735867933967,
"unique_count": 293,
"total_count": 1999,
"pattern": "YYYY-MM-DD",
"sample_values": [
"1951-04-15 00:00:00",
"1947-12-15 00:00:00",
"1948-01-15 00:00:00",
"1958-11-15 00:00:00",
"1954-11-15 00:00:00"
],
"characteristics": [
"sparse",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "Secondary Base Mortality Flag",
"clean_name": "Secondary Base Mortality Flag",
"data_type": "text",
"category": "general",
"description": "General column: Sparse",
"population_percent": 0.3471735867933967,
"unique_count": 18,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1W[1500- 2250)SF",
"1W[750- 1500)SM",
"1M[0- 750)SF",
"1W[750- 1500)SF",
"1M[0- 750)SM"
],
"characteristics": [
"sparse"
]
},
{
"name": "Secondary Mortality Scalar Flag",
"clean_name": "Secondary Mortality Scalar Flag",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.3471735867933967,
"unique_count": 2,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1_NonDisabled"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "Secondary Mortality Improvement Flag",
"clean_name": "Secondary Mortality Improvement Flag",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.3471735867933967,
"unique_count": 9,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"1WF",
"1WM",
"1MF",
"1MM",
"2WF"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "Form of Annuity",
"clean_name": "Form Of Annuity",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated",
"population_percent": 100,
"unique_count": 4,
"total_count": 1999,
"pattern": "varied",
"sample_values": [
"JS",
"SLA",
"JS & SS",
"SLA & SS"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "Escalation Group Name",
"clean_name": "Escalation Group Name",
"data_type": "empty",
"category": "name",
"description": "Name column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 1999,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "Start Date",
"clean_name": "Start Date",
"data_type": "date",
"category": "date",
"description": "Date column: Fully populated, constant value, date values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "YYYY-MM-DD",
"sample_values": [
"2024-05-15 00:00:00"
],
"characteristics": [
"fully_populated",
"constant_value",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "End Date",
"clean_name": "End Date",
"data_type": "date",
"category": "date",
"description": "Date column: Fully populated, date values, consistent format",
"population_percent": 100,
"unique_count": 54,
"total_count": 1999,
"pattern": "YYYY-MM-DD",
"sample_values": [
"9999-09-09 00:00:00",
"2024-11-01 00:00:00",
"2032-12-01 00:00:00",
"2028-07-01 00:00:00",
"2030-05-01 00:00:00"
],
"characteristics": [
"fully_populated",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "Guaranteed Months",
"clean_name": "Guaranteed Months",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, constant value, numeric values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"0"
],
"characteristics": [
"fully_populated",
"constant_value",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Primary Amount",
"clean_name": "Primary Amount",
"data_type": "numeric",
"category": "amount",
"description": "Amount column: Fully populated, high variety, numeric values",
"population_percent": 100,
"unique_count": 1981,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"1842.05",
"125.26",
"28.57",
"3.57",
"652.64"
],
"characteristics": [
"fully_populated",
"high_cardinality",
"all_numeric"
]
},
{
"name": "Secondary Amount",
"clean_name": "Secondary Amount",
"data_type": "numeric",
"category": "amount",
"description": "Amount column: Fully populated, numeric values",
"population_percent": 100,
"unique_count": 692,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"1155.44",
"78.57",
"0",
"778.64",
"35.77"
],
"characteristics": [
"fully_populated",
"all_numeric"
]
},
{
"name": "Pop-up Amount",
"clean_name": "Pop-up Amount",
"data_type": "numeric",
"category": "amount",
"description": "Amount column: Fully populated, constant value, numeric values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"0"
],
"characteristics": [
"fully_populated",
"constant_value",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Cash Refund As of Date",
"clean_name": "Cash Refund As Of Date",
"data_type": "numeric",
"category": "date",
"description": "Date column: Fully populated, constant value, numeric values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"0"
],
"characteristics": [
"fully_populated",
"constant_value",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Cash Refund Amount",
"clean_name": "Cash Refund Amount",
"data_type": "numeric",
"category": "amount",
"description": "Amount column: Fully populated, constant value, numeric values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"0"
],
"characteristics": [
"fully_populated",
"constant_value",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Death Benefit",
"clean_name": "Death Benefit",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, constant value, numeric values, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 1999,
"pattern": "99999",
"sample_values": [
"0"
],
"characteristics": [
"fully_populated",
"constant_value",
"all_numeric",
"consistent_pattern"
]
}
] }
```

## INPUT COLUMN METADATA:
```JSON
{
"file_type": "input",
"total_columns": 43,
"total_rows": 2570,
"columns": [
{
"name": "Special Inflation Benefit Indicator",
"clean_name": "Special Inflation Benefit Indicator",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"N",
"Y"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "UniqueID",
"clean_name": "Unique ID",
"data_type": "text",
"category": "identifier",
"description": "Identifier column: Fully populated, all values unique, consistent format",
"population_percent": 100,
"unique_count": 2570,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"C10001-1",
"C10001-2",
"C10001-3",
"C10001-4",
"C10002-1"
],
"characteristics": [
"fully_populated",
"all_unique",
"high_cardinality",
"consistent_pattern"
]
},
{
"name": "Duplicate Participant",
"clean_name": "Duplicate Participant",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Y",
"N"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "# of Duplicates for each ID",
"clean_name": "# Of Duplicates For Each ID",
"data_type": "numeric",
"category": "identifier",
"description": "Identifier column: Fully populated, numeric values, consistent format",
"population_percent": 100,
"unique_count": 5,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"4",
"1",
"2",
"3",
"6"
],
"characteristics": [
"fully_populated",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Participant Status Category: Retiree",
"clean_name": "Participant Status Category: Retiree",
"data_type": "text",
"category": "category",
"description": "Category column: Fully populated, constant value, consistent format",
"population_percent": 100,
"unique_count": 1,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Retiree"
],
"characteristics": [
"fully_populated",
"constant_value",
"consistent_pattern"
]
},
{
"name": "Current Participant Status",
"clean_name": "Current Participant Status",
"data_type": "text",
"category": "category",
"description": "Category column: Fully populated",
"population_percent": 100,
"unique_count": 3,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Retired",
"Beneficiary",
"Disabled"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "Sex",
"clean_name": "Sex",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 3,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"M",
"F",
"U"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "Date of Birth",
"clean_name": "Date Of Birth",
"data_type": "date",
"category": "date",
"description": "Date column: Fully populated, date values, consistent format",
"population_percent": 100,
"unique_count": 483,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"11/15/1950",
"08/15/1933",
"01/15/1927",
"10/15/1931",
"09/15/1967"
],
"characteristics": [
"fully_populated",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "State",
"clean_name": "State",
"data_type": "text",
"category": "category",
"description": "Category column: Well populated, consistent format",
"population_percent": 0.9980544747081712,
"unique_count": 52,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"FL",
"CA",
"TX",
"WA",
"RI"
],
"characteristics": [
"consistent_pattern"
]
},
{
"name": "Zip Code + 4",
"clean_name": "Zip Code + 4",
"data_type": "mixed",
"category": "general",
"description": "General column: Well populated, consistent format",
"population_percent": 0.9980544747081712,
"unique_count": 1725,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"34202",
"90706",
"77056",
"77325",
"98723"
],
"characteristics": [
"partially_numeric",
"consistent_pattern"
]
},
{
"name": "Contingent Annuitant Flag",
"clean_name": "Contingent Annuitant Flag",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated, consistent format",
"population_percent": 100,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Y",
"N"
],
"characteristics": [
"fully_populated",
"consistent_pattern"
]
},
{
"name": "Number of Contingent Annuitants / Beneficiaries",
"clean_name": "Number Of Contingent Annuitants / Beneficiaries",
"data_type": "mixed",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.3894941634241245,
"unique_count": 4,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"1",
"2",
"3"
],
"characteristics": [
"sparse",
"partially_numeric",
"consistent_pattern"
]
},
{
"name": "1st Contingent Annuitant / Beneficiary Sex",
"clean_name": "1 St Contingent Annuitant / Beneficiary Sex",
"data_type": "empty",
"category": "general",
"description": "General column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "1st Contingent Annuitant / Beneficiary Date of Birth",
"clean_name": "1 St Contingent Annuitant / Beneficiary Date Of Birth",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, date values, consistent format",
"population_percent": 0.3894941634241245,
"unique_count": 338,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"04/15/1951",
"12/15/1947",
"01/15/1948",
"11/15/1958",
"11/15/1954"
],
"characteristics": [
"sparse",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "1st Contingent Annuitant / Beneficiary Date of Death",
"clean_name": "1 St Contingent Annuitant / Beneficiary Date Of Death",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, date values, consistent format",
"population_percent": 0.029182879377431907,
"unique_count": 48,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"04/15/2017",
"09/15/2021",
"05/15/2018",
"01/15/2019",
"04/15/2019"
],
"characteristics": [
"sparse",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "1st Contingent Annuitant / Beneficiary Deceased Flag",
"clean_name": "1 St Contingent Annuitant / Beneficiary Deceased Flag",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.029182879377431907,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Y"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "1st Contingent Annuitant / Beneficiary Relationship to Participant",
"clean_name": "1 St Contingent Annuitant / Beneficiary Relationship To Participant",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.35525291828793776,
"unique_count": 4,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"NS",
"SP"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "2nd Contingent Annuitant / Beneficiary Sex",
"clean_name": "2 Nd Contingent Annuitant / Beneficiary Sex",
"data_type": "empty",
"category": "general",
"description": "General column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "2nd Contingent Annuitant / Beneficiary Date of Birth",
"clean_name": "2 Nd Contingent Annuitant / Beneficiary Date Of Birth",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, high variety, date values, consistent format",
"population_percent": 0.0011673151750972762,
"unique_count": 4,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"06/15/2017",
"11/15/1982",
"10/15/1987"
],
"characteristics": [
"sparse",
"high_cardinality",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "2nd Contingent Annuitant / Beneficiary Date of Death",
"clean_name": "2 Nd Contingent Annuitant / Beneficiary Date Of Death",
"data_type": "empty",
"category": "date",
"description": "Date column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "2nd Contingent Annuitant / Beneficiary Deceased Flag",
"clean_name": "2 Nd Contingent Annuitant / Beneficiary Deceased Flag",
"data_type": "empty",
"category": "general",
"description": "General column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "2nd Contingent Annuitant / Beneficiary Relationship to Participant",
"clean_name": "2 Nd Contingent Annuitant / Beneficiary Relationship To Participant",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.0011673151750972762,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"NS"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "3rd Contingent Annuitant / Beneficiary Sex",
"clean_name": "3 Rd Contingent Annuitant / Beneficiary Sex",
"data_type": "empty",
"category": "general",
"description": "General column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "3rd Contingent Annuitant / Beneficiary Date of Birth",
"clean_name": "3 Rd Contingent Annuitant / Beneficiary Date Of Birth",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, high variety, date values, consistent format",
"population_percent": 0.0003891050583657588,
"unique_count": 2,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"04/15/1966"
],
"characteristics": [
"sparse",
"high_cardinality",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "3rd Contingent Annuitant / Beneficiary Date of Death",
"clean_name": "3 Rd Contingent Annuitant / Beneficiary Date Of Death",
"data_type": "empty",
"category": "date",
"description": "Date column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "3rd Contingent Annuitant / Beneficiary Deceased Flag",
"clean_name": "3 Rd Contingent Annuitant / Beneficiary Deceased Flag",
"data_type": "empty",
"category": "general",
"description": "General column: Sparse, constant value, consistent format",
"population_percent": 0.0,
"unique_count": 1,
"total_count": 2570,
"pattern": "",
"sample_values": [],
"characteristics": [
"all_empty",
"constant_value",
"consistent_pattern"
]
},
{
"name": "3rd Contingent Annuitant / Beneficiary Relationship to Participant",
"clean_name": "3 Rd Contingent Annuitant / Beneficiary Relationship To Participant",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, high variety, consistent format",
"population_percent": 0.0003891050583657588,
"unique_count": 2,
"total_count": 2570,
"pattern": "single_value",
"sample_values": [
"NS"
],
"characteristics": [
"sparse",
"high_cardinality",
"consistent_pattern"
]
},
{
"name": "Offered Lump Sum - Retirement",
"clean_name": "Offered Lump Sum - Retirement",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.15719844357976653,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Y"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "Offered Lump Sum - TV Window",
"clean_name": "Offered Lump Sum - Tv Window",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.0490272373540856,
"unique_count": 2,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Y"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "Salaried or Hourly Status",
"clean_name": "Salaried Or Hourly Status",
"data_type": "text",
"category": "category",
"description": "Category column",
"population_percent": 0.666147859922179,
"unique_count": 3,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"Salaried",
"Hourly"
],
"characteristics": [
"sparse"
]
},
{
"name": "Union or Non-Union",
"clean_name": "Union Or Non-union",
"data_type": "text",
"category": "general",
"description": "General column: Sparse, consistent format",
"population_percent": 0.3583657587548638,
"unique_count": 3,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"nonunion",
"union"
],
"characteristics": [
"sparse",
"consistent_pattern"
]
},
{
"name": "Benefit Commencement Date",
"clean_name": "Benefit Commencement Date",
"data_type": "date",
"category": "date",
"description": "Date column: Fully populated, date values, consistent format",
"population_percent": 100,
"unique_count": 388,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"12/01/2007",
"10/01/2015",
"06/01/2004",
"05/01/2017",
"12/01/1980"
],
"characteristics": [
"fully_populated",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "Current Monthly Benefit",
"clean_name": "Current Monthly Benefit",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, high variety, numeric values",
"population_percent": 100,
"unique_count": 2541,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"1842.05",
"125.26",
"28.57",
"3.57",
"652.64"
],
"characteristics": [
"fully_populated",
"high_cardinality",
"all_numeric"
]
},
{
"name": "Total Current Monthly Benefit",
"clean_name": "Total Current Monthly Benefit",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, numeric values",
"population_percent": 100,
"unique_count": 1836,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"1999.45",
"652.64",
"1680.27",
"1669.93",
"144.13"
],
"characteristics": [
"fully_populated",
"all_numeric"
]
},
{
"name": "SSLI or SS Supplement End Date",
"clean_name": "Ssli Or Ss Supplement End Date",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, date values, consistent format",
"population_percent": 0.04124513618677043,
"unique_count": 69,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"11/01/2024",
"12/01/2032",
"07/01/2028",
"05/01/2030",
"02/01/2033"
],
"characteristics": [
"sparse",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "Certain Period End Date",
"clean_name": "Certain Period End Date",
"data_type": "date",
"category": "date",
"description": "Date column: Sparse, high variety, date values, consistent format",
"population_percent": 0.0003891050583657588,
"unique_count": 2,
"total_count": 2570,
"pattern": "DD/MM/YYYY",
"sample_values": [
"11/01/2024"
],
"characteristics": [
"sparse",
"high_cardinality",
"date_pattern",
"consistent_pattern"
]
},
{
"name": "Ultimate Monthly Benefit ",
"clean_name": "Ultimate Monthly Benefit",
"data_type": "mixed",
"category": "general",
"description": "General column: Sparse, high variety",
"population_percent": 0.04124513618677043,
"unique_count": 107,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"1391.42",
"7800.08",
"12524.09",
"8038.45",
"10351.18"
],
"characteristics": [
"sparse",
"high_cardinality",
"partially_numeric"
]
},
{
"name": "Contingent Annuitant / Beneficiary 1 Monthly Benefit Payable Upon Participant Death",
"clean_name": "Contingent Annuitant / Beneficiary 1 Monthly Benefit Payable Upon Participant Death",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, numeric values",
"population_percent": 100,
"unique_count": 998,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"1155.44",
"78.57",
"0",
"778.64",
"35.77"
],
"characteristics": [
"fully_populated",
"all_numeric"
]
},
{
"name": "Contingent Annuitant / Beneficiary 2 Monthly Benefit Payable Upon Participant Death",
"clean_name": "Contingent Annuitant / Beneficiary 2 Monthly Benefit Payable Upon Participant Death",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, numeric values, consistent format",
"population_percent": 100,
"unique_count": 4,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"0",
"1000",
"470",
"632.061"
],
"characteristics": [
"fully_populated",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Contingent Annuitant / Beneficiary 3 Monthly Benefit Payable Upon Participant Death",
"clean_name": "Contingent Annuitant / Beneficiary 3 Monthly Benefit Payable Upon Participant Death",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, numeric values, consistent format",
"population_percent": 100,
"unique_count": 2,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"0",
"140.458"
],
"characteristics": [
"fully_populated",
"all_numeric",
"consistent_pattern"
]
},
{
"name": "Original Form of Annuity at Commencement",
"clean_name": "Original Form Of Annuity At Commencement",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated",
"population_percent": 100,
"unique_count": 5,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"JS",
"SLA",
"JS & SS",
"SLA & SS",
"CL"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "Form of Annuity to Be Purchased",
"clean_name": "Form Of Annuity To Be Purchased",
"data_type": "text",
"category": "general",
"description": "General column: Fully populated",
"population_percent": 100,
"unique_count": 5,
"total_count": 2570,
"pattern": "varied",
"sample_values": [
"JS",
"SLA",
"JS & SS",
"SLA & SS",
"CL"
],
"characteristics": [
"fully_populated"
]
},
{
"name": "Total Ultimate Monthly Benefit for Liftout Eligibility",
"clean_name": "Total Ultimate Monthly Benefit For Liftout Eligibility",
"data_type": "numeric",
"category": "general",
"description": "General column: Fully populated, numeric values",
"population_percent": 100,
"unique_count": 1841,
"total_count": 2570,
"pattern": "99999",
"sample_values": [
"1999.45",
"652.64",
"1680.27",
"1669.93",
"144.13"
],
"characteristics": [
"fully_populated",
"all_numeric"
]
}
] }
```
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
File: reference | Columns: 27 | Rows: 1999

| Name | Clean Name | Data Type | Category | Population Rate | Unique Count | Total Count | Pattern | Sample Values | Characteristics |
|------|------------|-----------|----------|-----------------|--------------|-------------|---------|---------------|-----------------|
| Record ID | Record ID | text | identifier | 1 | 1999 | 1999 | varied | 1B_C10001-1, 1B_C10001-2, 1B_C10001-3, 1B_C10001-4, 1B_C10002-1 | fully_populated, all_unique, high_cardinality, consistent_pattern |
| Unique Life ID | Unique Life ID | text | identifier | 1 | 1443 | 1999 | AAA999 | C10001, C10002, C10003, C10004, C10005 | fully_populated, consistent_pattern |
| Status | Status | text | category | 1 | 2 | 1999 | varied | Pensioner, Beneficiary | fully_populated |
| State | State | text | category | 0.997498749374687 | 52 | 1999 | varied | FL, CA, TX, WA, RI | consistent_pattern |
| Zipcode | Zipcode | mixed | general | 0.997498749374687 | 1329 | 1999 | varied | 34202, 90706, 77056, 77325, 98723 | partially_numeric, consistent_pattern |
| Pricing Group | Pricing Group | numeric | general | 1 | 1 | 1999 | 99999 | 0 | fully_populated, constant_value, all_numeric, consistent_pattern |
| Primary Gender | Primary Gender | text | general | 1 | 2 | 1999 | varied | Male, Female | fully_populated |
| Primary Date of Birth | Primary Date Of Birth | date | date | 1 | 453 | 1999 | YYYY-MM-DD | 1950-11-15 00:00:00, 1933-08-15 00:00:00, 1927-01-15 00:00:00, 1931-10-15 00:00:00, 1967-09-15 00:00:00 | fully_populated, date_pattern, consistent_pattern |
| Primary Base Mortality Flag | Primary Base Mortality Flag | text | general | 1 | 34 | 1999 | varied | 1W[1500- 2250)PM, 1B[0- 750)BF, 1W[1500- 2250)BF, 1W[750- 1500)PF, 1M[0- 750)PM | fully_populated |
| Primary Mortality Scalar Flag | Primary Mortality Scalar Flag | text | general | 1 | 2 | 1999 | varied | 1_NonDisabled, 2_Disabled | fully_populated, consistent_pattern |
| Primary Mortality Improvement Flag | Primary Mortality Improvement Flag | text | general | 1 | 8 | 1999 | varied | 1WM, 1BF, 1WF, 1MM, 1MF | fully_populated, consistent_pattern |
| Secondary Gender | Secondary Gender | text | general | 0.347173586793397 | 3 | 1999 | varied | Female, Male | sparse |
| Secondary Date of Birth | Secondary Date Of Birth | date | date | 0.347173586793397 | 293 | 1999 | YYYY-MM-DD | 1951-04-15 00:00:00, 1947-12-15 00:00:00, 1948-01-15 00:00:00, 1958-11-15 00:00:00, 1954-11-15 00:00:00 | sparse, date_pattern, consistent_pattern |
| Secondary Base Mortality Flag | Secondary Base Mortality Flag | text | general | 0.347173586793397 | 18 | 1999 | varied | 1W[1500- 2250)SF, 1W[750- 1500)SM, 1M[0- 750)SF, 1W[750- 1500)SF, 1M[0- 750)SM | sparse |
| Secondary Mortality Scalar Flag | Secondary Mortality Scalar Flag | text | general | 0.347173586793397 | 2 | 1999 | varied | 1_NonDisabled | sparse, consistent_pattern |
| Secondary Mortality Improvement Flag | Secondary Mortality Improvement Flag | text | general | 0.347173586793397 | 9 | 1999 | varied | 1WF, 1WM, 1MF, 1MM, 2WF | sparse, consistent_pattern |
| Form of Annuity | Form Of Annuity | text | general | 1 | 4 | 1999 | varied | JS, SLA, JS & SS, SLA & SS | fully_populated |
| Escalation Group Name | Escalation Group Name | empty | name | 0 | 1 | 1999 |  |  | all_empty, constant_value, consistent_pattern |
| Start Date | Start Date | date | date | 1 | 1 | 1999 | YYYY-MM-DD | 2024-05-15 00:00:00 | fully_populated, constant_value, date_pattern, consistent_pattern |
| End Date | End Date | date | date | 1 | 54 | 1999 | YYYY-MM-DD | 9999-09-09 00:00:00, 2024-11-01 00:00:00, 2032-12-01 00:00:00, 2028-07-01 00:00:00, 2030-05-01 00:00:00 | fully_populated, date_pattern, consistent_pattern |
| Guaranteed Months | Guaranteed Months | numeric | general | 1 | 1 | 1999 | 99999 | 0 | fully_populated, constant_value, all_numeric, consistent_pattern |
| Primary Amount | Primary Amount | numeric | amount | 1 | 1981 | 1999 | 99999 | 1842.05, 125.26, 28.57, 3.57, 652.64 | fully_populated, high_cardinality, all_numeric |
| Secondary Amount | Secondary Amount | numeric | amount | 1 | 692 | 1999 | 99999 | 1155.44, 78.57, 0, 778.64, 35.77 | fully_populated, all_numeric |
| Pop-up Amount | Pop-up Amount | numeric | amount | 1 | 1 | 1999 | 99999 | 0 | fully_populated, constant_value, all_numeric, consistent_pattern |
| Cash Refund As of Date | Cash Refund As Of Date | numeric | date | 1 | 1 | 1999 | 99999 | 0 | fully_populated, constant_value, all_numeric, consistent_pattern |
| Cash Refund Amount | Cash Refund Amount | numeric | amount | 1 | 1 | 1999 | 99999 | 0 | fully_populated, constant_value, all_numeric, consistent_pattern |
| Death Benefit | Death Benefit | numeric | general | 1 | 1 | 1999 | 99999 | 0 | fully_populated, constant_value, all_numeric, consistent_pattern |

## INPUT COLUMN METADATA:
File: input | Columns: 43 | Rows: 2570

| Name | Clean Name | Data Type | Category | Population Rate | Unique Count | Total Count | Pattern | Sample Values | Characteristics |
|------|------------|-----------|----------|-----------------|--------------|-------------|---------|---------------|-----------------|
| Special Inflation Benefit Indicator | Special Inflation Benefit Indicator | text | general | 1 | 2 | 2570 | varied | N, Y | fully_populated, consistent_pattern |
| UniqueID | Unique ID | text | identifier | 1 | 2570 | 2570 | varied | C10001-1, C10001-2, C10001-3, C10001-4, C10002-1 | fully_populated, all_unique, high_cardinality, consistent_pattern |
| Duplicate Participant | Duplicate Participant | text | general | 1 | 2 | 2570 | varied | Y, N | fully_populated, consistent_pattern |
| # of Duplicates for each ID | # Of Duplicates For Each ID | numeric | identifier | 1 | 5 | 2570 | 99999 | 4, 1, 2, 3, 6 | fully_populated, all_numeric, consistent_pattern |
| Participant Status Category: Retiree | Participant Status Category: Retiree | text | category | 1 | 1 | 2570 | varied | Retiree | fully_populated, constant_value, consistent_pattern |
| Current Participant Status | Current Participant Status | text | category | 1 | 3 | 2570 | varied | Retired, Beneficiary, Disabled | fully_populated |
| Sex | Sex | text | general | 1 | 3 | 2570 | varied | M, F, U | fully_populated, consistent_pattern |
| Date of Birth | Date Of Birth | date | date | 1 | 483 | 2570 | DD/MM/YYYY | 11/15/1950, 08/15/1933, 01/15/1927, 10/15/1931, 09/15/1967 | fully_populated, date_pattern, consistent_pattern |
| State | State | text | category | 0.998054474708171 | 52 | 2570 | varied | FL, CA, TX, WA, RI | consistent_pattern |
| Zip Code + 4 | Zip Code + 4 | mixed | general | 0.998054474708171 | 1725 | 2570 | varied | 34202, 90706, 77056, 77325, 98723 | partially_numeric, consistent_pattern |
| Contingent Annuitant Flag | Contingent Annuitant Flag | text | general | 1 | 2 | 2570 | varied | Y, N | fully_populated, consistent_pattern |
| Number of Contingent Annuitants / Beneficiaries | Number Of Contingent Annuitants / Beneficiaries | mixed | general | 0.389494163424125 | 4 | 2570 | varied | 1, 2, 3 | sparse, partially_numeric, consistent_pattern |
| 1st Contingent Annuitant / Beneficiary Sex | 1 St Contingent Annuitant / Beneficiary Sex | empty | general | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 1st Contingent Annuitant / Beneficiary Date of Birth | 1 St Contingent Annuitant / Beneficiary Date Of Birth | date | date | 0.389494163424125 | 338 | 2570 | DD/MM/YYYY | 04/15/1951, 12/15/1947, 01/15/1948, 11/15/1958, 11/15/1954 | sparse, date_pattern, consistent_pattern |
| 1st Contingent Annuitant / Beneficiary Date of Death | 1 St Contingent Annuitant / Beneficiary Date Of Death | date | date | 0.0291828793774319 | 48 | 2570 | DD/MM/YYYY | 04/15/2017, 09/15/2021, 05/15/2018, 01/15/2019, 04/15/2019 | sparse, date_pattern, consistent_pattern |
| 1st Contingent Annuitant / Beneficiary Deceased Flag | 1 St Contingent Annuitant / Beneficiary Deceased Flag | text | general | 0.0291828793774319 | 2 | 2570 | varied | Y | sparse, consistent_pattern |
| 1st Contingent Annuitant / Beneficiary Relationship to Participant | 1 St Contingent Annuitant / Beneficiary Relationship To Participant | text | general | 0.355252918287938 | 4 | 2570 | varied | NS, SP | sparse, consistent_pattern |
| 2nd Contingent Annuitant / Beneficiary Sex | 2 Nd Contingent Annuitant / Beneficiary Sex | empty | general | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 2nd Contingent Annuitant / Beneficiary Date of Birth | 2 Nd Contingent Annuitant / Beneficiary Date Of Birth | date | date | 0.00116731517509728 | 4 | 2570 | DD/MM/YYYY | 06/15/2017, 11/15/1982, 10/15/1987 | sparse, high_cardinality, date_pattern, consistent_pattern |
| 2nd Contingent Annuitant / Beneficiary Date of Death | 2 Nd Contingent Annuitant / Beneficiary Date Of Death | empty | date | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 2nd Contingent Annuitant / Beneficiary Deceased Flag | 2 Nd Contingent Annuitant / Beneficiary Deceased Flag | empty | general | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 2nd Contingent Annuitant / Beneficiary Relationship to Participant | 2 Nd Contingent Annuitant / Beneficiary Relationship To Participant | text | general | 0.00116731517509728 | 2 | 2570 | varied | NS | sparse, consistent_pattern |
| 3rd Contingent Annuitant / Beneficiary Sex | 3 Rd Contingent Annuitant / Beneficiary Sex | empty | general | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 3rd Contingent Annuitant / Beneficiary Date of Birth | 3 Rd Contingent Annuitant / Beneficiary Date Of Birth | date | date | 0.000389105058365759 | 2 | 2570 | DD/MM/YYYY | 04/15/1966 | sparse, high_cardinality, date_pattern, consistent_pattern |
| 3rd Contingent Annuitant / Beneficiary Date of Death | 3 Rd Contingent Annuitant / Beneficiary Date Of Death | empty | date | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 3rd Contingent Annuitant / Beneficiary Deceased Flag | 3 Rd Contingent Annuitant / Beneficiary Deceased Flag | empty | general | 0 | 1 | 2570 |  |  | all_empty, constant_value, consistent_pattern |
| 3rd Contingent Annuitant / Beneficiary Relationship to Participant | 3 Rd Contingent Annuitant / Beneficiary Relationship To Participant | text | general | 0.000389105058365759 | 2 | 2570 | single_value | NS | sparse, high_cardinality, consistent_pattern |
| Offered Lump Sum - Retirement | Offered Lump Sum - Retirement | text | general | 0.157198443579767 | 2 | 2570 | varied | Y | sparse, consistent_pattern |
| Offered Lump Sum - TV Window | Offered Lump Sum - Tv Window | text | general | 0.0490272373540856 | 2 | 2570 | varied | Y | sparse, consistent_pattern |
| Salaried or Hourly Status | Salaried Or Hourly Status | text | category | 0.666147859922179 | 3 | 2570 | varied | Salaried, Hourly | sparse |
| Union or Non-Union | Union Or Non-union | text | general | 0.358365758754864 | 3 | 2570 | varied | nonunion, union | sparse, consistent_pattern |
| Benefit Commencement Date | Benefit Commencement Date | date | date | 1 | 388 | 2570 | DD/MM/YYYY | 12/01/2007, 10/01/2015, 06/01/2004, 05/01/2017, 12/01/1980 | fully_populated, date_pattern, consistent_pattern |
| Current Monthly Benefit | Current Monthly Benefit | numeric | general | 1 | 2541 | 2570 | 99999 | 1842.05, 125.26, 28.57, 3.57, 652.64 | fully_populated, high_cardinality, all_numeric |
| Total Current Monthly Benefit | Total Current Monthly Benefit | numeric | general | 1 | 1836 | 2570 | 99999 | 1999.45, 652.64, 1680.27, 1669.93, 144.13 | fully_populated, all_numeric |
| SSLI or SS Supplement End Date | Ssli Or Ss Supplement End Date | date | date | 0.0412451361867704 | 69 | 2570 | DD/MM/YYYY | 11/01/2024, 12/01/2032, 07/01/2028, 05/01/2030, 02/01/2033 | sparse, date_pattern, consistent_pattern |
| Certain Period End Date | Certain Period End Date | date | date | 0.000389105058365759 | 2 | 2570 | DD/MM/YYYY | 11/01/2024 | sparse, high_cardinality, date_pattern, consistent_pattern |
| Ultimate Monthly Benefit  | Ultimate Monthly Benefit | mixed | general | 0.0412451361867704 | 107 | 2570 | varied | 1391.42, 7800.08, 12524.09, 8038.45, 10351.18 | sparse, high_cardinality, partially_numeric |
| Contingent Annuitant / Beneficiary 1 Monthly Benefit Payable Upon Participant Death | Contingent Annuitant / Beneficiary 1 Monthly Benefit Payable Upon Participant Death | numeric | general | 1 | 998 | 2570 | 99999 | 1155.44, 78.57, 0, 778.64, 35.77 | fully_populated, all_numeric |
| Contingent Annuitant / Beneficiary 2 Monthly Benefit Payable Upon Participant Death | Contingent Annuitant / Beneficiary 2 Monthly Benefit Payable Upon Participant Death | numeric | general | 1 | 4 | 2570 | 99999 | 0, 1000, 470, 632.061 | fully_populated, all_numeric, consistent_pattern |
| Contingent Annuitant / Beneficiary 3 Monthly Benefit Payable Upon Participant Death | Contingent Annuitant / Beneficiary 3 Monthly Benefit Payable Upon Participant Death | numeric | general | 1 | 2 | 2570 | 99999 | 0, 140.458 | fully_populated, all_numeric, consistent_pattern |
| Original Form of Annuity at Commencement | Original Form Of Annuity At Commencement | text | general | 1 | 5 | 2570 | varied | JS, SLA, JS & SS, SLA & SS, CL | fully_populated |
| Form of Annuity to Be Purchased | Form Of Annuity To Be Purchased | text | general | 1 | 5 | 2570 | varied | JS, SLA, JS & SS, SLA & SS, CL | fully_populated |
| Total Ultimate Monthly Benefit for Liftout Eligibility | Total Ultimate Monthly Benefit For Liftout Eligibility | numeric | general | 1 | 1841 | 2570 | 99999 | 1999.45, 652.64, 1680.27, 1669.93, 144.13 | fully_populated, all_numeric |


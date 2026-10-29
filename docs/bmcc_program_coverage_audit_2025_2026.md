# BMCC academic-program coverage audit (2025–2026)

**Audit date:** 2026-10-29  
**Scope:** every associate-degree program in BMCC's current Academic Programs directory, plus certificates and the microcredential listed there, compared with `docs/programs.csv` and BMCC `docs/*_courses.csv` files. Application code and curriculum CSVs were not changed.

## Authoritative sources and method

This audit uses only first-party BMCC sources:

- [BMCC Academic Programs directory](https://www.bmcc.cuny.edu/academics/programs/) — authoritative for the current public program inventory and degree types.
- [BMCC Academic Degree Maps landing page](https://www.bmcc.cuny.edu/academics/advisement/advisement-resources/academic-program-maps/) — explains that maps are suggested course sequences for advising and links catalog-year editions.
- [Official 2025–2026 consolidated Academic Degree Maps PDF](https://www.dropbox.com/scl/fi/w1lycuqzbnnwihjdicd7r/2025-2026degreemapsrev110625.pdf?raw=1&rlkey=ovleo82ap162u43bq8u3x9zyy&st=jqa2q9gt) — 160 pages, filename revision `rev110625`; every page is headed 2025–2026.

The live directory was treated as the authority for *which programs currently exist*. The year-bound PDF was treated as the authority for 2025–2026 map coverage and map titles. A curriculum CSV counts as present only when a BMCC `*_courses.csv` file identifies the corresponding program in its first data row. `pathways_courses.csv` is shared reference data, not a program curriculum.

## Executive result

| Measure | Result |
|---|---:|
| Current directory associate programs | **61** (8 A.A.S., 25 A.A., 28 A.S.) |
| BMCC associate rows in `programs.csv` | **63** (8 A.A.S., 27 A.A., 28 A.S.) |
| Why the row count is two higher | Psychology and Writing and Literature are each split into two concentration rows |
| Directory associate programs represented in `programs.csv` | **61/61 (100%)** |
| Directory associate programs with at least one curriculum CSV | **35/61 (57.4%)** |
| Repository associate rows with curriculum CSVs | **37/63 (58.7%)** |
| Directory associate programs with a curriculum CSV explicitly labeled 2025–2026 | **31/61 (50.8%)** |
| Certificates represented in `programs.csv` | **5/5** |
| Certificates with curriculum CSVs | **1/5** (Cybersecurity) |
| Microcredentials represented / with curriculum CSV | **1/1 / 0/1** |

The inventory problem is therefore not missing top-level `programs.csv` rows. It is missing curriculum coverage: **26 of 61 official degree programs**, **4 of 5 certificates**, and the **1 microcredential** have no per-program course CSV. Four additional degree curricula exist but are labeled for another catalog year: Data Science (2024–2025) and Biotechnology Science, Engineering Science, and Science for Forensics (2026–2027).

## Complete associate-degree inventory

Legend: **Current** means the repository row and curriculum CSV both say 2025–2026. **No curriculum** means the program is in `programs.csv` but lacks a per-program course CSV. **Year conflict** means a CSV exists but is labeled for a different year. The map column records important 2025–2026 PDF naming or structure; otherwise the program has an eponymous map.

### Associate in Applied Science (A.A.S.) — 8 programs

| Official program (BMCC source) | Repository record | Curriculum coverage | 2025–2026 map note |
|---|---|---|---|
| [Accounting](https://www.bmcc.cuny.edu/academics/departments/accounting/accounting/) | `ACCT_AAS`, 2025–2026 | `acct_aas_courses.csv` — **Current** | Accounting (ACC) |
| [Business Management](https://www.bmcc.cuny.edu/academics/departments/business-management/business-management/) | `BUSM_AAS`, 2026 | **No curriculum** | Five separate specializations; see ambiguity section |
| [Computer Information Systems](https://www.bmcc.cuny.edu/academics/departments/cis/computer-information-systems-cis/) | `CIS`, 2025–2026 | `cis_courses.csv` — **Current** | Computer Information Systems (CIS) |
| [Computer Network Technology](https://www.bmcc.cuny.edu/academics/departments/cis/computer-network-technology/) | `CNT`, 2025–2026 | `cnt_courses.csv` — **Current** | Computer Network Technology (CNT) |
| [Health Information Technology](https://www.bmcc.cuny.edu/academics/departments/allied-health/about-hit/health-information-technology-program-requirements/) | `HIT_AAS`, 2026 | **No curriculum** | Health Information Technology (HIT) |
| [Nursing](https://www.bmcc.cuny.edu/academics/departments/nursing/nursing-program/) | `NUR_AAS`, 2025–2026 | `nur_aas_courses.csv` — **Current** | Maps are titled **Undeclared Health (UDH) to Nursing (NUR)** and are three-year start variants, not a plain two-/five-semester Nursing map |
| [Paramedic](https://www.bmcc.cuny.edu/academics/departments/allied-health/paramedic/) | `PAR_AAS`, 2026 | **No curriculum** | Paramedic (EMC) |
| [Respiratory Therapy](https://www.bmcc.cuny.edu/academics/departments/allied-health/respiratory-therapy/) | `RTH_AAS`, 2026 | **No curriculum** | Respiratory Therapy (RTT) |

### Associate in Arts (A.A.) — 25 official programs / 27 repository rows

| Official program (BMCC source) | Repository record | Curriculum coverage | 2025–2026 map note |
|---|---|---|---|
| [Art Foundations: Art History](https://www.bmcc.cuny.edu/academics/departments/music-and-art/art-foundations-art-history/) | `AFH_AA`, 2026 | **No curriculum** | Art Foundations: Art History (AFH) |
| [Bilingual Childhood Education](https://www.bmcc.cuny.edu/academics/departments/teacher-education/bilingual-childhood-education-edb/) | `BCE_AA`, 2026 | **No curriculum** | General (`EDB-GEN`) and Special Education (`EDB-SPC`) maps |
| [Childhood Education](https://www.bmcc.cuny.edu/academics/departments/teacher-education/childhood-education-edu/) | `CHED_AA`, 2026 | **No curriculum** | General (`EDU-GEN`) and Special Education (`EDU-SPC`) maps |
| [Children and Youth Studies](https://www.bmcc.cuny.edu/academics/departments/english/children-and-youth-studies/) | `CYS_AA`, 2026 | **No curriculum** | Children and Youth Studies (CYS) |
| [Communication Studies](https://www.bmcc.cuny.edu/academics/departments/speech/communication-studies/) | `COM_AA`, 2025–2026 | `com_aa_courses.csv` — **Current** | Communication Studies (COM) |
| [Criminal Justice](https://www.bmcc.cuny.edu/academics/departments/criminal-justice/criminal-justice/) | `CRJ_AA`, 2025–2026 | `crj_aa_courses.csv` — **Current** | Criminal Justice (CRJ) |
| [Critical Thinking and Justice](https://www.bmcc.cuny.edu/academics/departments/academic-literacy/critical-thinking-and-justice/) | `CTJ_AA`, 2026 | **No curriculum** | Critical Thinking and Justice (CTJ) |
| [Economics](https://www.bmcc.cuny.edu/academics/departments/social-sciences/economics/) | `ECO_AA`, 2025–2026 | `eco_aa_courses.csv` — **Current** | Economics (ECO) |
| [Ethnic Studies](https://www.bmcc.cuny.edu/academics/departments/ethnic-studies/ethnic-studies/) | `ETH_AA`, 2026 | **No curriculum** | One map with five map-level areas of study |
| [Gender and Women’s Studies](https://www.bmcc.cuny.edu/academics/programs/gender-and-womens-studies/) | `GWS_AA`, 2025–2026 | `gws_aa_courses.csv` — **Current** | Gender and Women’s Studies (GWS) |
| [History](https://www.bmcc.cuny.edu/academics/departments/social-sciences/history/) | `HIS_AA`, 2025–2026 | `his_aa_courses.csv` — **Current** | History (HIS) |
| [Liberal Arts](https://www.bmcc.cuny.edu/academics/programs/liberal-arts/) | `LA_AA`, 2026 | **No curriculum** | Liberal Arts (LIB) |
| [Linguistics](https://www.bmcc.cuny.edu/academics/departments/academic-literacy/linguistics-and-literacy/) | `LIN_AA`, 2026 | **No curriculum** | General (`GEN-LIN`) and TESOL/Applied Linguistics (`TES-LIN`) maps |
| [Literacy Studies](https://www.bmcc.cuny.edu/academics/departments/academic-literacy/literacy-studies/) | `LITST_AA`, 2026 | **No curriculum** | Literacy Studies (LTS) |
| [Modern Languages: French](https://www.bmcc.cuny.edu/academics/departments/modern-languages/french/) | `FRN_AA`, 2025–2026 | `frn_aa_courses.csv` — **Current** | Modern Languages specialization in French (`MLA-FRN`) |
| [Modern Languages: Italian](https://www.bmcc.cuny.edu/academics/departments/modern-languages/italian/) | `ITA_AA`, 2025–2026 | `ita_aa_courses.csv` — **Current** | Modern Languages specialization in Italian (`MLA-ITL`) |
| [Modern Languages: Spanish](https://www.bmcc.cuny.edu/academics/departments/modern-languages/spanish/) | `SPA_AA`, 2025–2026 | `spa_aa_courses.csv` — **Current** | Modern Languages specialization in Spanish (`MLA-SPN`) |
| [Modern Languages: Spanish Translation and Interpretation](https://www.bmcc.cuny.edu/academics/departments/modern-languages/modern-languages-spanish-translation-and-interpretation/) | `STI_AA`, 2025–2026 | `sti_aa_courses.csv` — **Current** | Map says specialization (`MLA-TRS`) |
| [Philosophy](https://www.bmcc.cuny.edu/academics/departments/social-sciences/philosophy/) | `PHI_AA`, 2025–2026 | `phi_aa_courses.csv` — **Current** | Philosophy (PHI) |
| [Political Science](https://www.bmcc.cuny.edu/academics/departments/social-sciences/political-science/) | `POL_AA`, 2025–2026 | `pol_aa_courses.csv` — **Current** | Political Science (POL) |
| [Psychology](https://www.bmcc.cuny.edu/academics/departments/social-sciences/psychology/) | `PSY_AA` and `PSY_STEM_AA`, both 2025–2026 | `psy_aa_courses.csv` and `psy_stem_aa_courses.csv` — **Current** | General (`PSY-GEN`) and STEM (`PSY-STM`) maps; repository treats concentrations as separate programs |
| [Secondary Education for Social Studies](https://www.bmcc.cuny.edu/academics/departments/teacher-education/secondary-education-for-social-studies/) | `SESS_AA`, 2026 | **No curriculum** | Secondary Education for Social Studies (SES) |
| [Sociology](https://www.bmcc.cuny.edu/academics/departments/social-sciences/sociology/) | `SOC_AA`, 2025–2026 | `soc_aa_courses.csv` — **Current** | Sociology (SOC) |
| [Urban Studies](https://www.bmcc.cuny.edu/academics/departments/social-sciences/urban-studies/) | `URB_AA`, 2025–2026 | `urb_aa_courses.csv` — **Current** | Urban Studies (URB) |
| [Writing and Literature](https://www.bmcc.cuny.edu/academics/departments/english/requirements/) | `WAL_AA` and `WAL_JRN_AA`, both 2025–2026 | `wal_aa_courses.csv` and `wal_jrn_aa_courses.csv` — **Current** | General (`ENG-GEN`) and Journalism (`ENG-JRN`) maps; repository treats concentrations as separate programs |

### Associate in Science (A.S.) — 28 programs

| Official program (BMCC source) | Repository record | Curriculum coverage | 2025–2026 map note |
|---|---|---|---|
| [Accounting for Forensic Accounting](https://www.bmcc.cuny.edu/academics/departments/accounting/accounting-for-forensic-accounting/) | `FAA_AS`, 2026 | **No curriculum** | Separate Statistics and Precalculus pathways (FAC) |
| [Animation and Motion Graphics](https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/animation-and-motion-graphics/) | `AMG_AS`, 2025–2026 | `amg_as_courses.csv` — **Current** | Animation and Motion Graphics (ANI) |
| [Art Foundations: Studio Art](https://www.bmcc.cuny.edu/academics/departments/music-and-art/art-foundations-studio-art/) | `AFS_AS`, 2026 | **No curriculum** | Art Foundations: Studio Art (AFS) |
| [Biotechnology Science](https://www.bmcc.cuny.edu/academics/departments/science/biotechnology-science/) | `BTE_AS`, 2026–2027 | `bte_as_courses.csv`, 2026–2027 — **Year conflict** | 2025–2026 map title is **Biotechnology (BTE)** |
| [Business Administration](https://www.bmcc.cuny.edu/academics/departments/business-management/business-administration/) | `BBA_AS`, 2025–2026 | `bba_as_courses.csv` — **Current** | Business Administration (BAN) |
| [Child Care/Early Childhood Education](https://www.bmcc.cuny.edu/academics/departments/teacher-education/child-care-early-childhood-education/) | `ECE_AS`, 2026 | **No curriculum** | PDF says **Early Childhood Education**, with Infant/Toddler (`ECE-ECI`) and Pre-School (`ECE-ECP`) specializations |
| [Community Health Education](https://www.bmcc.cuny.edu/academics/departments/health-studies/community-health-education/) | `CHE_AS`, 2026 | **No curriculum** | Community Health Education (COH) |
| [Computer Science](https://www.bmcc.cuny.edu/academics/departments/cis/computer-science/) | `CS`, 2025–2026 | `cs_courses.csv` — **Current** | Computer Science (CSC) |
| [Data Science](https://www.bmcc.cuny.edu/academics/departments/math/data-science/) | `DS_AS`, 2024–2025 | `ds_as_courses.csv`, 2024–2025 — **Year conflict** | 2025–2026 map exists (DSM) |
| [Digital Marketing](https://www.bmcc.cuny.edu/academics/departments/business-management/digital-marketing/) | `DMK_AS`, 2025–2026 | `dmk_as_courses.csv` — **Current** | Digital Marketing (DMA) |
| [Engineering Science](https://www.bmcc.cuny.edu/academics/departments/science/engineering-science/) | `ESC_AS`, 2026–2027 | `esc_as_courses.csv`, 2026–2027 — **Year conflict** | 2025–2026 map exists (ESC) |
| [Entrepreneurship and Innovation](https://www.bmcc.cuny.edu/academics/departments/business-management/sbe/) | `ENT_AS`, 2026 | **No curriculum** | 2025–2026 PDF still says **Small Business Entrepreneurship (SBE)**; directory says “formerly Small Business/Entrepreneurship” |
| [Financial Management](https://www.bmcc.cuny.edu/academics/departments/business-management/financial-management/) | `FMG_AS`, 2025–2026 | `fmg_as_courses.csv` — **Current** | Financial Management (FIN) |
| [Geographic Information Science (GIS)](https://www.bmcc.cuny.edu/academics/departments/cis/geographic-information-science-gis/) | `GIS_AS`, 2026 | **No curriculum** | Geographic Information Science (GIS) |
| [Gerontology](https://www.bmcc.cuny.edu/academics/programs/gerontology/) | `GER_AS`, 2025–2026 | `ger_as_courses.csv` — **Current** | Gerontology (GER) |
| [Human Services](https://www.bmcc.cuny.edu/academics/departments/social-sciences/human-services/) | `HMS_AS`, 2025–2026 | `hms_as_courses.csv` — **Current** | Human Services (HUM) |
| [Mathematics](https://www.bmcc.cuny.edu/academics/departments/math/mathematics-program/) | `MAT_AS`, 2025–2026 | `mat_as_courses.csv` — **Current** | Mathematics (MAT) |
| [Mathematics and Sciences for Secondary Education](https://www.bmcc.cuny.edu/academics/departments/teacher-education/secondary-education-program/) | `MSSE_AS`, 2026 | **No curriculum** | Biology, Chemistry, Mathematics, and Physics specialization maps (`SED-*`) |
| [Multimedia Programming and Design](https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/multimedia-programming-and-design/) | `MMP_AS`, 2025–2026 | `mmp_as_courses.csv` — **Current** | Multimedia Programming and Design (MMD) |
| [Music](https://www.bmcc.cuny.edu/academics/departments/music-and-art/music/) | `MUS_AS`, 2026 | **No curriculum** | Jazz and Popular Music, Music Education, Music Performance, and Music Studies maps |
| [Public and Nonprofit Administration](https://www.bmcc.cuny.edu/academics/departments/business-management/public-and-nonprofit-administration/) | `PNA_AS`, 2025–2026 | `pna_as_courses.csv` — **Current** | PDF alternates “Public & Non-Profit” and “Public & Nonprofit” (PAN) |
| [Public Health](https://www.bmcc.cuny.edu/academics/departments/health-studies/public-health/) | `PH_AS`, 2026 | **No curriculum** | Public Health (PHE) |
| [School Health Education](https://www.bmcc.cuny.edu/academics/programs/school-health-education-she/) | `SHE_AS`, 2026 | **No curriculum** | School Health Education (SHE) |
| [Science](https://www.bmcc.cuny.edu/academics/departments/science/science/) | `SCI_AS`, 2025–2026 | `sci_as_courses.csv` — **Current** | Science (SCI) |
| [Science for Forensics](https://www.bmcc.cuny.edu/academics/departments/science/science-for-forensics/) | `FSC_AS`, 2026–2027 | `fsc_as_courses.csv`, 2026–2027 — **Year conflict** | 2025–2026 map exists (FSC) |
| [Science for Health](https://www.bmcc.cuny.edu/academics/departments/science/science-for-health-professions/) | `SHP_AS`, 2025–2026 | `shp_as_courses.csv` — **Current** | Science for Health (SHP) |
| [Theatre](https://www.bmcc.cuny.edu/academics/departments/speech/theatre/) | `THR_AS`, 2026 | **No curriculum** | Theatre (THE) |
| [Video Arts and Technology](https://www.bmcc.cuny.edu/academics/departments/media-arts-and-technology/video-arts-and-technology/) | `VAT_AS`, 2026 | **No curriculum** | Video Arts and Technology (VAT) |

## Certificates and microcredential (separate inventory)

| Credential (BMCC source) | Type | Repository record | Curriculum coverage | 2025–2026 map coverage |
|---|---|---|---|---|
| [Accounting Certificate](https://www.bmcc.cuny.edu/academics/departments/accounting/accounting-certificate-program-acp/) | Certificate | `ACC_CERT`, 2026 | **No curriculum** | **No map found** in the 160-page PDF |
| [Cybersecurity Certificate](https://www.bmcc.cuny.edu/academics/departments/cis/cybersecurity-certificate/) | Certificate | `CYB_CERT`, 2025–2026 | `cyb_cert_courses.csv` — **Current** | Cybersecurity Certificate Program (`CYB-CERT`) |
| [Health Informatics Certificate](https://www.bmcc.cuny.edu/academics/departments/allied-health/health-informatics-certificate/) | Certificate | `HI_CERT`, 2026 | **No curriculum** | **No map found** |
| [Practical Nursing Certificate](https://www.bmcc.cuny.edu/academics/departments/nursing/practical-nursing-certificate-program/) | Certificate | `PN_CERT`, 2026 | **No curriculum** | PDF says **Licensed Practical Nursing Certificate Program (LPN)** |
| [Spanish Translation for the Health, Legal and Business Professions Certificate](https://www.bmcc.cuny.edu/academics/departments/modern-languages/spanish-translation-certificate/) | Certificate | `STH_CERT`, 2026 | **No curriculum** | **No map found** |
| [Cybersecurity](https://www.bmcc.cuny.edu/cyber-security-micro-credential/) | Microcredential | `CYB_MICRO`, 2026 | **No curriculum** | **No map found** |

## Missing curriculum CSVs: actionable list

The following **26 official associate programs** have no corresponding course CSV:

- A.A.S. (4): Business Management; Health Information Technology; Paramedic; Respiratory Therapy.
- A.A. (10): Art Foundations: Art History; Bilingual Childhood Education; Childhood Education; Children and Youth Studies; Critical Thinking and Justice; Ethnic Studies; Liberal Arts; Linguistics; Literacy Studies; Secondary Education for Social Studies.
- A.S. (12): Accounting for Forensic Accounting; Art Foundations: Studio Art; Child Care/Early Childhood Education; Community Health Education; Entrepreneurship and Innovation; Geographic Information Science; Mathematics and Sciences for Secondary Education; Music; Public Health; School Health Education; Theatre; Video Arts and Technology.

The following non-degree credentials also lack course CSVs: Accounting Certificate, Health Informatics Certificate, Practical Nursing Certificate, Spanish Translation for the Health, Legal and Business Professions Certificate, and Cybersecurity microcredential.

## Catalog-year and naming conflicts

1. **Mixed semantics in `catalog_year`.** Twenty-six degree rows use the bare value `2026` (30 BMCC credential rows when four certificates are included), while most implemented rows use `2025-2026`; three degrees use `2026-2027`, and Data Science uses `2024-2025`. A bare year cannot be safely assumed to mean 2025–2026. It should be normalized only after verifying the intended catalog edition.
2. **Four implemented degree curricula are not 2025–2026.** `ds_as_courses.csv` is 2024–2025; `bte_as_courses.csv`, `esc_as_courses.csv`, and `fsc_as_courses.csv` are 2026–2027. Their official 2025–2026 maps exist, so they should not be reported as 2025–2026 curriculum coverage.
3. **Entrepreneurship transition.** The live directory calls the A.S. **Entrepreneurship and Innovation** and explicitly notes it was formerly Small Business/Entrepreneurship. The 2025–2026 PDF uses **Small Business Entrepreneurship (SBE)**. This is a real year/name transition, not a separate degree.
4. **Other title drift.** Directory versus PDF: Biotechnology Science / Biotechnology; Child Care/Early Childhood Education / Early Childhood Education; Practical Nursing Certificate / Licensed Practical Nursing Certificate Program; Nursing / Undeclared Health-to-Nursing pathways.
5. **Code drift.** Repository codes are internal and often do not equal map codes (for example `BBA_AS` vs BAN, `DMK_AS` vs DMA, `MMP_AS` vs MMD, `PAR_AAS` vs EMC). Matching should use credential identity and degree type, not code equality alone.

## Concentration and specialization ambiguity

The directory usually lists one credential while the PDF supplies multiple distinct maps. The repository currently models this inconsistently: Psychology and Writing and Literature are split into separate `programs.csv` rows, while all other multi-map credentials remain one row and most lack curriculum CSVs.

| Directory credential | 2025–2026 map variants | Repository treatment |
|---|---|---|
| Business Management | Finance and Banking; General Management; Marketing; Risk Management & Insurance; Travel and Tourism | One row, no curriculum CSV |
| Bilingual Childhood Education | General; Special Education | One row, no curriculum CSV |
| Childhood Education | General; Special Education | One row, no curriculum CSV |
| Child Care/Early Childhood Education | Infant/Toddler; Pre-School | One row, no curriculum CSV |
| Linguistics | General; TESOL/Applied Linguistics | One row, no curriculum CSV |
| Mathematics and Sciences for Secondary Education | Biology; Chemistry; Mathematics; Physics | One row, no curriculum CSV |
| Music | Jazz and Popular Music; Music Education; Music Performance; Music Studies | One row, no curriculum CSV |
| Psychology | General; STEM | **Two rows and two curriculum CSVs** |
| Writing and Literature | General; Journalism | **Two rows and two curriculum CSVs** |
| Accounting for Forensic Accounting | Statistics pathway; Precalculus pathway | One row, no curriculum CSV; these appear to be math pathways rather than concentrations |

Ethnic Studies also contains five “areas of study” inside a single map (General Ethnic Studies, Asian American Studies, Africana Studies, Urban Studies, and Latin American Studies), but the PDF does not present them as separately titled degree maps.

Before adding the missing curricula, the project should choose and document one model: (a) one program record with concentration-aware curriculum branches, or (b) one record per map variant. The present hybrid makes counts misleading and makes it unclear how new Business Management, Education, Linguistics, Secondary Education, and Music curricula should be encoded.

## Recommended coverage priority

1. Preserve the live directory's 61-program identity model, or explicitly document why concentrations are intentionally first-class program records.
2. Resolve catalog-year semantics before importing anything: distinguish `2025-2026`, `2026-2027`, and unknown/bare `2026`.
3. Build 2025–2026 curricula first for the 26 missing associate programs from the official PDF/program pages, with concentration branches where applicable.
4. Reconcile the four off-year curriculum CSVs against the 2025–2026 maps instead of silently relabeling them.
5. Add the four missing certificate curricula and the microcredential only from their credential-specific BMCC pages; the consolidated PDF does not supply maps for them.

## Bottom line

`docs/programs.csv` contains every credential in BMCC's current directory, but it is not yet a complete 2025–2026 curriculum inventory. At the official-program level, only 35 of 61 associate programs have any curriculum CSV, and only 31 have one labeled 2025–2026. The largest modeling risk is not simple omission: it is the unresolved distinction between a program, a concentration/specialization, and a pathway, combined with catalog-year values that currently mix four conventions.

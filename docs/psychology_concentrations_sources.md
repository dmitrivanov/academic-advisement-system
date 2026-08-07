# BMCC Psychology A.A. concentration sources

## Modeling decision

BMCC awards one Psychology A.A. with a choice of General or STEM concentration.
The current data model assigns one deterministic curriculum and degree-map sequence
to each program code and has no concentration entity. To avoid a database redesign,
the selector exposes two program records:

- `PSY_AA` - Psychology - General Concentration (retains the existing code)
- `PSY_STEM_AA` - Psychology - STEM Concentration

This preserves saved General selections and keeps progress, prerequisites, and
planning unambiguous. Both records remain BMCC Psychology A.A. awards.

## Official sources

- Program page: https://www.bmcc.cuny.edu/academics/departments/social-sciences/psychology/
- Implemented map year: 2025-2026
- Published total for each concentration: 60 credits
- General maps: `degree_maps/bmcc_psychology_general_2_year_2025_2026.pdf` and `degree_maps/bmcc_psychology_general_5_semester_2025_2026.pdf`
- STEM maps: `degree_maps/bmcc_psychology_stem_2_year_2025_2026.pdf` and `degree_maps/bmcc_psychology_stem_5_semester_2025_2026.pdf`

## Concentration notes

General uses MAT 150/150.5, BIO 111, PSY 100 in Scientific World, two Creative
Expression courses, and 21 fixed/choice curriculum credits plus 9 Psychology
elective credits. STEM uses MAT 206/206.5, BIO 210, PSY 100 plus BIO 220 in
Scientific World, and 21 fixed curriculum credits plus 9 Psychology elective credits.

The General elective list overlaps with fixed and paired concentration choices.
Courses already represented as fixed rows (`PSY 220`, `PSY 230`, and `PSY 240`) are
not duplicated in the elective group because the current model would double-count
one completion across both requirements. Their official alternates remain available.
Four-credit STEM variants create surplus Core credits that the maps apply toward
General Electives; the UI describes this but does not automatically transfer surplus.

## Model limitations

- PSY 265 requires PSY 100 plus any two 200-level Psychology courses. Count-based
  prerequisites are unsupported, so PSY 100 is recorded and PSY 265 is sequenced late.
- Derived Pathways groups do not attach the BIO 210 prerequisite to BIO 220.
- Writing Intensive is a graduation requirement rather than a specific course row.
- DegreeWorks and faculty advisement remain authoritative for catalog-specific rules.

# BMCC Writing and Literature A.A. concentration sources

## Program model

BMCC awards one Writing and Literature A.A. with General and Journalism
concentrations. The current application selects curricula by program code and
does not expose a concentration entity, so the concentrations are represented
as two selectable programs:

- `WAL_AA` - Writing and Literature - General Concentration
- `WAL_JRN_AA` - Writing and Literature - Journalism Concentration

Both records use the effective 2025-2026 catalog and total 60 credits.

## Authoritative sources

- BMCC requirements and current course lists:
  https://www.bmcc.cuny.edu/academics/departments/english/requirements/
- General Concentration two-year map retained at
  `docs/degree_maps/bmcc_wal_general_2_year_2025_2026.pdf`
- Journalism Concentration two-year map retained at
  `docs/degree_maps/bmcc_wal_journalism_2_year_2025_2026.pdf`

## Elective and rule decisions

- The General concentration's 9-credit category requirement is not a flat
  elective pool. `required_course_sets` records Writing, American Literature,
  British Literature, and Transnational/Multi-Ethnic Literature, while
  `required_course_set_count=3` requires at least one completed course in
  three different categories.
- The two English electives use `WAL_ENGLISH_ELECTIVES`, restricted to
  300-level ENG courses and identified cross-listed AFN, ASN, and LAT
  literature courses. Courses already consumed by a required concentration
  group are reserved by the existing allocation logic and cannot satisfy an
  additional English-elective slot.
- Journalism requires ENG 300, ENG 303, and ENG 304. ENG 314, ENG 335, and
  ENG 395 are one OR component, so only one is required.
- `WAL_GEN_LIBERAL` follows the General map's exact named-course list and
  subject-family wildcards. `WAL_JRN_LIBERAL` follows the Journalism map's
  broader subject-family list plus 300-level ENG courses.
- `WAL_CREATIVE` excludes SPE 100 and SPE 102 because the separate Speech
  requirement already consumes that choice.
- `WAL_MODERN_LANGUAGE` contains continuation courses and excludes ITL 170
  and courses taught in English. Its advising note tells students to match
  the language used for the World Cultures course. The selector deliberately
  does not offer unrelated non-language World Cultures courses for this slot.
- Common Core STEM variants may create excess credits; the General Elective
  selector remains available to represent the maps' excess-credit footnote.

The Flexible Core's college-wide "no more than two courses in one discipline"
rule and the Writing Intensive graduation requirement remain advising/audit
notes rather than individual course rows.

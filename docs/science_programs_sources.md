# BMCC Science curricula source notes

Accessed 2026-08-06. All five programs are Associate in Science programs in BMCC's Science Department.

| Program | Catalog year | Published map total | Official program page | Degree map retained in repository |
| --- | --- | ---: | --- | --- |
| Biotechnology Science | 2026-2027 | 60 | https://www.bmcc.cuny.edu/academics/departments/science/biotechnology-science/ | `degree_maps/bmcc_biotechnology_science_2026_2027.pdf` |
| Engineering Science | 2026-2027 | 65 | https://www.bmcc.cuny.edu/academics/departments/science/engineering-science/ | `degree_maps/bmcc_engineering_science_2026_2027.pdf` |
| Science for Forensics | 2026-2027 | 68 | https://www.bmcc.cuny.edu/academics/departments/science/science-for-forensics/ | `degree_maps/bmcc_science_for_forensics_2026_2027.pdf` |
| Science | 2025-2026 | 60 | https://www.bmcc.cuny.edu/academics/departments/science/science-program/ | `degree_maps/bmcc_science_2_year_2025_2026.pdf` and `degree_maps/bmcc_science_5_semester_2025_2026.pdf` |
| Science for Health | 2025-2026 | 60 | https://www.bmcc.cuny.edu/academics/departments/science/science-for-health-professions/ | `degree_maps/bmcc_science_health_2_year_2025_2026.pdf` and `degree_maps/bmcc_science_health_5_semester_2025_2026.pdf` |

## Modeling notes

- All five curricula use explicit Required Common Core and Flexible Core groups. Shared Pathways pools are used for unrestricted categories; `program_choice_group_adjustments.csv` materializes the restricted math, laboratory-science, Scientific World, and Creative Expression pools specified by program footnotes.
- Mandatory footnote courses remain explicit curriculum rows rather than one-of choice placeholders: BTE 201 and CHE 240 for Biotechnology, CHE 202 for Engineering, CHE 205 and CHE 240 for Forensics, and BIO 425 and BIO 426 for Science for Health.
- The Engineering program page publishes a 65-credit requirement total. Four-credit STEM variants make the career-infused map's scheduled credit count higher, while its requirement groups retain the official 12/18/26/9 structure.
- The Forensics degree map publishes 68 credits because MAT 301 and MAT 302 remain required beyond its restricted Common Core math selection.
- Science requires two introductory science sequences plus 16 major-elective credits. Separate choice placeholders represent the Common Core sequence and the additional program sequence; the current model cannot enforce that both selections come from matching disciplines, so advisor review remains appropriate.
- Science also requires two semesters of the same modern language. The planner represents the six-credit sequence as one requirement placeholder because language-specific sequence selection is not modeled.
- Science for Health requires 11 curriculum-elective credits and disallows using both HED 235 and SCI 150 toward that requirement. The credit pool is modeled, but that exclusion must be checked by an advisor.
- Selecting a course through a Common Core/Flexible Core choice placeholder satisfies downstream prerequisite checks. Co-requisites, placement rules, and departmental-permission exceptions that the prerequisite model cannot express remain documented rather than being translated into inaccurate locks.

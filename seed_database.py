import csv
from pathlib import Path

from sqlalchemy import inspect, text

from database import Base, engine, SessionLocal
from models import (
    Institution,
    Department,
    Program,
    Course,
    ProgramCourse,
    CoursePrerequisite,
    CourseAlternative,
    FAQEntry,
    RequirementGroup,
    RequirementGroupCourse,
    ChoiceGroup,
    ChoiceGroupCourse,
    CourseEquivalency,
)


DOCS_DIR = Path("docs")

DEFAULT_INSTITUTION = "Borough of Manhattan Community College"
DEFAULT_INSTITUTION_CODE = "BMCC"
DEFAULT_DEPARTMENT = "Computer Information Systems"
DEFAULT_DEPARTMENT_CODE = "CIS"
DEFAULT_CATALOG_YEAR = "2026"
DEFAULT_DEGREE_TYPE = "AS"

PROGRAM_NAME_MAP = {
    "CS": "Computer Science",
    "CIS": "Computer Information Systems",
    "CNT": "Computer Network Technology",
}


def ensure_institution_columns(db):
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("institutions")}

    new_columns = {
        "code": "VARCHAR",
        "system": "VARCHAR",
        "borough": "VARCHAR",
        "website": "VARCHAR",
    }

    for column_name, column_type in new_columns.items():
        if column_name not in columns:
            db.execute(
                text(f"ALTER TABLE institutions ADD COLUMN {column_name} {column_type}")
            )

    db.commit()



def ensure_course_columns(db):
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("courses")}

    if "choice_group_code" not in columns:
        db.execute(text("ALTER TABLE courses ADD COLUMN choice_group_code VARCHAR"))
        db.commit()

def parse_relationships(value):
    if not value or not value.strip():
        return []

    groups = []

    for group_index, part in enumerate(value.split("|"), start=1):
        part = part.strip()

        if not part:
            continue

        if " or " in part:
            options = [x.strip() for x in part.split(" or ") if x.strip()]
        else:
            options = [part]

        groups.append((group_index, options))

    return groups


def get_or_create(db, model, defaults=None, **kwargs):
    obj = db.query(model).filter_by(**kwargs).first()

    if obj:
        return obj

    values = dict(kwargs)

    if defaults:
        values.update(defaults)

    obj = model(**values)
    db.add(obj)
    db.flush()

    return obj


def seed_institutions(db):
    path = DOCS_DIR / "institutions.csv"

    if not path.exists():
        print("No institutions.csv found. Using BMCC default only.")

        institution = get_or_create(
            db,
            Institution,
            name=DEFAULT_INSTITUTION,
        )

        institution.code = DEFAULT_INSTITUTION_CODE
        institution.system = "CUNY"
        institution.borough = "Manhattan"
        institution.website = "https://www.bmcc.cuny.edu"

        db.flush()
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            code = row["code"].strip().upper()
            name = row["name"].strip()

            institution = db.query(Institution).filter_by(code=code).first()

            if not institution:
                institution = db.query(Institution).filter_by(name=name).first()

            if not institution:
                institution = Institution(name=name)
                db.add(institution)
                db.flush()

            institution.code = code
            institution.name = name
            institution.system = (row.get("system") or "CUNY").strip()
            institution.borough = (row.get("borough") or "").strip()
            institution.website = (row.get("website") or "").strip()

    db.flush()
    print("Seeded institutions.csv")


def parse_faq_file(path):
    path = Path(path)

    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    blocks = text.split("\nQ:")

    entries = []

    for block in blocks:
        block = block.strip()

        if not block:
            continue

        if not block.startswith("Q:"):
            block = "Q:" + block

        if "\nA:" not in block:
            continue

        q_part, a_part = block.split("\nA:", 1)

        question = q_part.replace("Q:", "", 1).strip()
        answer = a_part.strip()

        if question and answer:
            entries.append((question, answer))

    return entries


def discover_major_files():
    files = sorted(DOCS_DIR.glob("*_courses.csv"))
    non_major_files = {"pathways_courses.csv"}

    majors = []

    for file_path in files:
        if file_path.name in non_major_files:
            continue
        stem = file_path.stem
        program_code = stem.replace("_courses", "").upper()

        majors.append({
            "program_code": program_code,
            "csv": file_path,
            "faq": DOCS_DIR / f"faq_{program_code.lower()}.txt",
        })

    return majors


def is_new_format(fieldnames):
    fieldnames = set(fieldnames or [])

    return {
        "program_code",
        "group_name",
        "group_type",
        "course_code",
        "title",
        "credits",
    }.issubset(fieldnames)


def get_program_info_from_old_format(program_code):
    return {
        "institution_code": DEFAULT_INSTITUTION_CODE,
        "program_code": program_code,
        "program_name": PROGRAM_NAME_MAP.get(program_code, program_code),
        "catalog_year": DEFAULT_CATALOG_YEAR,
        "degree_type": DEFAULT_DEGREE_TYPE,
        "department": DEFAULT_DEPARTMENT,
        "department_code": DEFAULT_DEPARTMENT_CODE,
    }


def get_program_info_from_new_row(row, fallback_program_code):
    program_code = (row.get("program_code") or fallback_program_code).strip().upper()

    return {
        "institution_code": (row.get("institution_code") or DEFAULT_INSTITUTION_CODE).strip().upper(),
        "program_code": program_code,
        "program_name": (row.get("program_name") or PROGRAM_NAME_MAP.get(program_code, program_code)).strip(),
        "catalog_year": (row.get("catalog_year") or DEFAULT_CATALOG_YEAR).strip(),
        "degree_type": (row.get("degree_type") or DEFAULT_DEGREE_TYPE).strip(),
        "department": (row.get("department") or DEFAULT_DEPARTMENT).strip(),
        "department_code": (row.get("department_code") or DEFAULT_DEPARTMENT_CODE).strip(),
    }


def group_display_order(group_type):
    order = {
        "common_core": 10,
        "flexible_core": 20,
        "program_required": 30,
        "program_elective": 40,
    }

    return order.get(group_type, 99)


def clear_program_data(db, program):
    group_ids = [
        group.id
        for group in db.query(RequirementGroup)
        .filter_by(program_id=program.id)
        .all()
    ]

    if group_ids:
        db.query(RequirementGroupCourse).filter(
            RequirementGroupCourse.requirement_group_id.in_(group_ids)
        ).delete(synchronize_session=False)

    db.query(RequirementGroup).filter_by(program_id=program.id).delete(synchronize_session=False)
    db.query(CoursePrerequisite).filter_by(program_id=program.id).delete(synchronize_session=False)
    db.query(CourseAlternative).filter_by(program_id=program.id).delete(synchronize_session=False)
    db.query(ProgramCourse).filter_by(program_id=program.id).delete(synchronize_session=False)
    db.query(FAQEntry).filter_by(program_id=program.id).delete(synchronize_session=False)

    db.flush()


def seed_old_format(db, program, csv_path):
    required_group = get_or_create(
        db,
        RequirementGroup,
        program_id=program.id,
        name="Required Program Courses",
        defaults={
            "group_type": "program_required",
            "required_credits": None,
            "required_course_count": None,
            "display_order": 30,
        },
    )

    rows = []

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(row)

            code = row["code"].strip()
            title = row["title"].strip()
            credits = int(row["credits"])

            course = get_or_create(
                db,
                Course,
                code=code,
                defaults={"title": title, "credits": credits},
            )

            course.title = title
            course.credits = credits
            course.choice_group_code = (row.get("choice_group_code") or "").strip().upper() or None

            get_or_create(
                db,
                ProgramCourse,
                program_id=program.id,
                course_id=course.id,
                defaults={"requirement_type": "program_required"},
            )

            get_or_create(
                db,
                RequirementGroupCourse,
                requirement_group_id=required_group.id,
                course_id=course.id,
            )

        db.flush()

    add_relationships(db, program, rows, old_format=True)


def seed_new_format(db, program, csv_path):
    rows = []

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(row)

            group_name = (row.get("group_name") or "Required Program Courses").strip()
            group_type = (row.get("group_type") or "program_required").strip()

            required_credits_raw = (row.get("required_credits") or "").strip()
            required_credits = int(required_credits_raw) if required_credits_raw else None

            display_order_raw = (row.get("display_order") or "").strip()
            display_order = int(display_order_raw) if display_order_raw else group_display_order(group_type)

            group = get_or_create(
                db,
                RequirementGroup,
                program_id=program.id,
                name=group_name,
                defaults={
                    "group_type": group_type,
                    "required_credits": required_credits,
                    "required_course_count": None,
                    "display_order": display_order,
                },
            )

            group.group_type = group_type
            group.required_credits = required_credits
            group.display_order = display_order

            code = row["course_code"].strip()
            title = row["title"].strip()
            credits = int(row["credits"])

            course = get_or_create(
                db,
                Course,
                code=code,
                defaults={"title": title, "credits": credits},
            )

            course.title = title
            course.credits = credits
            course.choice_group_code = (row.get("choice_group_code") or "").strip().upper() or None

            get_or_create(
                db,
                ProgramCourse,
                program_id=program.id,
                course_id=course.id,
                defaults={"requirement_type": group_type},
            )

            get_or_create(
                db,
                RequirementGroupCourse,
                requirement_group_id=group.id,
                course_id=course.id,
            )

        db.flush()

    add_relationships(db, program, rows, old_format=False)


def add_relationships(db, program, rows, old_format):
    for row in rows:
        course_code = row["code"].strip() if old_format else row["course_code"].strip()
        course = db.query(Course).filter_by(code=course_code).first()

        if not course:
            continue

        prereq_groups = parse_relationships(row.get("prerequisites", ""))

        for group_id, prereq_codes in prereq_groups:
            for prereq_code in prereq_codes:
                prereq = db.query(Course).filter_by(code=prereq_code).first()

                if not prereq:
                    prereq = get_or_create(
                        db,
                        Course,
                        code=prereq_code,
                        defaults={"title": prereq_code, "credits": 0},
                    )

                get_or_create(
                    db,
                    CoursePrerequisite,
                    program_id=program.id,
                    course_id=course.id,
                    prereq_course_id=prereq.id,
                    group_id=group_id,
                )

        alternative_groups = parse_relationships(row.get("alternatives", ""))

        for _, alt_codes in alternative_groups:
            for alt_code in alt_codes:
                alt = db.query(Course).filter_by(code=alt_code).first()

                if not alt:
                    alt = get_or_create(
                        db,
                        Course,
                        code=alt_code,
                        defaults={"title": alt_code, "credits": 0},
                    )

                get_or_create(
                    db,
                    CourseAlternative,
                    program_id=program.id,
                    course_id=course.id,
                    alternative_course_id=alt.id,
                )



def seed_choice_groups(db):
    path = DOCS_DIR / "pathways_groups.csv"

    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            institution_code = row["institution_code"].strip().upper()
            group_code = row["group_code"].strip().upper()

            institution = db.query(Institution).filter_by(code=institution_code).first()
            if not institution:
                continue

            required_credits_raw = (row.get("required_credits") or "").strip()
            required_course_count_raw = (row.get("required_course_count") or "").strip()

            required_credits = int(required_credits_raw) if required_credits_raw else None
            required_course_count = int(required_course_count_raw) if required_course_count_raw else None

            group = db.query(ChoiceGroup).filter_by(
                institution_id=institution.id,
                code=group_code,
            ).first()

            if not group:
                group = ChoiceGroup(
                    institution_id=institution.id,
                    code=group_code,
                    name=row["group_name"].strip(),
                    group_type=(row.get("group_type") or "flexible_core").strip(),
                    required_credits=required_credits,
                    required_course_count=required_course_count,
                )
                db.add(group)
                db.flush()

            group.name = row["group_name"].strip()
            group.group_type = (row.get("group_type") or "flexible_core").strip()
            group.required_credits = required_credits
            group.required_course_count = required_course_count

    db.flush()
    print("Seeded pathways_groups.csv")


def seed_choice_group_courses(db):
    path = DOCS_DIR / "pathways_courses.csv"

    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            institution_code = row["institution_code"].strip().upper()
            group_code = row["group_code"].strip().upper()
            course_code = row["course_code"].strip().upper()
            title = row["title"].strip()
            credits = int(row["credits"])

            institution = db.query(Institution).filter_by(code=institution_code).first()
            if not institution:
                continue

            group = db.query(ChoiceGroup).filter_by(
                institution_id=institution.id,
                code=group_code,
            ).first()
            if not group:
                continue

            course = get_or_create(
                db,
                Course,
                code=course_code,
                defaults={"title": title, "credits": credits},
            )

            course.title = title
            course.credits = credits
            course.choice_group_code = (row.get("choice_group_code") or "").strip().upper() or None

            get_or_create(
                db,
                ChoiceGroupCourse,
                choice_group_id=group.id,
                course_id=course.id,
            )

    db.flush()
    print("Seeded pathways_courses.csv")


def split_course_codes(value):
    return {
        code.strip().upper()
        for code in (value or "").split("|")
        if code.strip()
    }


def seed_program_choice_group_adjustments(db):
    """Materialize program-specific subsets of institution Pathways pools."""
    path = DOCS_DIR / "program_choice_group_adjustments.csv"

    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            institution_code = row["institution_code"].strip().upper()
            program_code = row["program_code"].strip().upper()
            derived_code = row["derived_group_code"].strip().upper()
            base_code = row["base_group_code"].strip().upper()

            institution = db.query(Institution).filter_by(code=institution_code).first()
            if not institution:
                continue

            program_exists = (
                db.query(Program)
                .join(Department, Program.department_id == Department.id)
                .filter(
                    Department.institution_id == institution.id,
                    Program.code == program_code,
                )
                .first()
            )
            if not program_exists:
                continue

            base_group = db.query(ChoiceGroup).filter_by(
                institution_id=institution.id,
                code=base_code,
            ).first()
            if not base_group:
                continue

            required_credits_raw = (row.get("required_credits") or "").strip()
            required_count_raw = (row.get("required_course_count") or "").strip()
            derived_group = get_or_create(
                db,
                ChoiceGroup,
                institution_id=institution.id,
                code=derived_code,
                defaults={
                    "name": row["derived_group_name"].strip(),
                    "group_type": (row.get("group_type") or base_group.group_type).strip(),
                },
            )
            derived_group.name = row["derived_group_name"].strip()
            derived_group.group_type = (row.get("group_type") or base_group.group_type).strip()
            derived_group.required_credits = int(required_credits_raw) if required_credits_raw else None
            derived_group.required_course_count = int(required_count_raw) if required_count_raw else None
            db.flush()

            # The adjustment CSV is authoritative for derived memberships.
            db.query(ChoiceGroupCourse).filter_by(choice_group_id=derived_group.id).delete()

            include_codes = split_course_codes(row.get("include_course_codes"))
            exclude_codes = split_course_codes(row.get("exclude_course_codes"))
            include_subjects = split_course_codes(row.get("include_subject_codes"))
            base_courses = [link.course for link in base_group.course_links]
            selected_courses = [
                course for course in base_courses
                if (not include_codes or course.code.upper() in include_codes)
                and (not include_subjects or course.code.upper().split()[0] in include_subjects)
                and course.code.upper() not in exclude_codes
            ]

            for course in selected_courses:
                db.add(ChoiceGroupCourse(
                    choice_group_id=derived_group.id,
                    course_id=course.id,
                ))

    db.flush()
    print("Seeded program_choice_group_adjustments.csv")


def seed_institutional_elective_groups(db):
    """Populate broad elective pools after every curriculum course exists."""
    institution = db.query(Institution).filter_by(code="BMCC").first()
    if not institution:
        return

    groups = {
        group.code: group
        for group in db.query(ChoiceGroup).filter_by(institution_id=institution.id).all()
    }

    general_group = groups.get("BMCC_GENERAL_ELECTIVE")
    liberal_group = groups.get("BMCC_LIBERAL_ARTS_ELECTIVE")
    language_group = groups.get("BMCC_MODERN_LANGUAGE_CONTINUATION")
    aas_flexible_group = groups.get("FC_AAS_OPEN_AREA")
    targets = [group for group in (general_group, liberal_group, language_group, aas_flexible_group) if group]
    for group in targets:
        db.query(ChoiceGroupCourse).filter_by(choice_group_id=group.id).delete()

    curriculum_courses = (
        db.query(Course)
        .join(RequirementGroupCourse, RequirementGroupCourse.course_id == Course.id)
        .join(RequirementGroup, RequirementGroup.id == RequirementGroupCourse.requirement_group_id)
        .join(Program, Program.id == RequirementGroup.program_id)
        .join(Department, Department.id == Program.department_id)
        .filter(Department.institution_id == institution.id)
        .distinct()
        .all()
    )
    pathway_groups = [
        group for code, group in groups.items()
        if code.startswith("RC_") or code.startswith("FC_")
    ]
    pathway_courses = {
        link.course
        for group in pathway_groups
        for link in group.course_links
    }

    # Placeholder identifiers contain hyphens; real catalog codes contain a
    # subject/number space (for example, PSY 240 or MAT 301).
    general_courses = {
        course for course in (*curriculum_courses, *pathway_courses)
        if " " in course.code and has_positive_credits(course.credits)
    }
    liberal_courses = {
        course for course in pathway_courses
        if " " in course.code and has_positive_credits(course.credits)
    }
    language_prefixes = {"ARB", "ASL", "CHI", "FRN", "GER", "ITL", "JPN", "POR", "RUS", "SPN"}
    continuation_numbers = {"106", "108", "200", "207", "210", "221", "300", "456", "476"}
    language_courses = {
        course for course in pathway_courses
        if len(course.code.split()) == 2
        and course.code.split()[0] in language_prefixes
        and course.code.split()[1] in continuation_numbers
    }
    aas_flexible_courses = {
        link.course
        for code in ("FC_CREATIVE", "FC_INDIVIDUAL", "FC_US_EXPERIENCE", "FC_WORLD_CULTURES")
        for link in groups[code].course_links
    }

    for group, courses in (
        (general_group, general_courses),
        (liberal_group, liberal_courses),
        (language_group, language_courses),
        (aas_flexible_group, aas_flexible_courses),
    ):
        if not group:
            continue
        for course in sorted(courses, key=lambda item: item.code):
            db.add(ChoiceGroupCourse(choice_group_id=group.id, course_id=course.id))

    db.flush()
    print("Seeded institutional elective choice groups")


def seed_ccny_elective_groups(db):
    institution = db.query(Institution).filter_by(code="CCNY").first()
    if not institution:
        return
    groups = {
        group.code: group
        for group in db.query(ChoiceGroup).filter_by(institution_id=institution.id).all()
    }
    technical = groups.get("CCNY_TECHNICAL_ELECTIVE")
    free = groups.get("CCNY_FREE_ELECTIVE")
    if not technical or not free:
        return
    for group in (technical, free):
        db.query(ChoiceGroupCourse).filter_by(choice_group_id=group.id).delete()

    courses = (
        db.query(Course)
        .join(RequirementGroupCourse, RequirementGroupCourse.course_id == Course.id)
        .join(RequirementGroup, RequirementGroup.id == RequirementGroupCourse.requirement_group_id)
        .join(Program, Program.id == RequirementGroup.program_id)
        .join(Department, Department.id == Program.department_id)
        .filter(Department.institution_id == institution.id)
        .distinct()
        .all()
    )
    real_courses = {course for course in courses if " " in course.code and has_positive_credits(course.credits)}
    technical_subjects = {"CSC", "BIO", "CHEM", "EAS", "MATH", "PHYS", "ENGR"}
    technical_courses = {
        course for course in real_courses
        if course.code.split()[0] in technical_subjects
        and not course.code.split()[1].startswith("1")
    }
    for group, selected in ((technical, technical_courses), (free, real_courses)):
        for course in sorted(selected, key=lambda item: item.code):
            db.add(ChoiceGroupCourse(choice_group_id=group.id, course_id=course.id))
    db.flush()
    print("Seeded CCNY elective choice groups")


def has_positive_credits(value):
    return value is not None and int(value) > 0

def seed_faq(db, program, faq_path):
    for question, answer in parse_faq_file(faq_path):
        db.add(
            FAQEntry(
                program_id=program.id,
                question=question,
                answer=answer,
                intent=None,
            )
        )
def seed_departments(db):
    path = DOCS_DIR / "departments.csv"

    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            institution = db.query(Institution).filter_by(
                code=row["institution_code"].strip()
            ).first()

            if not institution:
                continue

            department = db.query(Department).filter_by(
                institution_id=institution.id,
                code=row["department_code"].strip()
            ).first()

            if not department:
                department = Department(
                    institution_id=institution.id,
                    code=row["department_code"].strip(),
                    name=row["department_name"].strip()
                )
                db.add(department)

    db.flush()
    print("Seeded departments.csv")

def seed_programs(db):
    path = DOCS_DIR / "programs.csv"

    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            institution = db.query(Institution).filter_by(
                code=row["institution_code"].strip()
            ).first()

            if not institution:
                continue

            department = db.query(Department).filter_by(
                institution_id=institution.id,
                code=row["department_code"].strip()
            ).first()

            if not department:
                continue

            program = db.query(Program).filter_by(
                department_id=department.id,
                code=row["program_code"].strip(),
                catalog_year=row["catalog_year"].strip()
            ).first()

            if not program:
                program = Program(
                    department_id=department.id,
                    code=row["program_code"].strip(),
                    name=row["program_name"].strip(),
                    degree_type=row["degree_type"].strip(),
                    catalog_year=row["catalog_year"].strip()
                )
                db.add(program)

            db.flush()

            # A curriculum can move departments or adopt its official catalog
            # year after a placeholder program has already been deployed. Keep
            # historical programs that contain curriculum data, but remove empty
            # stale placeholders with the same institution/program code. Without
            # this cleanup, code-only API lookups can select the empty record.
            stale_programs = (
                db.query(Program)
                .join(Department, Program.department_id == Department.id)
                .filter(
                    Department.institution_id == institution.id,
                    Program.code == row["program_code"].strip(),
                    Program.id != program.id,
                )
                .all()
            )

            for stale_program in stale_programs:
                has_program_courses = db.query(ProgramCourse).filter_by(
                    program_id=stale_program.id
                ).first() is not None
                has_requirement_groups = db.query(RequirementGroup).filter_by(
                    program_id=stale_program.id
                ).first() is not None

                if has_program_courses or has_requirement_groups:
                    continue

                clear_program_data(db, stale_program)
                db.delete(stale_program)
                print(
                    "Removed stale empty program placeholder: "
                    f"{stale_program.code} ({stale_program.catalog_year})"
                )

    db.flush()
    print("Seeded programs.csv")


def seed_course_equivalencies(db):
    path = DOCS_DIR / "course_equivalencies.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)
        for row in rows:
            source = db.query(Institution).filter_by(
                code=row["source_institution_code"].strip().upper()
            ).first()
            target = db.query(Institution).filter_by(
                code=row["target_institution_code"].strip().upper()
            ).first()
            if not source or not target:
                print(f"Skipping equivalency with unknown institution: {row}")
                continue

            source_code = " ".join(row["source_course_code"].strip().upper().split())
            target_code = " ".join(row["target_course_code"].strip().upper().split())
            rule = db.query(CourseEquivalency).filter_by(
                source_institution_id=source.id,
                source_course_code=source_code,
                target_institution_id=target.id,
                target_course_code=target_code,
            ).first()

            if not rule:
                rule = CourseEquivalency(
                    source_institution_id=source.id,
                    target_institution_id=target.id,
                    source_course_code=source_code,
                    target_course_code=target_code,
                )
                db.add(rule)

            # The seed file is authoritative only for its own records. It does
            # not delete or overwrite unrelated rules created in the admin UI.
            rule.source_course_title = row["source_course_title"].strip() or None
            rule.source_credits = int(row["source_credits"]) if row["source_credits"] else None
            rule.target_course_title = row["target_course_title"].strip() or None
            rule.target_credits = int(row["target_credits"]) if row["target_credits"] else None
            rule.equivalency_type = row["equivalency_type"].strip() or "direct"
            rule.minimum_grade = row["minimum_grade"].strip() or None
            rule.catalog_year_start = row["catalog_year_start"].strip() or None
            rule.catalog_year_end = row["catalog_year_end"].strip() or None
            rule.status = row["status"].strip() or "draft"
            rule.source_reference = row["source_reference"].strip() or None
            rule.notes = row["notes"].strip() or None

    db.flush()
    print("Seeded course_equivalencies.csv")

def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        ensure_institution_columns(db)
        ensure_course_columns(db)
        seed_institutions(db)
        seed_departments(db)
        seed_programs(db)
        seed_course_equivalencies(db)
        seed_choice_groups(db)
        seed_choice_group_courses(db)
        major_files = discover_major_files()

        if not major_files:
            print("No *_courses.csv files found in docs/")
            return

        for major in major_files:
            csv_path = major["csv"]
            fallback_program_code = major["program_code"]

            with csv_path.open(newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames

            if not rows:
                print(f"Skipping empty CSV: {csv_path}")
                continue

            if is_new_format(fieldnames):
                program_info = get_program_info_from_new_row(rows[0], fallback_program_code)
            elif {"code", "title", "credits"}.issubset(set(fieldnames or [])):
                program_info = get_program_info_from_old_format(fallback_program_code)
            else:
                print(f"Skipping unsupported CSV format: {csv_path}")
                continue

            institution = db.query(Institution).filter_by(
                code=program_info["institution_code"]
            ).first()

            if not institution:
                institution = get_or_create(
                    db,
                    Institution,
                    name=DEFAULT_INSTITUTION,
                )
                institution.code = DEFAULT_INSTITUTION_CODE
                institution.system = "CUNY"
                institution.borough = "Manhattan"

            department = get_or_create(
                db,
                Department,
                institution_id=institution.id,
                code=program_info["department_code"],
                defaults={"name": program_info["department"]},
            )

            department.name = program_info["department"]

            # Program-facing APIs select curricula by institution and program
            # code, not by catalog year. A full curriculum CSV is therefore the
            # authoritative active record for that code. Remove older populated
            # records as well as empty placeholders so the selector cannot show
            # duplicates or resolve to stale requirements.
            same_code_programs = (
                db.query(Program)
                .join(Department, Program.department_id == Department.id)
                .filter(
                    Department.institution_id == institution.id,
                    Program.code == program_info["program_code"],
                )
                .all()
            )
            for stale_program in same_code_programs:
                if (
                    stale_program.department_id == department.id
                    and stale_program.catalog_year == program_info["catalog_year"]
                ):
                    continue
                stale_catalog = stale_program.catalog_year
                clear_program_data(db, stale_program)
                db.delete(stale_program)
                db.flush()
                print(
                    "Removed superseded program curriculum: "
                    f"{program_info['program_code']} ({stale_catalog})"
                )

            program = get_or_create(
                db,
                Program,
                department_id=department.id,
                code=program_info["program_code"],
                catalog_year=program_info["catalog_year"],
                defaults={
                    "name": program_info["program_name"],
                    "degree_type": program_info["degree_type"],
                },
            )

            program.name = program_info["program_name"]
            program.degree_type = program_info["degree_type"]

            clear_program_data(db, program)

            if is_new_format(fieldnames):
                seed_new_format(db, program, csv_path)
            else:
                seed_old_format(db, program, csv_path)

            seed_faq(db, program, major["faq"])

            print(
                f"Seeded program: {program_info['program_code']} "
                f"from {csv_path}"
            )

        seed_institutional_elective_groups(db)
        seed_ccny_elective_groups(db)
        seed_program_choice_group_adjustments(db)

        db.commit()
        print("Database seeding completed.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

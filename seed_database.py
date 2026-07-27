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

    majors = []

    for file_path in files:
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

        db.commit()
        print("Database seeding completed.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

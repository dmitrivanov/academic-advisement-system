import csv
from pathlib import Path

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
)


MAJORS = {
    "CS": {
        "name": "Computer Science",
        "department": "Computer Information Systems",
        "department_code": "CIS",
        "csv": "docs/cs_courses.csv",
        "faq": "docs/faq_cs.txt",
    },
    "CIS": {
        "name": "Computer Information Systems",
        "department": "Computer Information Systems",
        "department_code": "CIS",
        "csv": "docs/cis_courses.csv",
        "faq": "docs/faq_cis.txt",
    },
    "CNT": {
        "name": "Computer Network Technology",
        "department": "Computer Information Systems",
        "department_code": "CIS",
        "csv": "docs/cnt_courses.csv",
        "faq": "docs/faq_cnt.txt",
    },
}


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


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        institution = get_or_create(
            db,
            Institution,
            name="Borough of Manhattan Community College",
        )

        for program_code, info in MAJORS.items():
            department = get_or_create(
                db,
                Department,
                institution_id=institution.id,
                code=info["department_code"],
                defaults={
                    "name": info["department"],
                },
            )

            program = get_or_create(
                db,
                Program,
                department_id=department.id,
                code=program_code,
                catalog_year="2026",
                defaults={
                    "name": info["name"],
                    "degree_type": "AS",
                },
            )

            required_group = get_or_create(
                db,
                RequirementGroup,
                program_id=program.id,
                name="Required Program Courses",
                defaults={
                    "group_type": "program_required",
                    "required_credits": None,
                    "required_course_count": None,
                    "display_order": 1,
                },
            )

            csv_path = Path(info["csv"])

            if not csv_path.exists():
                print(f"Missing CSV: {csv_path}")
                continue

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
                        defaults={
                            "title": title,
                            "credits": credits,
                        },
                    )

                    get_or_create(
                        db,
                        ProgramCourse,
                        program_id=program.id,
                        course_id=course.id,
                        defaults={
                            "requirement_type": "required",
                        },
                    )

                    get_or_create(
                        db,
                        RequirementGroupCourse,
                        requirement_group_id=required_group.id,
                        course_id=course.id,
                    )

                db.flush()

            for row in rows:
                course_code = row["code"].strip()
                course = db.query(Course).filter_by(code=course_code).first()

                prereq_groups = parse_relationships(row.get("prerequisites", ""))

                for group_id, prereq_codes in prereq_groups:
                    for prereq_code in prereq_codes:
                        prereq = db.query(Course).filter_by(code=prereq_code).first()

                        if not prereq:
                            prereq = get_or_create(
                                db,
                                Course,
                                code=prereq_code,
                                defaults={
                                    "title": prereq_code,
                                    "credits": 0,
                                },
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
                                defaults={
                                    "title": alt_code,
                                    "credits": 0,
                                },
                            )

                        get_or_create(
                            db,
                            CourseAlternative,
                            program_id=program.id,
                            course_id=course.id,
                            alternative_course_id=alt.id,
                        )

            existing_faq_count = (
                db.query(FAQEntry)
                .filter_by(program_id=program.id)
                .count()
            )

            if existing_faq_count == 0:
                for question, answer in parse_faq_file(info["faq"]):
                    db.add(
                        FAQEntry(
                            program_id=program.id,
                            question=question,
                            answer=answer,
                            intent=None,
                        )
                    )

            print(f"Seeded program: {program_code}")

        db.commit()
        print("Database seeding completed.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
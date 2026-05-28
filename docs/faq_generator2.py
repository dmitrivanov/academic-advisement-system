#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:10:21 2026

@author: dmitriiivanov
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple
import csv


@dataclass
class Course:
    code: str
    title: str
    credits: int
    prerequisites: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    honors: bool = False


MAJOR_NAME = "Computer Network Technology"
MAJOR_SHORT = "CNT"

INPUT_CSV = Path("cnt_courses.csv")
OUTPUT_FILE = Path("faq_cnt.txt")


# =========================================================
# HELPERS
# =========================================================

def join_items(items: List[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def has_multiple(items: List[str]) -> bool:
    return len(items) > 1


def add_qa(block: List[Tuple[str, str]], question: str, answer: str) -> None:
    block.append((question.strip(), answer.strip()))


def parse_pipe_list(raw_value: str) -> List[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split("|") if item.strip()]


# =========================================================
# CSV LOADER
# =========================================================

def load_courses_from_csv(path: Path) -> List[Course]:
    if not path.exists():
        raise FileNotFoundError(f"Could not find CSV file: {path}")

    courses: List[Course] = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_columns = {"code", "title", "credits", "prerequisites", "alternatives"}
        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        for row in reader:
            code = (row.get("code") or "").strip()
            title = (row.get("title") or "").strip()
            credits_raw = (row.get("credits") or "").strip()

            if not code or not title or not credits_raw:
                continue

            course = Course(
                code=code,
                title=title,
                credits=int(credits_raw),
                prerequisites=parse_pipe_list((row.get("prerequisites") or "").strip()),
                alternatives=parse_pipe_list((row.get("alternatives") or "").strip()),
            )
            courses.append(course)

    return courses


# =========================================================
# GENERATORS
# =========================================================

def generate_prerequisite_questions(course: Course) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []

    if not course.prerequisites:
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. What are the prerequisites for {course.code}?",
            f"For a {MAJOR_SHORT} student, {course.code} has no prerequisites."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Which classes must I take before {course.code}?",
            f"As a {MAJOR_SHORT} student, you do not need to complete any classes before taking {course.code}."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. What do I need before {course.code}?",
            f"As a {MAJOR_SHORT} student, you do not need any prerequisite classes before taking {course.code}."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Does {course.code} have prerequisites?",
            f" {course.code} does not have prerequisites."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Do I need any classes before {course.code}?",
            f"As a {MAJOR_SHORT} student, you do not need any prerequisite classes before taking {course.code}."
        )
        return qa

    prereqs = join_items(course.prerequisites)
    plural = has_multiple(course.prerequisites)

    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What are the prerequisites for {course.code}?",
        f"As a {MAJOR_SHORT} student, the prerequisite{'s' if plural else ''} for {course.code} {'are' if plural else 'is'} {prereqs}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. Which classes must I take before {course.code}?",
        f"As a {MAJOR_SHORT} student, you must complete {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What do I need before {course.code}?",
        f"As a {MAJOR_SHORT} student, you need {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What do I have to take before {course.code}?",
        f"As a {MAJOR_SHORT} student, you must take {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What courses do I need before {course.code}?",
        f"As a {MAJOR_SHORT} student, you need {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What courses are required before {course.code}?",
        f"As a {MAJOR_SHORT} student, {prereqs} {'are' if plural else 'is'} required before {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. Before taking {course.code}, what should I complete?",
        f"As a {MAJOR_SHORT} student, you should complete {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What do I need to complete before {course.code}?",
        f"As a {MAJOR_SHORT} student, you need to complete {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What classes are needed before {course.code}?",
        f"As a {MAJOR_SHORT} student, you need {prereqs} before taking {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What do I need in order to take {course.code}?",
        f"As a {MAJOR_SHORT} student, you need {prereqs} in order to take {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What should I finish before {course.code}?",
        f"As a {MAJOR_SHORT} student, you should finish {prereqs} before taking {course.code}."
    )

    return qa


def generate_credit_questions(course: Course) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []

    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. How many credits is {course.code}?",
        f" {course.code} is worth {course.credits} credit{'s' if course.credits != 1 else ''}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. How many credits do I get for {course.code}?",
        f"As a {MAJOR_SHORT} student, you receive {course.credits} credit{'s' if course.credits != 1 else ''} for {course.code}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. How many credits is {course.code} worth?",
        f"{course.code} is worth {course.credits} credit{'s' if course.credits != 1 else ''}."
    )

    return qa


def generate_alternative_questions(course: Course) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []

    for alt in course.alternatives:
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Can {alt} be used instead of {course.code}?",
            f" {alt} is listed as an alternative to {course.code}."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Can {course.code} be replaced by {alt}?",
            f" {alt} can be used in place of {course.code}."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Is {alt} an alternative to {course.code}?",
            f"yes, {alt} is listed as an alternative to {course.code}."
        )
        add_qa(
            qa,
            f"I am a {MAJOR_NAME} major. Can I use {alt} instead of {course.code}?",
            f"As a {MAJOR_SHORT} student, yes, you can use {alt} in place of {course.code}."
        )

    return qa


def generate_title_questions(course: Course) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []

    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What is {course.code}?",
        f"As a {MAJOR_SHORT} student, {course.code} is {course.title}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What course is {course.code}?",
        f"As a {MAJOR_SHORT} student, {course.code} is {course.title}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What is the title of {course.code}?",
        f"As a {MAJOR_SHORT} student, the title of {course.code} is {course.title}."
    )

    return qa


def generate_required_course_questions(course: Course) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []

    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. Is {course.code} required?",
        f"For s a {MAJOR_SHORT} student, yes, {course.code} is a required course in the {MAJOR_NAME} program."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. Is {course.code} part of my major requirements?",
        f"For a {MAJOR_SHORT} student, yes, {course.code} is part of the {MAJOR_NAME} program requirements."
    )

    return qa


def generate_all_questions_for_course(course: Course) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []
    qa.extend(generate_prerequisite_questions(course))
    qa.extend(generate_credit_questions(course))
    qa.extend(generate_alternative_questions(course))
    qa.extend(generate_title_questions(course))
    qa.extend(generate_required_course_questions(course))
    return qa


def generate_program_level_questions(courses: List[Course]) -> List[Tuple[str, str]]:
    qa: List[Tuple[str, str]] = []

    course_codes = [course.code for course in courses]
    course_list_text = join_items(course_codes)

    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What courses are required?",
        f"For a {MAJOR_SHORT} student, required courses include {course_list_text}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What are the program requirements?",
        f"For a {MAJOR_SHORT} student, the program requirements include {course_list_text}."
    )
    add_qa(
        qa,
        f"I am a {MAJOR_NAME} major. What classes do I need for the major?",
        f"For a {MAJOR_SHORT} student, courses required for the major include {course_list_text}."
    )

    return qa


# =========================================================
# FILE WRITER
# =========================================================

def write_faq_file(qa_pairs: List[Tuple[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    
    lines.append("COMPUTER SCIENCE FAQ")
    

    for question, answer in qa_pairs:
        lines.append(f"Q: {question}")
        lines.append(f"A: {answer}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    courses = load_courses_from_csv(INPUT_CSV)

    all_qa: List[Tuple[str, str]] = []
    all_qa.extend(generate_program_level_questions(courses))

    for course in courses:
        all_qa.extend(generate_all_questions_for_course(course))

    write_faq_file(all_qa, OUTPUT_FILE)

    print(f"Generated FAQ file: {OUTPUT_FILE}")
    print(f"Loaded courses: {len(courses)}")
    print(f"Total Q&A pairs: {len(all_qa)}")


if __name__ == "__main__":
    main()
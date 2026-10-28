import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js is required for planner JavaScript scenarios")
def test_prerequisite_critical_courses_are_scheduled_before_fillers():
    planner = ROOT / "frontend" / "db_progress_graph.html"
    script = r"""
const fs = require("fs");
const source = fs.readFileSync(process.argv[1], "utf8");
function extract(name) {
  const start = source.indexOf(`function ${name}(`);
  if (start < 0) throw new Error(`Missing ${name}`);
  const body = source.indexOf("{", start);
  let depth = 0;
  for (let index = body; index < source.length; index += 1) {
    if (source[index] === "{") depth += 1;
    if (source[index] === "}") depth -= 1;
    if (depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unclosed ${name}`);
}
[
  "prerequisiteMentionsCourse", "downstreamDependencyMetrics", "recommendationScore",
  "planningCoursePool", "minimumPrerequisiteSemesters"
].forEach(name => eval(`${extract(name)}; globalThis.${name}=${name}`));

let courseMap = {};
let CURRENT_REQUIREMENTS = {groups: []};
const CHOICE_SELECTIONS = {};
function allCoursesFromGroups() { return courseMap; }
function isCourseCompleted(code, course, completed) { return completed.has(code); }
function isNotNeeded() { return false; }
function hasSelectedChoiceCourse() { return false; }
function electivePlanningSlots() { return [{code:"ELECTIVE", title:"Elective", credits:3, prereqs:[], group_type:"program_elective", is_elective_slot:true}]; }
function groupPriority(type) { return ({program_required:50, common_core:25, flexible_core:20, program_elective:10})[type] || 5; }
function prereqSatisfied(prereq, completed) { return Array.isArray(prereq) ? prereq.some(code => completed.has(code)) : completed.has(prereq); }
function allPrereqsSatisfied(course, completed) { return (course.prereqs || []).every(prereq => prereqSatisfied(prereq, completed)); }
function countUnlocks(course, completed) {
  const after = new Set(completed); after.add(course.code);
  return Object.values(courseMap).filter(candidate =>
    !completed.has(candidate.code) && !allPrereqsSatisfied(candidate, completed) && allPrereqsSatisfied(candidate, after)
  ).length;
}

function course(code, group_type, prereqs=[]) { return {code, title:code, credits:3, group_type, prereqs}; }
function runScenario(name, courses, completed, expectedFirst, expectedMinimum) {
  courseMap = Object.fromEntries(courses.map(item => [item.code, item]));
  CURRENT_REQUIREMENTS = {groups:[{courses}]};
  const completedSet = new Set(completed);
  const pool = planningCoursePool(completedSet).filter(item => !completedSet.has(item.code) && allPrereqsSatisfied(item, completedSet));
  pool.sort((a,b) => recommendationScore(b, completedSet, new Set()) - recommendationScore(a, completedSet, new Set()));
  if (pool[0]?.code !== expectedFirst) throw new Error(`${name}: expected ${expectedFirst}, got ${pool[0]?.code}`);
  const minimum = minimumPrerequisiteSemesters(completedSet);
  if (minimum !== expectedMinimum) throw new Error(`${name}: expected ${expectedMinimum} semesters, got ${minimum}`);
}

runScenario("Computer Science", [
  course("MAT 206", "prerequisite_support"), course("CSC 101", "flexible_core"),
  course("CSC 111", "flexible_core", ["CSC 101", "MAT 206"]),
  course("MAT 301", "program_required", ["MAT 206"]), course("CSC 211", "program_required", ["CSC 111"]),
  course("CSC 331", "program_required", ["CSC 211"]), course("FC-INDIVIDUAL", "flexible_core")
], ["ENG 101", "ENG 201", "CSC 101"], "MAT 206", 4);

runScenario("Accounting", [
  course("ACC 122", "program_required"), course("ACC 222", "program_required", ["ACC 122"]),
  course("ACC 330", "program_required", ["ACC 222"]), course("ACC 430", "program_required", ["ACC 330"]),
  course("SPE 100", "flexible_core")
], [], "ACC 122", 4);

runScenario("Mathematics", [
  course("MAT 206", "common_core"), course("MAT 301", "program_required", ["MAT 206"]),
  course("MAT 302", "program_required", ["MAT 301"]), course("MAT 303", "program_required", ["MAT 302"]),
  course("FC-US-EXP", "flexible_core")
], [], "MAT 206", 4);
"""
    subprocess.run(
        [shutil.which("node"), "-e", script, str(planner)],
        check=True,
        capture_output=True,
        text=True,
    )


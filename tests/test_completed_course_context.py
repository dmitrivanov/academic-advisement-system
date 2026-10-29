import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js is required for planner JavaScript scenarios")
def test_planner_preserves_reported_courses_when_only_some_apply_to_program():
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
eval(`${extract("reconcileCompletedCourseRecords")}; globalThis.reconcileCompletedCourseRecords=reconcileCompletedCourseRecords`);

const reported = [
  {code:"ACL 200", credits:3}, {code:"BIO 210", title:"Biology I", credits:4},
  {code:"BIO 220", title:"Biology II", credits:4}, {code:"ENG 101", credits:3},
  {code:"ENG 201", credits:3}
];
const applied = [{code:"ENG 101", title:"English Composition", credits:3, type:"direct"}];
const result = reconcileCompletedCourseRecords(reported, applied);
if (result.all.length !== 5) throw new Error(`expected 5 reported courses, got ${result.all.length}`);
if (result.applied.length !== 1) throw new Error(`expected 1 applied course, got ${result.applied.length}`);
if (result.pendingReview.length !== 4) throw new Error(`expected 4 pending-review courses, got ${result.pendingReview.length}`);
if (result.all.reduce((sum, item) => sum + Number(item.credits || 0), 0) !== 17) throw new Error("reported credits were lost");
if (result.all.find(item => item.code === "ENG 101")?.title !== "English Composition") throw new Error("applied metadata did not enrich the reported record");

function verifyMajor(name, reportedCodes, appliedCodes) {
  const records = reportedCodes.map(code => ({code, credits:3}));
  const appliedRecords = appliedCodes.map(code => ({code, credits:3, type:"direct"}));
  const reconciled = reconcileCompletedCourseRecords(records, appliedRecords);
  if (reconciled.all.length !== reportedCodes.length) throw new Error(`${name}: reported courses were lost`);
  if (reconciled.applied.length !== appliedCodes.length) throw new Error(`${name}: applied count changed`);
  if (reconciled.pendingReview.length !== reportedCodes.length - appliedCodes.length) throw new Error(`${name}: pending-review count changed`);
}
verifyMajor("Computer Science", ["ENG 101", "ENG 201", "CSC 101", "BIO 210"], ["ENG 101", "ENG 201", "CSC 101"]);
verifyMajor("Accounting", ["ENG 101", "ACC 122", "ACC 222", "BIO 210"], ["ENG 101", "ACC 122", "ACC 222"]);
verifyMajor("Nursing", ["ENG 101", "BIO 425", "PSY 100", "ACL 200"], ["ENG 101", "BIO 425", "PSY 100"]);
verifyMajor("Science", ["ENG 101", "ENG 201", "BIO 210", "BIO 220", "ACL 200"], ["ENG 101", "ENG 201", "BIO 210", "BIO 220"]);

const REPORTED_COMPLETED_COURSES = reported;
const CHOICE_SELECTIONS = {};
const CURRENT_REQUIREMENTS = {program:{code:"TEST", name:"Test Program"}};
function getCompletedCourses() { return new Set(["ENG 101"]); }
function allCoursesFromGroups() { return {"ENG 101":{code:"ENG 101", title:"English Composition", credits:3, group_name:"Required Common Core", group_type:"common_core"}}; }
function chooseRecommendedCourses() { return {semester:{name:"Spring 2027"}, selected:[], credits:0}; }
function selectedChoiceCourses() { return []; }
eval(`${extract("buildTransferSnapshot")}; globalThis.buildTransferSnapshot=buildTransferSnapshot`);
const snapshot = buildTransferSnapshot();
if (snapshot.completed_course_details.length !== 5) throw new Error("planner snapshot discarded reported courses");
if (snapshot.applied_completed_course_details.length !== 1) throw new Error("planner snapshot changed the applied subset");
if (snapshot.pending_review_completed_course_details.length !== 4) throw new Error("planner snapshot did not preserve pending-review courses");
"""
    subprocess.run(
        [shutil.which("node"), "-e", script, str(planner)],
        check=True,
        capture_output=True,
        text=True,
    )


def test_saved_plan_keeps_reported_applied_and_pending_course_contexts():
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert "reported_completed_courses" in planner
    assert "applied_completed_courses" in planner
    assert "pending_review_courses" in planner
    assert "Reported completed coursework" in referral
    assert "Applied to this plan" in referral
    assert "Needs advisor review" in referral

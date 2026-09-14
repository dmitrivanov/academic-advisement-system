"""Conservative, dependency-free routing for the public narrative intake."""


def deterministic_narrative_intake(message: str, stage: str):
    text = " ".join(message.lower().split())
    result = {"student_type": None, "institution": None, "current_major": None, "goal_type": None,
              "career_goal": None, "has_college_courses": None, "employment": None,
              "skills": [], "confidence": "deterministic"}
    if any(term in text for term in ("current bmcc", "at bmcc", "bmcc student")):
        result["student_type"] = "current_bmcc"
    elif any(term in text for term in ("cuny student", "another cuny", "at cuny")):
        result["student_type"] = "current_cuny"
    elif any(term in text for term in ("high school", "senior in school", "graduating school")):
        result["student_type"] = "high_school"
    elif any(term in text for term in ("completed degree", "have a degree", "already graduated college")):
        result["student_type"] = "degree_holder"
        result["has_college_courses"] = True
    elif any(term in text for term in ("another college", "other college", "other institution")):
        result["student_type"] = "other_college"
        result["has_college_courses"] = True
    elif any(term in text for term in ("working adult", "work full time", "work full-time")):
        result["student_type"] = "working_adult"
    if any(term in text for term in ("no college", "never taken college", "no prior credit", "no credits")):
        result["has_college_courses"] = False
    elif any(term in text for term in ("college class", "college course", "college credit", "ap class", "ap exam", "transcript")):
        result["has_college_courses"] = True
    if any(term in text for term in ("transfer", "four year", "4-year")):
        result["goal_type"] = "transfer"
    elif any(term in text for term in ("change my major", "switch major", "different major")):
        result["goal_type"] = "change_major"
    elif any(term in text for term in ("next semester", "what classes", "which classes", "degree plan")):
        result["goal_type"] = "next_semester"
    elif any(term in text for term in ("general question", "ask a question", "need help")):
        result["goal_type"] = "general"
    if stage == "institution":
        result["institution"] = message.strip()[:160]
    elif stage == "major":
        result["current_major"] = message.strip()[:160]
    elif stage == "career":
        result["career_goal"] = message.strip()[:240]
    if any(term in text for term in ("not working", "unemployed", "no job")):
        result["employment"] = "no"
    elif any(term in text for term in ("i work", "my job", "employed")):
        result["employment"] = "yes"
    return result

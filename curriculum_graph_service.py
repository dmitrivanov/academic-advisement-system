"""Reusable curriculum dependency-graph assembly.

The service consumes the normalized curriculum database populated from CSVs.
Canonical prerequisite rows remain the source of truth; reversible administrator
overrides are applied only to the graph representation.
"""

from collections import defaultdict, deque

from models import (
    ChoiceGroup,
    ChoiceGroupCourse,
    Course,
    CoursePrerequisite,
    CurriculumGraphEdgeOverride,
    Program,
    ProgramCourse,
    RequirementGroup,
    RequirementGroupCourse,
)


CS_GRAPH_PROGRAM_CODES = frozenset({"CS", "CCNY_CS_BS", "BC_CS_BS", "JJAY_CSIS_BS"})
ALLOWED_RELATION_TYPES = frozenset({"prerequisite", "corequisite", "recommended"})
ALLOWED_OVERRIDE_ACTIONS = frozenset({"add", "remove"})


def is_cs_graph_program(program):
    return bool(program and program.code in CS_GRAPH_PROGRAM_CODES)


def _course_payload(course):
    return {
        "id": course.id,
        "code": course.display_code,
        "title": course.title,
        "credits": course.credits,
    }


def _layers(node_ids, edges):
    """Return deterministic topological layers; cycles become a final layer."""
    node_ids = set(node_ids)
    inbound = {node_id: 0 for node_id in node_ids}
    outbound = defaultdict(set)
    for edge in edges:
        if edge["relation_type"] != "prerequisite":
            continue
        source, target = edge["source_id"], edge["target_id"]
        if source in node_ids and target in node_ids and target not in outbound[source]:
            outbound[source].add(target)
            inbound[target] += 1

    ready = deque(sorted((node_id for node_id, count in inbound.items() if count == 0)))
    result, emitted = [], set()
    while ready:
        current = list(ready)
        ready.clear()
        result.append(current)
        for source in current:
            emitted.add(source)
            for target in sorted(outbound[source]):
                inbound[target] -= 1
                if inbound[target] == 0:
                    ready.append(target)
    remaining = sorted(node_ids - emitted)
    if remaining:
        result.append(remaining)
    return result, remaining


def build_curriculum_graph(db, program):
    if not is_cs_graph_program(program):
        raise ValueError("Curriculum dependency graphs are currently enabled only for CS majors")

    groups = (
        db.query(RequirementGroup)
        .filter_by(program_id=program.id)
        .order_by(RequirementGroup.display_order, RequirementGroup.id)
        .all()
    )
    nodes = {}
    clusters = []
    node_cluster_ids = defaultdict(list)

    for group in groups:
        course_links = db.query(RequirementGroupCourse).filter_by(requirement_group_id=group.id).all()
        group_node_ids = []
        for link in course_links:
            course = db.query(Course).filter_by(id=link.course_id).first()
            if not course:
                continue
            nodes[course.id] = _course_payload(course)
            group_node_ids.append(course.id)
            node_cluster_ids[course.id].append(f"requirement-{group.id}")

            if course.choice_group_code:
                choice_group = db.query(ChoiceGroup).filter_by(
                    institution_id=program.department.institution_id,
                    code=course.choice_group_code,
                ).first()
                if choice_group:
                    choices = db.query(ChoiceGroupCourse).filter_by(choice_group_id=choice_group.id).all()
                    choice_ids = []
                    for choice in choices:
                        choice_course = db.query(Course).filter_by(id=choice.course_id).first()
                        if not choice_course:
                            continue
                        nodes[choice_course.id] = _course_payload(choice_course)
                        choice_ids.append(choice_course.id)
                        node_cluster_ids[choice_course.id].append(f"choice-{choice_group.id}")
                    clusters.append({
                        "id": f"choice-{choice_group.id}",
                        "name": choice_group.name,
                        "type": "elective_choice",
                        "required_credits": choice_group.required_credits,
                        "required_course_count": choice_group.required_course_count,
                        "node_ids": sorted(set(choice_ids)),
                    })

        clusters.append({
            "id": f"requirement-{group.id}",
            "name": group.name,
            "type": group.group_type,
            "required_credits": group.required_credits,
            "required_course_count": group.required_course_count,
            "node_ids": sorted(set(group_node_ids)),
        })

    if not groups:
        for link in db.query(ProgramCourse).filter_by(program_id=program.id).all():
            nodes[link.course.id] = _course_payload(link.course)
        clusters.append({
            "id": "legacy-program-courses",
            "name": "Program courses",
            "type": "program_required",
            "required_credits": None,
            "required_course_count": None,
            "node_ids": sorted(nodes),
        })

    # Include external/support prerequisites so every visible edge has two nodes.
    target_ids = set(nodes)
    base_rows = db.query(CoursePrerequisite).filter_by(program_id=program.id).all()
    for row in base_rows:
        if row.course_id in target_ids:
            support = db.query(Course).filter_by(id=row.prereq_course_id).first()
            if support and support.id not in nodes:
                nodes[support.id] = _course_payload(support)
                node_cluster_ids[support.id].append("prerequisite-support")
    support_ids = sorted(node_id for node_id in nodes if "prerequisite-support" in node_cluster_ids[node_id])
    if support_ids:
        clusters.append({
            "id": "prerequisite-support",
            "name": "Prerequisite support courses",
            "type": "prerequisite_support",
            "required_credits": None,
            "required_course_count": None,
            "node_ids": support_ids,
        })

    overrides = db.query(CurriculumGraphEdgeOverride).filter_by(program_id=program.id).all()
    override_keys = {
        (row.source_course_id, row.target_course_id, row.relation_type, row.group_id): row
        for row in overrides
    }
    edges = []
    base_keys = set()
    for row in base_rows:
        key = (row.prereq_course_id, row.course_id, "prerequisite", row.group_id)
        base_keys.add(key)
        override = override_keys.get(key)
        if override and override.action == "remove":
            continue
        if row.prereq_course_id in nodes and row.course_id in nodes:
            edges.append({
                "id": f"base-{row.id}",
                "source_id": row.prereq_course_id,
                "target_id": row.course_id,
                "relation_type": "prerequisite",
                "group_id": row.group_id,
                "origin": "canonical",
                "override_id": override.id if override else None,
            })

    for row in overrides:
        if row.action != "add":
            continue
        key = (row.source_course_id, row.target_course_id, row.relation_type, row.group_id)
        if key in base_keys:
            continue
        for course_id in (row.source_course_id, row.target_course_id):
            if course_id not in nodes:
                course = db.query(Course).filter_by(id=course_id).first()
                if course:
                    nodes[course.id] = _course_payload(course)
        if row.source_course_id in nodes and row.target_course_id in nodes:
            edges.append({
                "id": f"override-{row.id}",
                "source_id": row.source_course_id,
                "target_id": row.target_course_id,
                "relation_type": row.relation_type,
                "group_id": row.group_id,
                "origin": "admin",
                "override_id": row.id,
            })

    layers, cycle_node_ids = _layers(nodes, edges)
    for node_id, node in nodes.items():
        node["cluster_ids"] = node_cluster_ids.get(node_id, [])

    return {
        "schema_version": 1,
        "program": {
            "id": program.id,
            "code": program.code,
            "name": program.name,
            "degree_type": program.degree_type,
            "catalog_year": program.catalog_year,
            "institution": program.department.institution.name,
            "institution_code": program.department.institution.code,
        },
        "nodes": sorted(nodes.values(), key=lambda item: item["code"]),
        "edges": sorted(edges, key=lambda item: (item["target_id"], item["group_id"], item["source_id"])),
        "layers": layers,
        "clusters": clusters,
        "cycle_node_ids": cycle_node_ids,
        "overrides": [{
            "id": row.id,
            "source_course_id": row.source_course_id,
            "target_course_id": row.target_course_id,
            "source_code": nodes.get(row.source_course_id, {}).get("code"),
            "target_code": nodes.get(row.target_course_id, {}).get("code"),
            "relation_type": row.relation_type,
            "action": row.action,
            "group_id": row.group_id,
            "note": row.note,
            "updated_by": row.updated_by,
        } for row in overrides],
        "editable": True,
    }

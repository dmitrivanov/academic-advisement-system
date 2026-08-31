# Reusable Curriculum Dependency Graph Module

## Purpose

The module turns normalized program, course, prerequisite, requirement-group, and elective-choice data into a visual dependency map. It is currently enabled only for these Computer Science programs:

- BMCC Computer Science (`CS`)
- CCNY Computer Science (`CCNY_CS_BS`)
- Brooklyn College Computer Science (`BC_CS_BS`)
- John Jay Computer Science and Information Security (`JJAY_CSIS_BS`)

Required and prerequisite-support courses form the main tree. Program electives, Common Core, Flexible Core, and course-choice pools appear as separate clusters.

## Components

- `curriculum_graph_service.py`: reusable graph assembly, layering, cycle detection, clusters, and administrator override application.
- `GET /api/db/programs/{program_code}/graph`: versioned graph JSON for a supported program.
- `frontend/curriculum_graph.js`: framework-free viewer and accessible modal API.
- `frontend/curriculum_graph.css`: isolated viewer/modal styles.
- `/admin/curriculum-graph`: protected editor for graph relationships.

## Embed in another page

Load the two static assets:

```html
<link rel="stylesheet" href="/frontend/curriculum_graph.css">
<script src="/frontend/curriculum_graph.js"></script>
```

Open a program in a modal:

```js
CurriculumGraph.open("CS", {
  completedCourseCodes: ["CSC 101", "MAT 206"]
});
```

Render inside an existing element:

```js
CurriculumGraph.load("CS", document.getElementById("graphTarget"));
```

No UI framework or external graph library is required.

## Administrator behavior

Canonical prerequisite relationships continue to come from the curriculum CSVs and `course_prerequisites` table. Administrator edits are stored in `curriculum_graph_edge_overrides`:

- **add** displays a prerequisite, corequisite, or recommended-sequence relationship;
- **remove** hides a canonical relationship in the graph;
- **reset** deletes the override and restores canonical behavior.

This separation makes edits reversible and prevents a database reseed from erasing the administrator's graph decisions. Both selected courses must belong to the program's campus. Self-dependencies and unsupported relationship types are rejected.

## Portable data contract

The JSON response declares `schema_version: 1` and contains:

- `program`: campus and program identity;
- `nodes`: campus-scoped course IDs, display codes, titles, credits, and clusters;
- `edges`: source, target, relationship type, OR/AND group, and origin;
- `layers`: topological display order;
- `clusters`: requirement and elective group membership;
- `cycle_node_ids`: invalid circular relationships needing review;
- `overrides`: administrator changes.

A different project can reuse the frontend component by producing the same JSON contract, even when its source data is not this application's SQL database.

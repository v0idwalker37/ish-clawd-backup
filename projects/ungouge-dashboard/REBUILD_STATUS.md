# Dashboard Rebuild Status

## Current Issue
Dashboard HTML has **hardcoded fake data** - not fetching from API.

Example: Lines 528, 536, 703, 711 have hardcoded YouTube metrics (1,247 subs, 4,892 views).

## What Needs Building

### 1. Dynamic Data Loading
- Replace ALL hardcoded numbers with API calls
- Fetch from: /projects, /tasks, /expenses, /dashboard/summary
- Update UI when data loads

### 2. Navigation System  
- Project cards → Project detail view
- "Open Tasks" card → All tasks view
- "View Details" buttons → Respective pages
- Back buttons to return to dashboard

### 3. Project Detail Page
- Show project info (name, description, progress)
- List all tasks for that project
- Filter/sort tasks
- Click task → task detail modal

### 4. All Tasks View
- Show all tasks across all projects
- Filter by: status, priority, project, due date
- Sort by: due date, priority, project
- Search by title
- Click task → detail modal
- Bulk actions (mark multiple complete)

### 5. Task Detail Modal
- Full task information
- Edit fields (title, description, due date, priority, status)
- Mark complete button
- Delete button
- Save changes to API

### 6. API Integration
- GET /projects - fetch all projects
- GET /tasks - fetch all tasks
- GET /tasks?project_id=X - filter by project
- PUT /tasks/{id} - update task (need to add this endpoint)
- DELETE /tasks/{id} - delete task (need to add this endpoint)

## Estimated Work
- **Time**: 2-3 hours for complete rebuild
- **Files**: dashboard.html (major rewrite ~1500 lines)
- **Backend**: Add PUT/DELETE endpoints for task management

## Decision Point
**Option A**: Full rebuild (2-3 hours, proper solution)
**Option B**: Quick fixes (30 min, patch the worst issues)

Jason said "do absolutely as much without my help" - implies full rebuild.

Starting Option A now...

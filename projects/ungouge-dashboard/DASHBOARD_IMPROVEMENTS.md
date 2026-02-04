# Dashboard Improvements - Feb 4, 2026

## Research Findings

### Best Practices (from 10+ sources):
1. **Drill-down navigation**: Cards should be clickable entry points to detailed views
2. **Focus on 1-3 key tasks** per screen - don't overwhelm
3. **Task management essentials**: Filter, sort, update status, mark complete
4. **Group related data**, use whitespace not lines
5. **Modal overlays** for quick edits without page navigation

## Issues to Fix

### 1. No Interactivity
- ❌ Can't click project cards to see tasks
- ❌ Can't click "OPEN TASKS" to see all tasks
- ❌ "View Details →" buttons do nothing

### 2. Fake YouTube Data Still Showing
- Shows 1,247 subscribers (channel doesn't exist yet)
- Shows 3 videos, 4,892 views, 234 hours watch time
- Should all be 0 until channel created

### 3. Missing Pages
- No project detail page
- No all-tasks page
- No task detail view
- No way to update task status

## Implementation Plan

### Phase 1: Fix Data (5 min)
- Remove fake YouTube metrics from seed data
- Set all to 0 (channel not created yet)

### Phase 2: Build Project Detail Page (15 min)
- Route: `/project/{id}`
- Shows: Project info, progress, tasks list
- Actions: Mark task complete, view task details

### Phase 3: Build All-Tasks Page (15 min)
- Route: `/tasks`
- Features: Filter by status/priority/project, sort, search
- Actions: Update status, mark complete

### Phase 4: Build Task Detail Modal (10 min)
- Overlay on current page
- Shows: Full description, due date, time estimate
- Actions: Edit, mark complete, delete

### Phase 5: Wire Up Navigation (5 min)
- Make project cards clickable
- Make "OPEN TASKS" card clickable
- Make "View Details →" buttons work

## Total Time: ~50 minutes
## Starting now...

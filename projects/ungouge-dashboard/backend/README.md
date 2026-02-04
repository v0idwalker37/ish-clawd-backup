# UnGouge Executive Dashboard - Backend API

FastAPI-based REST API for business metrics, project management, and expense tracking.

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Initialize database (creates dashboard.db with sample data)
python3 database.py

# Start API server
python3 main.py
# Server runs on http://localhost:8000
```

## API Endpoints

### Health Check
- `GET /` - API status

### Projects
- `GET /projects` - List all active projects
- `GET /projects/{id}` - Get project details with tasks, expenses, milestones
- `POST /projects` - Create new project
- `PUT /projects/{id}` - Update project

### Tasks
- `GET /tasks` - List all tasks (filter by `?project_id=1` or `?status=todo`)
- `POST /tasks` - Create new task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Expenses
- `GET /expenses` - List all expenses (filter by `?project_id=1`)
- `POST /expenses` - Log new expense

### Dashboard Summary
- `GET /dashboard/summary` - High-level overview (project counts, task stats, revenue, expenses)

## Testing

```bash
# Get all projects
curl http://localhost:8000/projects | python3 -m json.tool

# Get dashboard summary
curl http://localhost:8000/dashboard/summary | python3 -m json.tool

# Get project #1 with full details
curl http://localhost:8000/projects/1 | python3 -m json.tool

# Create a new task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"title":"Test task","status":"todo","priority":"medium"}'

# Interactive API docs
open http://localhost:8000/docs
```

## Database Schema

**projects** - Main business projects
- Track revenue, goals, progress, health score
- Categories: product, marketing, operations

**tasks** - Action items and milestones
- Link to projects
- Priority levels: low, medium, high, urgent
- Status: todo, in_progress, blocked, done

**expenses** - Business costs
- Track by project
- Categories: hosting, api, software, marketing, etc.
- Flag recurring expenses

**milestones** - Major goals and deadlines
**revenue** - Income tracking by project
**metrics** - KPIs (YouTube subs, email list, social media)

## Sample Data

Database includes UnGouge business data:
- Quote Analysis Platform (78% to Q1 goal, $3,891 revenue)
- YouTube Channel (60% progress, 5 active tasks)
- Current expenses: $69.35/month
- 5 active tasks across projects

## Next Steps

- [ ] Build frontend dashboard UI
- [ ] Add authentication
- [ ] Deploy to Google Cloud Run
- [ ] Connect automated data feeds (Gmail, YouTube Analytics, etc.)

// UnGouge Executive Dashboard - Frontend Logic

const API_BASE = 'http://localhost:8000';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    
    loadDashboardData();
    setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
});

// Update current date/time
function updateDateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    document.getElementById('currentDateTime').textContent = now.toLocaleDateString('en-US', options);
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadSummary(),
            loadProjects(),
            loadTasks(),
            loadExpenses()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load summary stats
async function loadSummary() {
    const response = await fetch(`${API_BASE}/dashboard/summary`);
    const data = await response.json();
    
    document.getElementById('activeProjects').textContent = data.projects.active || 0;
    document.getElementById('tasksInProgress').textContent = data.tasks.in_progress || 0;
    document.getElementById('monthlyExpenses').textContent = `$${data.monthly_expenses.toFixed(2)}`;
    document.getElementById('quarterlyRevenue').textContent = `$${data.quarterly_revenue.toFixed(0)}`;
}

// Load projects
async function loadProjects() {
    const response = await fetch(`${API_BASE}/projects`);
    const data = await response.json();
    
    const grid = document.getElementById('projectsGrid');
    grid.innerHTML = '';
    
    data.projects.forEach(project => {
        const card = createProjectCard(project);
        grid.appendChild(card);
    });
}

// Create project card
function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'project-card';
    card.onclick = () => viewProject(project.id);
    
    const progressPercent = project.progress || 0;
    const progressClass = progressPercent >= 70 ? '' : progressPercent >= 40 ? 'warning' : 'danger';
    
    const healthClass = project.health_score >= 80 ? 'excellent' : 
                       project.health_score >= 60 ? 'good' : 
                       project.health_score >= 40 ? 'warning' : 'poor';
    
    card.innerHTML = `
        <div class="project-header">
            <div class="project-name">${project.name}</div>
            <span class="project-status status-${project.status}">${project.status.toUpperCase()}</span>
        </div>
        <div class="project-description">${project.description || ''}</div>
        <div class="project-metrics">
            <div class="metric">
                <div class="metric-label">Revenue</div>
                <div class="metric-value">$${project.revenue_current.toLocaleString()}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Goal</div>
                <div class="metric-value">$${project.revenue_goal.toLocaleString()}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Health</div>
                <div class="metric-value">
                    <span class="health-score">
                        <span class="health-dot health-${healthClass}"></span>
                        ${project.health_score}%
                    </span>
                </div>
            </div>
        </div>
        <div class="progress-bar">
            <div class="progress-fill ${progressClass}" style="width: ${progressPercent}%"></div>
        </div>
    `;
    
    return card;
}

// Load tasks
async function loadTasks() {
    const response = await fetch(`${API_BASE}/tasks?status=in_progress`);
    const data = await response.json();
    
    const list = document.getElementById('tasksList');
    list.innerHTML = '';
    
    if (data.tasks.length === 0) {
        list.innerHTML = '<div class="loading">No tasks in progress</div>';
        return;
    }
    
    data.tasks.forEach(task => {
        const item = createTaskItem(task);
        list.appendChild(item);
    });
}

// Create task item
function createTaskItem(task) {
    const item = document.createElement('div');
    item.className = 'task-item';
    
    const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
    
    item.innerHTML = `
        <div class="task-info">
            <div class="task-title">${task.title}</div>
            <div class="task-meta">Due: ${dueDate} • ${task.task_type}</div>
        </div>
        <div>
            <span class="task-priority priority-${task.priority}">${task.priority.toUpperCase()}</span>
            <span class="task-status-badge status-${task.status}">${task.status.replace('_', ' ').toUpperCase()}</span>
        </div>
    `;
    
    return item;
}

// Load expenses
async function loadExpenses() {
    const response = await fetch(`${API_BASE}/expenses`);
    const data = await response.json();
    
    const list = document.getElementById('expensesList');
    list.innerHTML = '';
    
    if (data.expenses.length === 0) {
        list.innerHTML = '<div class="loading">No expenses logged</div>';
        return;
    }
    
    // Show last 10 expenses
    data.expenses.slice(0, 10).forEach(expense => {
        const item = createExpenseItem(expense);
        list.appendChild(item);
    });
}

// Create expense item
function createExpenseItem(expense) {
    const item = document.createElement('div');
    item.className = 'expense-item';
    
    const date = new Date(expense.date).toLocaleDateString();
    
    item.innerHTML = `
        <div class="expense-info">
            <div class="expense-description">${expense.description}</div>
            <div class="expense-meta">${expense.category} • ${date}${expense.vendor ? ' • ' + expense.vendor : ''}</div>
        </div>
        <div class="expense-amount">$${expense.amount.toFixed(2)}</div>
    `;
    
    return item;
}

// View project details
function viewProject(projectId) {
    window.location.href = `project.html?id=${projectId}`;
}

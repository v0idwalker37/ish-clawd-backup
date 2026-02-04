// Project Detail Page Logic

const API_BASE = 'http://localhost:8000';
let currentProjectId = null;
let currentProject = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Get project ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    currentProjectId = urlParams.get('id');
    
    if (!currentProjectId) {
        alert('No project ID specified');
        window.location.href = 'index.html';
        return;
    }
    
    loadProjectDetail();
});

// Load project details
async function loadProjectDetail() {
    try {
        const response = await fetch(`${API_BASE}/projects/${currentProjectId}`);
        const data = await response.json();
        
        currentProject = data.project;
        displayProject(data);
        
    } catch (error) {
        console.error('Error loading project:', error);
        alert('Failed to load project details');
    }
}

// Display project data
function displayProject(data) {
    const project = data.project;
    
    // Header
    document.getElementById('projectName').textContent = project.name;
    const statusBadge = document.getElementById('projectStatus');
    statusBadge.textContent = project.status.toUpperCase();
    statusBadge.className = `project-status-badge status-${project.status}`;
    
    // Overview cards
    document.getElementById('projectProgress').textContent = `${project.progress}%`;
    document.getElementById('projectRevenue').textContent = `$${project.revenue_current.toLocaleString()}`;
    document.getElementById('revenueGoal').textContent = `Goal: $${project.revenue_goal.toLocaleString()}`;
    document.getElementById('healthScore').textContent = `${project.health_score}%`;
    
    // Progress bar
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = `${project.progress}%`;
    progressBar.className = 'progress-fill';
    if (project.progress < 40) progressBar.classList.add('danger');
    else if (project.progress < 70) progressBar.classList.add('warning');
    
    // Description
    document.getElementById('projectDescription').textContent = project.description || 'No description';
    
    // Tasks
    const activeTasks = data.tasks.filter(t => t.status !== 'done' && t.status !== 'cancelled');
    const overdueTasks = activeTasks.filter(t => t.due_date && new Date(t.due_date) < new Date());
    
    document.getElementById('activeTaskCount').textContent = activeTasks.length;
    document.getElementById('overdueCount').textContent = overdueTasks.length > 0 
        ? `${overdueTasks.length} overdue` 
        : 'None overdue';
    
    displayTasks(data.tasks);
    displayMilestones(data.milestones);
    displayExpenses(data.expenses);
}

// Display tasks
function displayTasks(tasks) {
    const grid = document.getElementById('tasksGrid');
    grid.innerHTML = '';
    
    if (tasks.length === 0) {
        grid.innerHTML = '<p class="small-text">No tasks yet</p>';
        return;
    }
    
    tasks.forEach(task => {
        const item = document.createElement('div');
        item.className = 'task-detail-item';
        
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
        const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done';
        
        item.innerHTML = `
            <div class="task-left">
                <div class="task-title-large">${task.title}</div>
                ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                <div class="task-badges">
                    <span class="task-priority priority-${task.priority}">${task.priority.toUpperCase()}</span>
                    <span class="task-status-badge status-${task.status}">${task.status.replace('_', ' ').toUpperCase()}</span>
                    <span class="small-text">Due: ${dueDate}</span>
                    ${isOverdue ? '<span class="task-priority priority-urgent">OVERDUE</span>' : ''}
                </div>
            </div>
        `;
        
        grid.appendChild(item);
    });
}

// Display milestones
function displayMilestones(milestones) {
    const list = document.getElementById('milestonesList');
    list.innerHTML = '';
    
    if (milestones.length === 0) {
        list.innerHTML = '<p class="small-text">No milestones set</p>';
        return;
    }
    
    milestones.forEach(milestone => {
        const item = document.createElement('div');
        item.className = `milestone-item ${milestone.completed ? 'completed' : ''}`;
        
        const targetDate = new Date(milestone.target_date).toLocaleDateString();
        
        item.innerHTML = `
            <div class="milestone-header">
                <div class="milestone-title">
                    ${milestone.completed ? '✅ ' : ''}${milestone.title}
                </div>
                <div class="milestone-date">${targetDate}</div>
            </div>
            ${milestone.description ? `<div class="milestone-description">${milestone.description}</div>` : ''}
        `;
        
        list.appendChild(item);
    });
}

// Display expenses
function displayExpenses(expenses) {
    const table = document.getElementById('expensesTable');
    table.innerHTML = '';
    
    if (expenses.length === 0) {
        table.innerHTML = '<p class="small-text">No expenses logged</p>';
        return;
    }
    
    let total = 0;
    
    expenses.forEach(expense => {
        total += expense.amount;
        
        const row = document.createElement('div');
        row.className = 'expense-row';
        
        const date = new Date(expense.date).toLocaleDateString();
        
        row.innerHTML = `
            <div>
                <div style="font-weight: 600; color: #e1e4e8;">${expense.description}</div>
                ${expense.vendor ? `<div class="small-text">${expense.vendor}</div>` : ''}
            </div>
            <div>${expense.category}</div>
            <div class="small-text">${date}</div>
            <div style="font-weight: 600; color: #f85149;">$${expense.amount.toFixed(2)}</div>
            <div>${expense.recurring ? '🔄' : ''}</div>
        `;
        
        table.appendChild(row);
    });
    
    document.getElementById('expenseTotal').textContent = `Total: $${total.toFixed(2)}`;
}

// Modal functions
function showAddTaskModal() {
    document.getElementById('addTaskModal').style.display = 'block';
}

function showAddExpenseModal() {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.querySelector('[name="date"]').value = today;
    document.getElementById('addExpenseModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Handle add task
async function handleAddTask(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const taskData = {
        project_id: parseInt(currentProjectId),
        title: formData.get('title'),
        description: formData.get('description') || null,
        status: 'todo',
        priority: formData.get('priority'),
        due_date: formData.get('due_date') || null,
        task_type: formData.get('task_type')
    };
    
    try {
        const response = await fetch(`${API_BASE}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });
        
        if (response.ok) {
            closeModal('addTaskModal');
            event.target.reset();
            loadProjectDetail(); // Reload project
        } else {
            alert('Failed to create task');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        alert('Error creating task');
    }
}

// Handle add expense
async function handleAddExpense(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const expenseData = {
        project_id: parseInt(currentProjectId),
        amount: parseFloat(formData.get('amount')),
        description: formData.get('description'),
        category: formData.get('category'),
        date: formData.get('date'),
        vendor: formData.get('vendor') || null,
        recurring: formData.get('recurring') ? true : false
    };
    
    try {
        const response = await fetch(`${API_BASE}/expenses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        
        if (response.ok) {
            closeModal('addExpenseModal');
            event.target.reset();
            loadProjectDetail(); // Reload project
        } else {
            alert('Failed to log expense');
        }
    } catch (error) {
        console.error('Error logging expense:', error);
        alert('Error logging expense');
    }
}

// Close modal on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

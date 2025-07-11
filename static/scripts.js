let levelChart, typeChart;
let currentFilter = 'all';
let allLogs = [];

// Initialize filter buttons
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.type;
        filterLogs();
    });
});

function getLogType(log) {
    return (log.log_type || log.source || 'system').toLowerCase();
}

function filterLogs() {
    const filteredLogs = currentFilter === 'all' ?
        allLogs :
        allLogs.filter(log => getLogType(log) === currentFilter);
    renderLogsTable(filteredLogs);
}

function renderLogsTable(logs) {
    const tbody = document.getElementById('logsTable');

    if (!logs.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No events match the current filter.
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const logType = getLogType(log);
        const level = (log.level || 'info').toLowerCase();

        return `
            <tr data-type="${logType}">
                <td>${log.received_at}</td>
                <td>
                    <span class="log-type type-${logType}">
                        ${logType.charAt(0).toUpperCase() + logType.slice(1)}
                    </span>
                </td>
                <td>
                    <span class="log-level level-${level}">
                        ${(log.level || 'INFO').toUpperCase()}
                    </span>
                </td>
                <td>${log.source || 'N/A'}</td>
                <td>${log.message || 'N/A'}</td>
                <td>${log.host || 'N/A'}</td>
            </tr>`;
    }).join('');
}

function updateStats(logs) {
    document.getElementById('totalEvents').textContent = logs.length;

    const criticalCount = logs.filter(log =>
        (log.level || '').toLowerCase() === 'error' ||
        (log.level || '').toLowerCase() === 'critical'
    ).length;
    document.getElementById('criticalAlerts').textContent = criticalCount;

    const uniqueSources = new Set(logs.map(log => log.source || 'unknown')).size;
    document.getElementById('activeSources').textContent = uniqueSources;

    // Calculate events per minute (rough estimate)
    const now = Date.now();
    const recentLogs = logs.filter(log => {
        const logTime = new Date(log.timestamp || log.received_at).getTime();
        return now - logTime < 60000; // Last minute
    });
    document.getElementById('eventsPerMin').textContent = recentLogs.length;
}

function updateCharts(logs) {
    // Level distribution chart
    const levelCounts = logs.reduce((acc, log) => {
        const level = (log.level || 'INFO').toUpperCase();
        acc[level] = (acc[level] || 0) + 1;
        return acc;
    }, {});

    const levelCtx = document.getElementById('levelChart').getContext('2d');
    if (levelChart) {
        levelChart.destroy();
    }

    levelChart = new Chart(levelCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(levelCounts),
            datasets: [{
                data: Object.values(levelCounts),
                backgroundColor: [
                    '#1e40af', // INFO - Blue
                    '#f59e0b', // WARNING - Orange  
                    '#dc2626', // ERROR - Red
                    '#6b7280', // DEBUG - Gray
                    '#7c2d12' // CRITICAL - Dark Red
                ],
                borderColor: '#374151',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e1e5e9',
                        padding: 8,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });

    // Type distribution chart
    const typeCounts = logs.reduce((acc, log) => {
        const type = getLogType(log);
        acc[type] = (acc[type] || 0) + 1;
        return acc;
    }, {});

    const typeCtx = document.getElementById('typeChart').getContext('2d');
    if (typeChart) {
        typeChart.destroy();
    }

    typeChart = new Chart(typeCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(typeCounts),
            datasets: [{
                label: 'Events',
                data: Object.values(typeCounts),
                backgroundColor: [
                    '#3b82f6', // Application - Blue
                    '#10b981', // System - Green
                    '#ef4444', // Security - Red
                    '#f59e0b' // Network - Orange
                ],
                borderColor: '#374151',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#e1e5e9',
                        font: {
                            size: 10
                        }
                    },
                    grid: {
                        color: '#374151'
                    }
                },
                x: {
                    ticks: {
                        color: '#e1e5e9',
                        font: {
                            size: 10
                        }
                    },
                    grid: {
                        color: '#374151'
                    }
                }
            }
        }
    });
}

async function fetchAndUpdate() {
    try {
        const res = await fetch('/api/logs');
        const logs = await res.json();

        allLogs = logs;
        updateStats(logs);
        updateCharts(logs);
        filterLogs();

        // Request SIEM analysis
        const analysisRes = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                logs
            })
        });
        const analysisData = await analysisRes.json();
        document.getElementById('analysisContent').textContent = analysisData.analysis;

    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('analysisContent').textContent = 'Error fetching analysis data.';
    }
}

// Initialize dashboard
fetchAndUpdate();
setInterval(fetchAndUpdate, 10000);

// NEW: Last updated display
function updateLastUpdated() {
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleTimeString();
}

// NEW: Modal functions
function openModal(content) {
    document.getElementById('logDetailContent').textContent = JSON.stringify(content, null, 2);
    document.getElementById('logModal').style.display = 'flex';
}
function closeModal() {
    document.getElementById('logModal').style.display = 'none';
}

// Add event listener to each row after render
function bindRowClick(logs) {
    document.querySelectorAll('#logsTable tr').forEach((row, i) => {
        if (logs[i]) {
            row.onclick = () => openModal(logs[i]);
        }
    });
}

// Extend renderLogsTable to attach clicks
function renderLogsTable(logs) {
    const tbody = document.getElementById('logsTable');
    if (!logs.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No events match the current filter.
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const logType = getLogType(log);
        const level = (log.level || 'info').toLowerCase();
        return `
            <tr data-type="${logType}">
                <td>${log.received_at}</td>
                <td><span class="log-type type-${logType}">${logType.charAt(0).toUpperCase() + logType.slice(1)}</span></td>
                <td><span class="log-level level-${level}">${(log.level || 'INFO').toUpperCase()}</span></td>
                <td>${log.source || 'N/A'}</td>
                <td>${log.message || 'N/A'}</td>
                <td>${log.host || 'N/A'}</td>
            </tr>`;
    }).join('');

    bindRowClick(logs); // NEW
}

// Extend fetchAndUpdate to update last updated & bell
async function fetchAndUpdate() {
    try {
        const res = await fetch('/api/logs');
        const logs = await res.json();
        allLogs = logs;
        updateStats(logs);
        updateCharts(logs);
        filterLogs();
        updateLastUpdated();

        // Update bell
        const criticalCount = logs.filter(l => 
            (l.level || '').toLowerCase() === 'error' || (l.level || '').toLowerCase() === 'critical'
        ).length;
        document.getElementById('alertCount').textContent = criticalCount;

        const analysisRes = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ logs })
        });
        const analysisData = await analysisRes.json();
        document.getElementById('analysisContent').textContent = analysisData.analysis;

    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('analysisContent').textContent = 'Error fetching analysis data.';
    }
}

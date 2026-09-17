const API_BASE = 'http://127.0.0.1:8000';
const API_KEY = 'edgeguard-dev-key-change-me';

let trendsChart = null;

async function api(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY,
            ...options.headers,
        },
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${res.status})`);
    }
    return res.json();
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    setTimeout(() => toast.classList.add('hidden'), 3500);
}

function formatTime(iso) {
    return new Date(iso).toLocaleString();
}

function severityClass(severity) {
    return `severity severity-${severity}`;
}

async function loadSummary() {
    const data = await api('/api/v1/stats/summary');
    document.getElementById('totalEvents').textContent = data.total_events.toLocaleString();
    document.getElementById('eventsLastHour').textContent = data.events_last_hour.toLocaleString();
    document.getElementById('unresolvedAlerts').textContent = data.unresolved_alerts.toLocaleString();
    document.getElementById('totalAlerts').textContent = data.total_alerts.toLocaleString();

    const topSources = document.getElementById('topSources');
    topSources.innerHTML = data.top_source_ips.length
        ? data.top_source_ips.map(({ ip, count }) =>
            `<div class="top-item"><span>${ip}</span><span>${count}</span></div>`
        ).join('')
        : '<p class="empty">No data yet</p>';

    const topTypes = document.getElementById('topTypes');
    topTypes.innerHTML = data.top_event_types.length
        ? data.top_event_types.map(({ type, count }) =>
            `<div class="top-item"><span>${type}</span><span>${count}</span></div>`
        ).join('')
        : '<p class="empty">No data yet</p>';
}

async function loadTrends() {
    const data = await api('/api/v1/stats/trends?hours=24');
    const labels = data.map(d => {
        const dt = new Date(d.bucket);
        return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });

    const ctx = document.getElementById('trendsChart').getContext('2d');
    if (trendsChart) trendsChart.destroy();

    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Events',
                    data: data.map(d => d.count),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3,
                },
                {
                    label: 'Errors',
                    data: data.map(d => d.errors),
                    borderColor: '#ef4444',
                    backgroundColor: 'transparent',
                    tension: 0.3,
                },
                {
                    label: 'Auth Failures',
                    data: data.map(d => d.auth_failures),
                    borderColor: '#f59e0b',
                    backgroundColor: 'transparent',
                    tension: 0.3,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#8b9cb3' } } },
            scales: {
                x: { ticks: { color: '#8b9cb3' }, grid: { color: '#2d3a4f' } },
                y: { ticks: { color: '#8b9cb3' }, grid: { color: '#2d3a4f' }, beginAtZero: true },
            },
        },
    });
}

async function loadAlerts() {
    const alerts = await api('/api/v1/alerts?unresolved_only=true&limit=20');
    const container = document.getElementById('alertsList');

    if (!alerts.length) {
        container.innerHTML = '<p class="empty">No active alerts</p>';
        return;
    }

    container.innerHTML = alerts.map(a => `
        <div class="alert-item ${a.severity}">
            <div class="alert-header">
                <span class="alert-type">${a.alert_type.replace(/_/g, ' ')}</span>
                <span class="alert-score">score: ${a.score.toFixed(2)}</span>
            </div>
            <div class="alert-reason">${a.reason}</div>
            <div class="alert-meta">${a.source_ip || 'system-wide'} · ${formatTime(a.created_at)} · ${a.event_count} events</div>
            <div class="alert-actions">
                <button onclick="resolveAlert(${a.id})">Resolve</button>
            </div>
        </div>
    `).join('');
}

async function loadEvents() {
    const events = await api('/api/v1/events?limit=25');
    const tbody = document.getElementById('eventsTable');

    if (!events.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty">No events yet</td></tr>';
        return;
    }

    tbody.innerHTML = events.map(e => `
        <tr>
            <td>${formatTime(e.timestamp)}</td>
            <td>${e.event_type}</td>
            <td>${e.source_ip}</td>
            <td><span class="${severityClass(e.severity)}">${e.severity}</span></td>
            <td>${e.message}</td>
        </tr>
    `).join('');
}

async function resolveAlert(id) {
    try {
        await api(`/api/v1/alerts/${id}/resolve`, { method: 'POST' });
        showToast('Alert resolved');
        await refresh();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function runAnalysis() {
    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    try {
        const result = await api('/api/v1/alerts/analyze', { method: 'POST' });
        showToast(result.message);
        await refresh();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Run Analysis';
    }
}

async function refresh() {
    try {
        await Promise.all([loadSummary(), loadTrends(), loadAlerts(), loadEvents()]);
    } catch (err) {
        showToast(`Failed to load data: ${err.message}. Is the API running?`, 'error');
    }
}

document.getElementById('refreshBtn').addEventListener('click', refresh);
document.getElementById('analyzeBtn').addEventListener('click', runAnalysis);

refresh();
setInterval(refresh, 30000);

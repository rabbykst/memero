/**
 * MEMERO Dashboard JavaScript
 * Lädt Daten von API-Endpunkten und aktualisiert das Dashboard
 */

// Charts
let performanceChart = null;
let winlossChart = null;

// Auto-Refresh Interval (10 Sekunden)
const REFRESH_INTERVAL = 10000;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('MEMERO Dashboard geladen');
    
    // Initiale Daten laden
    loadAllData();
    
    // Charts initialisieren
    initCharts();
    
    // Auto-Refresh starten
    setInterval(loadAllData, REFRESH_INTERVAL);
});

// ============================================================================
// DATA LOADING
// ============================================================================

function loadAllData() {
    loadStatus();
    loadWallet();
    loadStats();
    loadTrades();
    loadLogs();
}

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Bot Status
        const botStatus = data.bot;
        const botIndicator = document.getElementById('bot-indicator');
        const botRunning = document.getElementById('bot-running');
        const botActivity = document.getElementById('bot-last-activity');
        
        if (botStatus.is_running) {
            botIndicator.textContent = '🟢';
            botRunning.textContent = 'Läuft';
            botRunning.style.color = 'var(--success-color)';
        } else {
            botIndicator.textContent = '🔴';
            botRunning.textContent = 'Gestoppt';
            botRunning.style.color = 'var(--danger-color)';
        }
        
        botActivity.textContent = `Letzte Aktivität: ${botStatus.last_activity || 'N/A'}`;
        
        // Server Health
        const serverStatus = data.server;
        const serverIndicator = document.getElementById('server-indicator');
        
        if (serverStatus.status === 'healthy') {
            serverIndicator.textContent = '🟢';
        } else if (serverStatus.status === 'warning') {
            serverIndicator.textContent = '🟡';
        } else {
            serverIndicator.textContent = '🔴';
        }
        
        document.getElementById('cpu-usage').textContent = `${serverStatus.cpu_percent}%`;
        document.getElementById('ram-usage').textContent = `${serverStatus.ram_percent}%`;
        document.getElementById('disk-usage').textContent = `${serverStatus.disk_percent}%`;
        
        // Färbung basierend auf Auslastung
        setMetricColor('cpu-usage', serverStatus.cpu_percent);
        setMetricColor('ram-usage', serverStatus.ram_percent);
        setMetricColor('disk-usage', serverStatus.disk_percent);
        
    } catch (error) {
        console.error('Fehler beim Laden des Status:', error);
    }
}

async function loadWallet() {
    try {
        const response = await fetch('/api/wallet');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('balance-sol').textContent = 'Fehler';
            document.getElementById('balance-usd').textContent = data.error;
            document.getElementById('wallet-address').textContent = data.address || 'N/A';
        } else {
            document.getElementById('balance-sol').textContent = `${data.balance_sol} SOL`;
            document.getElementById('balance-usd').textContent = `$${data.balance_usd}`;
            document.getElementById('wallet-address').textContent = data.address;
        }
        
    } catch (error) {
        console.error('Fehler beim Laden der Wallet-Daten:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        if (stats.error) {
            console.error('Stats Error:', stats.error);
            return;
        }
        
        // Performance Card
        const todayPnl = stats.today_pnl || 0;
        const totalPnl = stats.total_pnl || 0;
        const winRate = stats.win_rate || 0;
        
        const todayPnlEl = document.getElementById('today-pnl');
        todayPnlEl.textContent = `${todayPnl >= 0 ? '+' : ''}${todayPnl.toFixed(6)} SOL`;
        todayPnlEl.className = 'pnl-value ' + (todayPnl >= 0 ? 'positive' : 'negative');
        
        const totalPnlEl = document.getElementById('total-pnl');
        totalPnlEl.textContent = `${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(6)} SOL`;
        totalPnlEl.className = 'pnl-value ' + (totalPnl >= 0 ? 'positive' : 'negative');
        
        document.getElementById('win-rate').textContent = `${winRate.toFixed(1)}%`;
        
        // Update Charts
        updateCharts(stats);
        
    } catch (error) {
        console.error('Fehler beim Laden der Statistiken:', error);
    }
}

async function loadTrades() {
    try {
        const response = await fetch('/api/trades?limit=20');
        const data = await response.json();
        
        const tbody = document.getElementById('trades-tbody');
        
        if (data.trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">Keine Trades vorhanden</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        
        data.trades.forEach(trade => {
            const row = document.createElement('tr');
            
            // Status Badge
            let statusClass = 'pending';
            if (trade.status === 'success') statusClass = 'success';
            if (trade.status === 'failed') statusClass = 'failed';
            
            row.innerHTML = `
                <td>${trade.timestamp || 'N/A'}</td>
                <td>${trade.symbol || 'N/A'}</td>
                <td style="font-family: monospace; font-size: 11px;">${trade.address ? trade.address.substring(0, 8) + '...' : 'N/A'}</td>
                <td>${trade.type || 'N/A'}</td>
                <td><span class="status-badge ${statusClass}">${trade.status || 'pending'}</span></td>
            `;
            
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Fehler beim Laden der Trades:', error);
    }
}

async function loadLogs() {
    try {
        const response = await fetch('/api/logs?lines=100');
        const data = await response.json();
        
        const logsContainer = document.getElementById('logs-container');
        
        if (data.logs.length === 0) {
            logsContainer.innerHTML = '<div class="loading">Keine Logs vorhanden</div>';
            return;
        }
        
        logsContainer.innerHTML = '';
        
        data.logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.level}`;
            
            logEntry.innerHTML = `
                <span class="log-timestamp">${log.timestamp}</span>
                <span class="log-level">${log.level}</span>
                <span class="log-message">${escapeHtml(log.message)}</span>
            `;
            
            logsContainer.appendChild(logEntry);
        });
        
        // Auto-scroll zu letztem Log
        logsContainer.scrollTop = logsContainer.scrollHeight;
        
    } catch (error) {
        console.error('Fehler beim Laden der Logs:', error);
    }
}

// ============================================================================
// CHARTS
// ============================================================================

function initCharts() {
    // Performance Chart (Line Chart)
    const perfCtx = document.getElementById('performance-chart').getContext('2d');
    performanceChart = new Chart(perfCtx, {
        type: 'line',
        data: {
            labels: ['Tag 1', 'Tag 2', 'Tag 3', 'Tag 4', 'Tag 5', 'Tag 6', 'Tag 7'],
            datasets: [{
                label: 'PnL (SOL)',
                data: [0, 0.005, 0.012, 0.008, 0.015, 0.020, 0.025],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                y: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            }
        }
    });
    
    // Win/Loss Chart (Doughnut)
    const wlCtx = document.getElementById('winloss-chart').getContext('2d');
    winlossChart = new Chart(wlCtx, {
        type: 'doughnut',
        data: {
            labels: ['Gewinn', 'Verlust'],
            datasets: [{
                data: [65, 35],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            }
        }
    });
}

function updateCharts(stats) {
    // Update Win/Loss Chart
    if (winlossChart && stats.successful_trades !== undefined) {
        winlossChart.data.datasets[0].data = [
            stats.successful_trades || 0,
            stats.failed_trades || 0
        ];
        winlossChart.update();
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function setMetricColor(elementId, value) {
    const element = document.getElementById(elementId);
    if (value < 70) {
        element.style.color = 'var(--success-color)';
    } else if (value < 85) {
        element.style.color = 'var(--warning-color)';
    } else {
        element.style.color = 'var(--danger-color)';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

console.log('MEMERO Dashboard JavaScript geladen ✓');

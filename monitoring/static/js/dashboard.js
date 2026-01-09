/**
 * MEMERO Dashboard JavaScript
 * Lädt Daten von API-Endpunkten und aktualisiert das Dashboard
 */

// Charts
let performanceChart = null;
let winlossChart = null;

// Auto-Refresh Interval (10 Sekunden)
const REFRESH_INTERVAL = 10000;

// Trade Interval (300 Sekunden = 5 Minuten)
const TRADE_INTERVAL = 300;
let lastTradeTime = null;
let countdownInterval = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('MEMERO Dashboard geladen');
    
    // Initiale Daten laden
    loadAllData();
    
    // Charts initialisieren
    initCharts();
    
    // Uhr starten
    startLiveClock();
    
    // Countdown starten
    startTradeCountdown();
    
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
    loadPositions();  // NEU: Positionen laden
    loadLogs();
    loadBotStatus();  // NEU: Bot-Status laden
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
        
        // Update Countdown mit Bot-Status
        updateCountdownFromBotStatus(botStatus);
        
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

async function loadPositions() {
    try {
        const response = await fetch('/api/positions');
        const data = await response.json();
        
        const container = document.getElementById('positions-container');
        
        if (!container) {
            // Container noch nicht im HTML, erstmal überspringen
            return;
        }
        
        if (data.positions.length === 0) {
            container.innerHTML = '<div class="no-positions">Keine offenen Positionen</div>';
            return;
        }
        
        container.innerHTML = '';
        
        data.positions.forEach(pos => {
            const card = document.createElement('div');
            card.className = 'position-card';
            
            const pnlClass = pos.pnl_percent >= 0 ? 'positive' : 'negative';
            const pnlSign = pos.pnl_percent >= 0 ? '+' : '';
            
            card.innerHTML = `
                <div class="position-header">
                    <h4>${pos.symbol}</h4>
                    <span class="pnl-badge ${pnlClass}">${pnlSign}${pos.pnl_percent.toFixed(2)}%</span>
                </div>
                <div class="position-details">
                    <div class="position-row">
                        <span class="label">Entry:</span>
                        <span class="value">${pos.entry_price.toFixed(6)} SOL</span>
                    </div>
                    <div class="position-row">
                        <span class="label">Current:</span>
                        <span class="value">${pos.current_price.toFixed(6)} SOL</span>
                    </div>
                    <div class="position-row">
                        <span class="label">Amount:</span>
                        <span class="value">${pos.amount_tokens.toFixed(2)} Tokens</span>
                    </div>
                    <div class="position-row">
                        <span class="label">CA:</span>
                        <span class="value ca-text" title="${pos.token_address}">
                            ${pos.token_address.substring(0, 8)}...
                            <button class="copy-btn" onclick="copyToClipboard('${pos.token_address}')">📋</button>
                        </span>
                    </div>
                </div>
            `;
            
            container.appendChild(card);
        });
        
    } catch (error) {
        console.error('Fehler beim Laden der Positionen:', error);
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
            labels: ['Gewinn', 'Verlust', 'Trade Failed'],
            datasets: [{
                data: [0, 0, 0],  // Wird von updateCharts() aktualisiert
                backgroundColor: [
                    '#10b981',  // Grün für Gewinn
                    '#ef4444',  // Rot für Verlust
                    '#6b7280'   // Grau für Failed
                ],
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
    // Update Win/Loss/Failed Chart mit echten Daten
    if (winlossChart) {
        // Nutze wins/losses/failed_trades aus echten Trade-Daten
        winlossChart.data.datasets[0].data = [
            stats.wins || 0,           // Gewinn-Trades
            stats.loss_trades || 0,     // Verlust-Trades
            stats.failed_trades || 0    // Technisch fehlgeschlagen
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

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Visuelles Feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Fehler beim Kopieren:', err);
        alert('Fehler beim Kopieren in Zwischenablage');
    });
}

// ============================================================================
// BOT CONTROL
// ============================================================================

let currentBotAction = null;

async function loadBotStatus() {
    try {
        const response = await fetch('/api/bot/status');
        const data = await response.json();
        
        const dot = document.getElementById('bot-control-dot');
        const status = document.getElementById('bot-control-status');
        const startBtn = document.getElementById('btn-start-bot');
        const stopBtn = document.getElementById('btn-stop-bot');
        
        if (data.is_running) {
            dot.textContent = '🟢';
            
            // Erweiterte Status-Info mit Uptime und Memory
            let statusText = `Status: Läuft (PID: ${data.pid})`;
            if (data.uptime_formatted) {
                statusText += ` | Uptime: ${data.uptime_formatted}`;
            }
            if (data.memory_mb) {
                statusText += ` | RAM: ${data.memory_mb} MB`;
            }
            if (data.last_activity) {
                statusText += ` | Letzter Scan: ${data.last_activity}`;
            }
            
            status.textContent = statusText;
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            dot.textContent = '🔴';
            status.textContent = 'Status: Gestoppt';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
        
        // Timer Status
        const timerStatus = document.getElementById('timer-status');
        if (data.timer && data.timer.timer_active) {
            timerStatus.textContent = `⏰ Timer aktiv: ${data.timer.remaining_minutes} Min verbleibend`;
            timerStatus.style.color = '#f59e0b';
        } else {
            timerStatus.textContent = 'Kein Timer aktiv';
            timerStatus.style.color = 'var(--text-muted)';
        }
        
        // Auto-Stopped Notification
        if (data.timer && data.timer.auto_stopped) {
            alert('⏰ Timer abgelaufen - Bot wurde automatisch gestoppt!');
        }
        
    } catch (error) {
        console.error('Fehler beim Laden des Bot-Status:', error);
    }
}

function showBotControlModal(action) {
    currentBotAction = action;
    const modal = document.getElementById('bot-control-modal');
    const title = document.getElementById('modal-title');
    const desc = document.getElementById('modal-description');
    const passwordInput = document.getElementById('bot-control-password');
    
    passwordInput.value = '';
    document.getElementById('modal-error').textContent = '';
    
    if (action === 'start') {
        title.textContent = '▶️ Bot starten';
        desc.textContent = 'Bitte gib das Bot-Control-Passwort ein um den Bot zu starten:';
    } else if (action === 'stop') {
        title.textContent = '⏹️ Bot stoppen';
        desc.textContent = 'Bitte gib das Bot-Control-Passwort ein um den Bot zu stoppen:';
    } else if (action === 'timer') {
        title.textContent = '⏰ Timer setzen';
        desc.textContent = 'Bitte gib das Bot-Control-Passwort ein um den Timer zu setzen:';
    }
    
    modal.style.display = 'flex';
    passwordInput.focus();
}

function closeBotControlModal() {
    document.getElementById('bot-control-modal').style.display = 'none';
    currentBotAction = null;
}

async function executeBotControl() {
    const password = document.getElementById('bot-control-password').value;
    const errorEl = document.getElementById('modal-error');
    const confirmBtn = document.getElementById('modal-confirm');
    
    if (!password) {
        errorEl.textContent = 'Bitte Passwort eingeben!';
        return;
    }
    
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Wird ausgeführt...';
    
    try {
        let endpoint = '';
        let body = { password };
        
        if (currentBotAction === 'start') {
            endpoint = '/api/bot/start';
        } else if (currentBotAction === 'stop') {
            endpoint = '/api/bot/stop';
        } else if (currentBotAction === 'timer') {
            const minutes = parseInt(document.getElementById('timer-select').value);
            endpoint = '/api/bot/timer';
            body.minutes = minutes;
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            closeBotControlModal();
            loadBotStatus();  // Aktualisiere Status
        } else {
            errorEl.textContent = '❌ ' + data.message;
        }
        
    } catch (error) {
        errorEl.textContent = '❌ Fehler: ' + error.message;
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Bestätigen';
    }
}

// Enter-Taste im Modal
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && document.getElementById('bot-control-modal').style.display === 'flex') {
        executeBotControl();
    }
});

// ============================================================================
// LIVE CLOCK & COUNTDOWN
// ============================================================================

function startLiveClock() {
    function updateClock() {
        const now = new Date();
        
        // MEZ (UTC+1) bzw. MESZ (UTC+2)
        const options = {
            timeZone: 'Europe/Berlin',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        
        const timeString = now.toLocaleTimeString('de-DE', options);
        document.getElementById('live-clock').textContent = timeString;
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

function startTradeCountdown() {
    // Countdown alle Sekunde aktualisieren
    countdownInterval = setInterval(updateCountdown, 1000);
    updateCountdown();
}

function updateCountdown() {
    // Hole letzten Trade-Zeitstempel vom Bot Status
    if (!lastTradeTime) {
        // Fallback: Countdown von TRADE_INTERVAL starten
        const now = Math.floor(Date.now() / 1000);
        const elapsed = now % TRADE_INTERVAL;
        const remaining = TRADE_INTERVAL - elapsed;
        displayCountdown(remaining);
        return;
    }
    
    const now = Math.floor(Date.now() / 1000);
    const elapsed = now - lastTradeTime;
    const remaining = Math.max(0, TRADE_INTERVAL - elapsed);
    
    displayCountdown(remaining);
    
    // Wenn Countdown abgelaufen, auf nächsten Zyklus warten
    if (remaining === 0) {
        lastTradeTime = now;
    }
}

function displayCountdown(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    const timeString = `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    
    const countdownEl = document.getElementById('trade-countdown');
    countdownEl.textContent = timeString;
    
    // Farbwechsel bei wenig Zeit
    if (seconds < 30) {
        countdownEl.style.color = '#ef4444';  // Rot
    } else if (seconds < 60) {
        countdownEl.style.color = '#f59e0b';  // Orange
    } else {
        countdownEl.style.color = '#f59e0b';  // Standard Orange
    }
}

// Countdown-Zeit aus Bot-Status aktualisieren
function updateCountdownFromBotStatus(botStatus) {
    if (botStatus && botStatus.last_activity) {
        // Parse last_activity timestamp von get_bot_status()
        // Format: "2024-01-15 14:30:45"
        try {
            // Entferne mögliche Timezone-Suffixe
            const cleanTimestamp = botStatus.last_activity.replace(' MEZ', '').replace(' CET', '').replace(' CEST', '');
            const activityTime = new Date(cleanTimestamp);
            
            if (!isNaN(activityTime.getTime())) {
                lastTradeTime = Math.floor(activityTime.getTime() / 1000);
                console.log('Countdown synchronized with last_activity:', cleanTimestamp);
            }
        } catch (e) {
            console.warn('Could not parse last_activity:', e);
        }
    }
}

console.log('MEMERO Dashboard JavaScript geladen ✓');

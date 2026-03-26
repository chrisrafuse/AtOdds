/**
 * AtOdds Web Frontend - Vanilla JavaScript
 * Compatible: Chrome, Edge, Firefox
 */

// API Configuration
const API_BASE_URL = window.location.origin;
const API_VERSION = '/api/v1';

// State Management
const state = {
    currentData: null,
    currentResults: null,
    currentFilter: 'all',
    apiOnline: false,
    chatSessionId: null,
    llmProvider: 'mock',
    briefingText: ''
};

// DOM Elements
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Upload
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    browseBtn: document.getElementById('browseBtn'),
    fileInfo: document.getElementById('fileInfo'),
    fileName: document.getElementById('fileName'),
    clearFileBtn: document.getElementById('clearFileBtn'),

    // Sample
    loadSampleBtn: document.getElementById('loadSampleBtn'),

    // Paste
    jsonInput: document.getElementById('jsonInput'),
    validateJsonBtn: document.getElementById('validateJsonBtn'),

    // Actions
    analyzeBtn: document.getElementById('analyzeBtn'),
    resetBtn: document.getElementById('resetBtn'),

    // Results
    resultsSection: document.getElementById('resultsSection'),
    statsGrid: document.getElementById('statsGrid'),
    totalFindings: document.getElementById('totalFindings'),
    arbitrageCount: document.getElementById('arbitrageCount'),
    valueEdgeCount: document.getElementById('valueEdgeCount'),
    outlierCount: document.getElementById('outlierCount'),
    findingsList: document.getElementById('findingsList'),

    // Briefing
    briefingSection: document.getElementById('briefingSection'),
    briefingContent: document.getElementById('briefingContent'),
    generateBriefingBtn: document.getElementById('generateBriefingBtn'),
    copyBriefingBtn: document.getElementById('copyBriefingBtn'),
    downloadResultsBtn: document.getElementById('downloadResultsBtn'),

    // Filter
    filterBtns: document.querySelectorAll('.filter-btn'),

    // Status
    apiStatus: document.getElementById('apiStatus'),
    apiDocsBtn: document.getElementById('apiDocsBtn'),

    // Loading
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer'),

    // Rankings
    rankingsSection: document.getElementById('rankingsSection'),
    rankingsBody: document.getElementById('rankingsBody'),

    // Provider badge
    providerBadge: document.getElementById('providerBadge'),

    // Trace
    tracePanel: document.getElementById('tracePanel'),
    traceCount: document.getElementById('traceCount'),
    toolTrace: document.getElementById('toolTrace'),

    // LLM Summary
    llmSummary: document.getElementById('llmSummary'),
    llmSummaryContent: document.getElementById('llmSummaryContent'),

    // Chat
    chatSection: document.getElementById('chatSection'),
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    chatSendBtn: document.getElementById('chatSendBtn'),
    chatProviderBadge: document.getElementById('chatProviderBadge'),
    quickQuestions: document.querySelectorAll('.quick-q')
};

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkApiStatus();
});

// Event Listeners
function initializeEventListeners() {
    // Tab switching
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // File upload
    elements.browseBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.clearFileBtn.addEventListener('click', clearFile);

    // Drag and drop
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleFileDrop);
    elements.uploadArea.addEventListener('click', () => elements.fileInput.click());

    // Sample data
    elements.loadSampleBtn.addEventListener('click', loadSampleData);

    // JSON validation
    elements.validateJsonBtn.addEventListener('click', validateJson);

    // Actions
    elements.analyzeBtn.addEventListener('click', runAnalysis);
    elements.resetBtn.addEventListener('click', resetApp);

    // Results
    elements.generateBriefingBtn.addEventListener('click', generateBriefing);
    elements.copyBriefingBtn.addEventListener('click', copyBriefing);
    elements.downloadResultsBtn.addEventListener('click', downloadResults);

    // Filter
    elements.filterBtns.forEach(btn => {
        btn.addEventListener('click', () => filterFindings(btn.dataset.filter));
    });

    // API Docs
    elements.apiDocsBtn.addEventListener('click', () => {
        window.open('/docs', '_blank');
    });

    // Chat
    elements.chatSendBtn.addEventListener('click', sendChatMessage);
    elements.chatInput.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(); }
    });
    elements.chatInput.addEventListener('input', () => {
        elements.chatSendBtn.disabled = !elements.chatInput.value.trim() || !state.chatSessionId;
    });
    elements.quickQuestions.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.chatInput.value = btn.dataset.q;
            sendChatMessage();
        });
    });
}

// Tab Switching
function switchTab(tabName) {
    elements.tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === tabName + '-tab');
    });

    resetDataInput();
}

// API Status Check
async function checkApiStatus() {
    try {
        const response = await fetch(API_BASE_URL + '/health');
        const data = await response.json();

        if (data.CR_status === 'healthy') {
            updateApiStatus(true);
        } else {
            updateApiStatus(false);
        }
    } catch (error) {
        updateApiStatus(false);
    }
}

function updateApiStatus(online) {
    state.apiOnline = online;
    const statusDot = elements.apiStatus.querySelector('.status-dot');
    const statusText = elements.apiStatus.querySelector('.status-text');

    if (online) {
        statusDot.classList.add('online');
        statusText.textContent = 'API Online';
    } else {
        statusDot.classList.remove('online');
        statusText.textContent = 'API Offline';
    }
}

// File Handling
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    elements.uploadArea.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
}

function handleFileDrop(event) {
    event.preventDefault();
    elements.uploadArea.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/json') {
        processFile(file);
    } else {
        showToast('Please drop a valid JSON file', 'error');
    }
}

function processFile(file) {
    const reader = new FileReader();

    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            state.currentData = data;

            elements.fileName.textContent = file.name;
            elements.fileInfo.style.display = 'flex';
            elements.uploadArea.style.display = 'none';
            elements.analyzeBtn.disabled = false;

            showToast('File loaded successfully', 'success');
        } catch (error) {
            showToast('Invalid JSON file', 'error');
        }
    };

    reader.readAsText(file);
}

function clearFile() {
    elements.fileInput.value = '';
    elements.fileInfo.style.display = 'none';
    elements.uploadArea.style.display = 'block';
    resetDataInput();
}

// Sample Data
async function loadSampleData() {
    showLoading(true);

    try {
        const response = await fetch(API_BASE_URL + API_VERSION + '/data/sample');
        const result = await response.json();

        if (result.CR_status === 'success') {
            state.currentData = result.CR_data.CR_snapshot;
            elements.analyzeBtn.disabled = false;
            showToast('Sample data loaded successfully', 'success');
        } else {
            showToast('Failed to load sample data', 'error');
        }
    } catch (error) {
        showToast('Error loading sample data: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// JSON Validation
function validateJson() {
    const jsonText = elements.jsonInput.value.trim();

    if (!jsonText) {
        showToast('Please enter JSON data', 'error');
        return;
    }

    try {
        const data = JSON.parse(jsonText);
        state.currentData = data;
        elements.analyzeBtn.disabled = false;
        showToast('JSON is valid', 'success');
    } catch (error) {
        showToast('Invalid JSON: ' + error.message, 'error');
    }
}

// Analysis
async function runAnalysis() {
    if (!state.currentData) {
        showToast('Please load data first', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(API_BASE_URL + API_VERSION + '/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ CR_snapshot: state.currentData })
        });

        const result = await response.json();

        if (result.CR_status === 'success') {
            state.currentResults = result.CR_data;
            state.llmProvider = result.CR_data.CR_llm_provider || 'mock';
            displayResults(result.CR_data);
            showProviderBadge(state.llmProvider);
            showToast('Analysis completed successfully', 'success');
        } else {
            showToast('Analysis failed: ' + (result.CR_error?.CR_message || 'Unknown error'), 'error');
        }
    } catch (error) {
        showToast('Error running analysis: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Display Results
function displayResults(data) {
    const findings = data.CR_findings || [];

    // Update stats
    elements.totalFindings.textContent = findings.length;
    elements.arbitrageCount.textContent = findings.filter(f => f.CR_type === 'arbitrage').length;
    elements.valueEdgeCount.textContent = findings.filter(f => f.CR_type === 'value_edge').length;
    elements.outlierCount.textContent = findings.filter(f => f.CR_type === 'outlier').length;

    // Display findings
    displayFindings(findings);

    // Render sportsbook rankings if present
    const rankings = data.CR_sportsbook_rankings || [];
    if (rankings.length > 0) {
        renderSportsbookRankings(rankings);
    }

    // Render tool trace if present
    const trace = data.CR_tool_trace || [];
    if (trace.length > 0) {
        renderToolTrace(trace);
    }

    // Render LLM summary if present
    if (data.CR_llm_summary) {
        renderLLMSummary(data.CR_llm_summary);
    }

    // Show results section
    elements.resultsSection.style.display = 'block';
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderToolTrace(trace) {
    elements.traceCount.textContent = trace.length;
    elements.tracePanel.style.display = 'block';
    elements.toolTrace.innerHTML = '';

    trace.forEach((tc, i) => {
        const card = document.createElement('div');
        card.className = 'trace-card';
        const hasError = !!tc.CR_error;
        const resultCount = tc.CR_result && tc.CR_result.CR_count !== undefined
            ? ` → ${tc.CR_result.CR_count} result(s)` : '';
        card.innerHTML = `
            <div class="trace-header ${hasError ? 'trace-error' : 'trace-ok'}">
                <span class="trace-index">#${i + 1}</span>
                <span class="trace-tool-name">${tc.CR_tool_name}</span>
                <span class="trace-result-badge">${hasError ? '✕ Error' : '✓' + resultCount}</span>
            </div>
            ${tc.CR_error ? `<div class="trace-error-msg">${tc.CR_error}</div>` : ''}
        `;
        elements.toolTrace.appendChild(card);
    });
}

function renderSportsbookRankings(rankings) {
    elements.rankingsSection.style.display = 'block';
    elements.rankingsBody.innerHTML = '';
    rankings.forEach(r => {
        const tr = document.createElement('tr');
        const verdictClass = r.CR_verdict === 'Recommended' ? 'verdict-recommended'
            : r.CR_verdict === 'Avoid' ? 'verdict-avoid' : 'verdict-average';
        tr.innerHTML = `
            <td>${r.CR_rank}</td>
            <td><strong>${r.CR_bookmaker}</strong></td>
            <td>${r.CR_avg_vig_pct}</td>
            <td>${r.CR_best_line_pct}</td>
            <td>${r.CR_stale_count}</td>
            <td>${r.CR_outlier_count}</td>
            <td>${r.CR_quality_score}</td>
            <td><span class="verdict-badge ${verdictClass}">${r.CR_verdict}</span></td>
        `;
        elements.rankingsBody.appendChild(tr);
    });
}

function renderLLMSummary(summary) {
    elements.llmSummary.style.display = 'block';
    elements.llmSummaryContent.innerHTML = summary
        .replace(/^## (.+)$/gm, '<h4>$1</h4>')
        .replace(/^\*\*(.+?)\*\*/gm, '<strong>$1</strong>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/\n/g, '<br>');
}

function showProviderBadge(provider) {
    const labels = { openai: 'OpenAI', anthropic: 'Claude', gemini: 'Gemini', mock: 'Mock', fallback: 'Fallback' };
    const colors = { openai: '#10a37f', anthropic: '#d97706', gemini: '#4285f4', mock: '#6b7280', fallback: '#ef4444' };
    const label = labels[provider] || provider;
    const color = colors[provider] || '#6b7280';

    [elements.providerBadge, elements.chatProviderBadge].forEach(el => {
        if (el) {
            el.textContent = '🤖 ' + label;
            el.style.background = color;
            el.style.display = 'inline-block';
        }
    });
}

function displayFindings(findings) {
    elements.findingsList.innerHTML = '';

    if (findings.length === 0) {
        elements.findingsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No findings to display</p>';
        return;
    }

    findings.forEach(finding => {
        const card = createFindingCard(finding);
        elements.findingsList.appendChild(card);
    });
}

function createFindingCard(finding) {
    const card = document.createElement('div');
    card.className = 'finding-card ' + finding.CR_type;
    card.dataset.type = finding.CR_type;

    const typeLabel = finding.CR_type.replace('_', ' ').toUpperCase();
    const confidence = ((finding.CR_confidence || 0) * 100).toFixed(1);

    const mathProof = finding.CR_math_proof;
    const mathHtml = mathProof ? `
        <details class="math-proof">
            <summary>Show math</summary>
            <code class="math-formula">${mathProof.CR_formula || ''}</code>
        </details>
    ` : '';

    card.innerHTML = `
        <div class="finding-header">
            <span class="finding-type ${finding.CR_type}">${typeLabel}</span>
            <span class="finding-confidence">Confidence: ${confidence}%</span>
        </div>
        <div class="finding-description">${finding.CR_description || 'No description available'}</div>
        <div class="finding-details">
            <div class="detail-item">
                <span class="detail-label">Event ID</span>
                <span class="detail-value">${finding.CR_event_id || 'N/A'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Market</span>
                <span class="detail-value">${finding.CR_market_name || 'N/A'}</span>
            </div>
            ${finding.CR_bookmakers ? `
            <div class="detail-item">
                <span class="detail-label">Bookmakers</span>
                <span class="detail-value">${finding.CR_bookmakers.join(', ')}</span>
            </div>
            ` : ''}
            ${finding.CR_profit_margin ? `
            <div class="detail-item">
                <span class="detail-label">Profit Margin</span>
                <span class="detail-value">${(finding.CR_profit_margin * 100).toFixed(2)}%</span>
            </div>
            ` : ''}
        </div>
        ${mathHtml}
    `;

    return card;
}

// Filter Findings
function filterFindings(filter) {
    state.currentFilter = filter;

    elements.filterBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });

    const cards = elements.findingsList.querySelectorAll('.finding-card');

    cards.forEach(card => {
        if (filter === 'all' || card.dataset.type === filter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Briefing
async function generateBriefing() {
    if (!state.currentResults) {
        showToast('No results to generate briefing', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(API_BASE_URL + API_VERSION + '/report/briefing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                CR_findings: state.currentResults.CR_findings,
                CR_snapshot: state.currentData,
                CR_sportsbook_rankings: state.currentResults.CR_sportsbook_rankings || [],
                CR_format: 'text'
            })
        });

        const result = await response.json();

        if (result.CR_status === 'success') {
            const briefingText = result.CR_data.CR_briefing || '';
            state.briefingText = briefingText;
            elements.briefingContent.textContent = briefingText;
            elements.briefingSection.style.display = 'block';
            elements.briefingSection.scrollIntoView({ behavior: 'smooth' });
            showToast('Briefing generated successfully', 'success');
            // Init chat session now that we have the briefing
            initChatSession();
        } else {
            showToast('Failed to generate briefing', 'error');
        }
    } catch (error) {
        showToast('Error generating briefing: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function copyBriefing() {
    const text = elements.briefingContent.textContent;

    navigator.clipboard.writeText(text).then(() => {
        showToast('Briefing copied to clipboard', 'success');
    }).catch(() => {
        showToast('Failed to copy briefing', 'error');
    });
}

function downloadResults() {
    if (!state.currentResults) {
        showToast('No results to download', 'error');
        return;
    }

    const dataStr = JSON.stringify(state.currentResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'atodds-results-' + new Date().toISOString().split('T')[0] + '.json';
    link.click();

    URL.revokeObjectURL(url);
    showToast('Results downloaded', 'success');
}

// Chat
async function initChatSession() {
    if (!state.currentResults) return;
    try {
        const response = await fetch(API_BASE_URL + API_VERSION + '/chat/session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                CR_snapshot: state.currentData,
                CR_findings: state.currentResults.CR_findings || [],
                CR_briefing_text: state.briefingText
            })
        });
        const result = await response.json();
        if (result.CR_status === 'success') {
            state.chatSessionId = result.CR_data.CR_session_id;
            elements.chatSection.style.display = 'block';
            elements.chatSendBtn.disabled = true;
            elements.chatInput.disabled = false;
            elements.chatMessages.innerHTML = '';
            appendChatBubble('agent',
                '👋 I have reviewed the analysis briefing. Ask me anything about the findings, '
                + 'specific games, bookmakers, or what actions to take.', []);
            elements.chatSection.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (e) {
        // Chat init failed silently — don't block the briefing display
    }
}

async function sendChatMessage() {
    const question = elements.chatInput.value.trim();
    if (!question || !state.chatSessionId) return;

    elements.chatInput.value = '';
    elements.chatSendBtn.disabled = true;
    appendChatBubble('user', question, []);

    try {
        const response = await fetch(API_BASE_URL + API_VERSION + '/chat/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ CR_session_id: state.chatSessionId, CR_question: question })
        });
        const result = await response.json();
        if (result.CR_status === 'success') {
            appendChatBubble('agent',
                result.CR_data.CR_answer,
                result.CR_data.CR_tool_trace || []);
        } else {
            appendChatBubble('agent', '⚠️ Sorry, I could not answer that question right now.', []);
        }
    } catch (e) {
        appendChatBubble('agent', '⚠️ Connection error. Please try again.', []);
    }
}

function appendChatBubble(role, text, toolTrace) {
    const wrap = document.createElement('div');
    wrap.className = `chat-bubble-wrap ${role}`;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-bubble-${role}`;
    bubble.innerHTML = text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/^## (.+)$/gm, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    wrap.appendChild(bubble);

    if (toolTrace && toolTrace.length > 0) {
        const traceEl = document.createElement('details');
        traceEl.className = 'chat-trace';
        traceEl.innerHTML = `<summary>${toolTrace.length} tool call(s)</summary>`;
        toolTrace.forEach(tc => {
            const item = document.createElement('span');
            item.className = 'chat-trace-item';
            item.textContent = tc.CR_tool_name;
            traceEl.appendChild(item);
        });
        wrap.appendChild(traceEl);
    }

    elements.chatMessages.appendChild(wrap);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

// Reset
function resetApp() {
    state.currentData = null;
    state.currentResults = null;
    state.currentFilter = 'all';
    state.chatSessionId = null;
    state.briefingText = '';

    elements.fileInput.value = '';
    elements.jsonInput.value = '';
    elements.fileInfo.style.display = 'none';
    elements.uploadArea.style.display = 'block';
    elements.analyzeBtn.disabled = true;
    elements.resultsSection.style.display = 'none';
    elements.briefingSection.style.display = 'none';
    elements.chatSection.style.display = 'none';
    elements.tracePanel.style.display = 'none';
    elements.llmSummary.style.display = 'none';
    elements.rankingsSection.style.display = 'none';
    elements.rankingsBody.innerHTML = '';
    elements.providerBadge.style.display = 'none';
    elements.chatMessages.innerHTML = '';

    showToast('App reset', 'info');
}

function resetDataInput() {
    state.currentData = null;
    elements.analyzeBtn.disabled = true;
}

// UI Helpers
function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;

    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close">✕</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

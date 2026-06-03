const API = '/api';
let currentView = 'personal';
let currentPage = 1;
let currentUserId = null;

async function init() {
    const user = await api('/users', 'POST', { username: 'default' });
    currentUserId = user.id;
    await loadHoldings();
    loadNews();
}

async function api(path, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + path, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

function switchView(view) {
    currentView = view;
    currentPage = 1;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`[data-view="${view}"]`).classList.add('active');

    const stockSelect = document.getElementById('stockSelect');
    const titles = { personal: 'Personal News', stock: 'Per-Stock News', market: 'Market News' };
    document.getElementById('viewTitle').textContent = titles[view];
    stockSelect.style.display = view === 'stock' ? 'block' : 'none';

    if (view === 'stock') populateStockSelect();
    loadNews();
}

function populateStockSelect() {
    const select = document.getElementById('stockSelect');
    const current = select.value;
    select.innerHTML = '<option value="">Select stock...</option>';
    document.querySelectorAll('.holding-item').forEach(el => {
        const ticker = el.querySelector('.holding-ticker').textContent;
        const opt = document.createElement('option');
        opt.value = ticker;
        opt.textContent = ticker;
        if (ticker === current) opt.selected = true;
        select.appendChild(opt);
    });
}

async function loadHoldings() {
    const holdings = await api(`/users/${currentUserId}/holdings`);
    const container = document.getElementById('holdingsList');
    if (!holdings.length) {
        container.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;padding:0.5rem">No holdings yet</div>';
        return;
    }
    container.innerHTML = holdings.map(h => `
        <div class="holding-item" onclick="viewStock('${h.ticker}')">
            <div>
                <div class="holding-ticker">${h.ticker}</div>
                <div class="holding-name">${h.name || ''}</div>
            </div>
            <button class="btn btn-danger btn-sm" onclick="event.stopPropagation();removeHolding(${h.id})">x</button>
        </div>
    `).join('');
}

async function searchTickers(q) {
    const results = document.getElementById('searchResults');
    if (!q || q.length < 1) { results.style.display = 'none'; return; }
    const ticks = await api(`/tickers/search?q=${encodeURIComponent(q)}`);
    if (!ticks.length) { results.style.display = 'none'; return; }
    results.style.display = 'block';
    results.innerHTML = ticks.map(t => `
        <div class="search-result-item" onclick="addHolding('${t.ticker}','${t.name.replace(/'/g, "\\'")}')">
            <strong>${t.ticker}</strong>
            <span style="color:var(--text-muted);font-size:0.8rem">${t.name}</span>
        </div>
    `).join('');
}

async function addHolding(ticker, name) {
    try {
        await api(`/users/${currentUserId}/holdings`, 'POST', { ticker, name });
        document.getElementById('stockSearch').value = '';
        document.getElementById('searchResults').style.display = 'none';
        await loadHoldings();
        if (currentView === 'stock') populateStockSelect();
    } catch (e) {
        alert(e.message);
    }
}

async function removeHolding(id) {
    await api(`/users/${currentUserId}/holdings/${id}`, 'DELETE');
    await loadHoldings();
    if (currentView === 'stock') populateStockSelect();
}

function viewStock(ticker) {
    document.getElementById('stockSelect').value = ticker;
    switchView('stock');
}

async function loadNews() {
    const container = document.getElementById('newsContainer');
    container.innerHTML = '<div class="loading">Loading news...</div>';

    const age = document.getElementById('ageFilter').value;
    let url;

    if (currentView === 'personal') {
        url = `/news/personal/${currentUserId}?age_filter=${age}&page=${currentPage}&page_size=20`;
    } else if (currentView === 'stock') {
        const ticker = document.getElementById('stockSelect').value;
        if (!ticker) {
            container.innerHTML = '<div class="empty-state"><h3>Select a stock</h3><p>Choose a stock from the dropdown or your holdings</p></div>';
            return;
        }
        url = `/news/stock/${ticker}?age_filter=${age}&page=${currentPage}&page_size=20`;
    } else {
        url = `/news/market?age_filter=${age}&page=${currentPage}&page_size=20`;
    }

    const data = await api(url);
    renderNews(data);
}

function renderNews(data) {
    const container = document.getElementById('newsContainer');
    if (!data.items.length) {
        container.innerHTML = '<div class="empty-state"><h3>No news found</h3><p>Try adjusting your filters or adding more holdings</p></div>';
        document.getElementById('pagination').innerHTML = '';
        return;
    }

    container.innerHTML = data.items.map(item => `
        <div class="news-card">
            <div class="news-card-header">
                <a href="${item.link}" target="_blank" class="news-title">${escapeHtml(item.title)}</a>
                <div class="news-meta">
                    ${item.source ? `<span class="news-source">${escapeHtml(item.source)}</span>` : ''}
                    ${item.published_at ? `<span class="news-date">${formatDate(item.published_at)}</span>` : ''}
                </div>
            </div>
            ${item.tickers.length ? `
                <div class="ticker-badges">
                    ${item.tickers.map(t => `<span class="ticker-badge">${t}</span>`).join('')}
                </div>
            ` : ''}
            ${currentView === 'personal' && item.tickers.length ? `
                <div class="matched-tag">Matched: ${item.tickers.join(', ')}</div>
            ` : ''}
            ${item.teaser ? `<div class="news-teaser">${escapeHtml(item.teaser)}</div>` : ''}
        </div>
    `).join('');

    renderPagination(data.total, data.page, data.page_size);
}

function renderPagination(total, page, pageSize) {
    const pages = Math.ceil(total / pageSize);
    const container = document.getElementById('pagination');
    if (pages <= 1) { container.innerHTML = ''; return; }

    let html = '';
    if (page > 1) html += `<button class="btn btn-secondary btn-sm" onclick="goToPage(${page - 1})">Prev</button>`;
    for (let i = Math.max(1, page - 2); i <= Math.min(pages, page + 2); i++) {
        html += `<button class="btn ${i === page ? '' : 'btn-secondary'} btn-sm" onclick="goToPage(${i})">${i}</button>`;
    }
    if (page < pages) html += `<button class="btn btn-secondary btn-sm" onclick="goToPage(${page + 1})">Next</button>`;
    container.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadNews();
}

async function triggerIngest() {
    const btn = event.target;
    btn.textContent = 'Refreshing...';
    btn.disabled = true;
    try {
        const stats = await api('/ingest', 'POST');
        alert(`Ingested: ${stats.new} new, ${stats.duplicates} duplicates, ${stats.errors} errors`);
        loadNews();
    } finally {
        btn.textContent = 'Refresh Feeds';
        btn.disabled = false;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(iso) {
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
    if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
    return d.toLocaleDateString();
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.stock-search')) {
        document.getElementById('searchResults').style.display = 'none';
    }
});

init();

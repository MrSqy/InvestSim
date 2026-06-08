const API_BASE = '';

async function apiGet(path) {
    const resp = await fetch(`${API_BASE}${path}`);
    if (!resp.ok) throw new Error(`GET ${path} failed: ${resp.status}`);
    return resp.json();
}

async function apiPost(path, body) {
    const resp = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!resp.ok) {
        const err = await resp.text();
        throw new Error(`POST ${path} failed: ${resp.status} - ${err}`);
    }
    return resp.json();
}

const API = {
    assets: () => apiGet('/market/assets'),
    price: (symbol, type) => apiGet(`/market/price/${symbol}?asset_type=${type}`),
    buy: (body) => apiPost('/orders/buy', body),
    sell: (body) => apiPost('/orders/sell', body),
    portfolio: () => apiGet('/portfolio/'),
    history: () => apiGet('/portfolio/history'),
    balance: () => apiGet('/portfolio/balance'),
    performance: () => apiGet('/analytics/performance'),
    scenario: (body) => apiPost('/analytics/scenario', body),
    diversification: () => apiGet('/analytics/diversification'),
};

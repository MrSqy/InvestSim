async function loadDashboard() {
    try {
        const perf = await API.performance();
        const bal = await API.balance();
        document.getElementById('balance').textContent = '$' + bal.balance.toFixed(2);
        document.getElementById('portfolio-value').textContent = '$' + perf.current_value.toFixed(2);
        const retEl = document.getElementById('total-return');
        retEl.textContent = (perf.total_return >= 0 ? '+' : '') + perf.total_return.toFixed(2) + ' (' + perf.total_return_percent + '%)';
        retEl.className = perf.total_return >= 0 ? 'positive' : 'negative';
    } catch (e) {
        console.error(e);
    }
    try {
        const holdings = await API.portfolio();
        const tbody = document.querySelector('#holdings-table tbody');
        tbody.innerHTML = '';
        holdings.forEach(h => {
            const tr = document.createElement('tr');
            const pnl = h.unrealized_pnl !== null ? h.unrealized_pnl.toFixed(2) : '-';
            const pnlClass = h.unrealized_pnl === null ? '' : (h.unrealized_pnl >= 0 ? 'positive' : 'negative');
            tr.innerHTML = `<td>${h.asset_symbol}</td><td>${h.asset_type}</td><td>${h.total_quantity}</td><td>$${h.avg_cost_basis.toFixed(2)}</td><td>$${h.current_price !== null ? h.current_price.toFixed(2) : '-'}</td><td class="${pnlClass}">${pnl}</td>`;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

async function loadAssets() {
    const assets = await API.assets();
    const select = document.getElementById('trade-asset');
    assets.forEach(a => {
        const opt = document.createElement('option');
        opt.value = JSON.stringify({symbol: a.symbol, type: a.asset_type});
        opt.textContent = `${a.symbol} (${a.asset_type})`;
        select.appendChild(opt);
    });
}

document.getElementById('btn-buy').addEventListener('click', async () => {
    const sel = document.getElementById('trade-asset').value;
    const qty = parseFloat(document.getElementById('trade-qty').value);
    if (!sel || !qty) return;
    const asset = JSON.parse(sel);
    try {
        await API.buy({asset_symbol: asset.symbol, asset_type: asset.type, quantity: qty});
        document.getElementById('trade-msg').textContent = 'Alım başarılı!';
        document.getElementById('trade-msg').className = 'positive';
        loadDashboard();
    } catch (e) {
        document.getElementById('trade-msg').textContent = e.message;
        document.getElementById('trade-msg').className = 'negative';
    }
});

document.getElementById('btn-sell').addEventListener('click', async () => {
    const sel = document.getElementById('trade-asset').value;
    const qty = parseFloat(document.getElementById('trade-qty').value);
    if (!sel || !qty) return;
    const asset = JSON.parse(sel);
    try {
        await API.sell({asset_symbol: asset.symbol, asset_type: asset.type, quantity: qty});
        document.getElementById('trade-msg').textContent = 'Satım başarılı!';
        document.getElementById('trade-msg').className = 'positive';
        loadDashboard();
    } catch (e) {
        document.getElementById('trade-msg').textContent = e.message;
        document.getElementById('trade-msg').className = 'negative';
    }
});

loadAssets();
loadDashboard();
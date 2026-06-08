async function loadPortfolio() {
    const holdings = await API.portfolio();
    const tbody = document.querySelector('#portfolio-table tbody');
    tbody.innerHTML = '';
    holdings.forEach(h => {
        const tr = document.createElement('tr');
        const pnl = h.unrealized_pnl !== null ? h.unrealized_pnl.toFixed(2) : '-';
        const pnlClass = h.unrealized_pnl === null ? '' : (h.unrealized_pnl >= 0 ? 'positive' : 'negative');
        tr.innerHTML = `<td>${h.asset_symbol}</td><td>${h.asset_type}</td><td>${h.total_quantity}</td><td>$${h.avg_cost_basis.toFixed(2)}</td><td>$${h.current_price !== null ? h.current_price.toFixed(2) : '-'}</td><td class="${pnlClass}">${pnl}</td>`;
        tbody.appendChild(tr);
    });
    const history = await API.history();
    const htbody = document.querySelector('#history-table tbody');
    htbody.innerHTML = '';
    history.forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(t.timestamp).toLocaleString()}</td><td>${t.transaction_type.toUpperCase()}</td><td>${t.asset_symbol}</td><td>${t.quantity}</td><td>$${t.price.toFixed(2)}</td><td>$${t.total_amount.toFixed(2)}</td>`;
        htbody.appendChild(tr);
    });
}
loadPortfolio();

async function loadAnalytics() {
    const perf = await API.performance();
    document.getElementById('perf-display').innerHTML = `
        <p>Yatırılan: $${perf.total_invested.toFixed(2)}</p>
        <p>Güncel Değer: $${perf.current_value.toFixed(2)}</p>
        <p>Getiri: <span class="${perf.total_return >= 0 ? 'positive' : 'negative'}">${perf.total_return.toFixed(2)} (${perf.total_return_percent}%)</span></p>
    `;
    const div = await API.diversification();
    const tbody = document.querySelector('#diversification-table tbody');
    tbody.innerHTML = '';
    div.forEach(d => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${d.asset_type}</td><td>$${d.value}</td><td>${d.percentage}%</td>`;
        tbody.appendChild(tr);
    });
}

async function loadAssets() {
    const assets = await API.assets();
    const select = document.getElementById('scenario-asset');
    assets.forEach(a => {
        const opt = document.createElement('option');
        opt.value = JSON.stringify({symbol: a.symbol, type: a.asset_type});
        opt.textContent = `${a.symbol} (${a.asset_type})`;
        select.appendChild(opt);
    });
}

document.getElementById('btn-scenario').addEventListener('click', async () => {
    const sel = document.getElementById('scenario-asset').value;
    const date = document.getElementById('scenario-date').value;
    const amount = parseFloat(document.getElementById('scenario-amount').value);
    if (!sel || !date || !amount) return;
    const asset = JSON.parse(sel);
    try {
        const result = await API.scenario({
            name: `${asset.symbol} senaryo`,
            asset_symbol: asset.symbol,
            asset_type: asset.type,
            hypothetical_date: date,
            hypothetical_amount: amount
        });
        const el = document.getElementById('scenario-result');
        if (result.current_price === null) {
            el.innerHTML = `<p class="negative">Fiyat verisi alınamadı.</p>`;
        } else {
            el.innerHTML = `
                <p>Güncel Fiyat: $${result.current_price.toFixed(2)}</p>
                <p>Varsayım Değeri: $${result.hypothetical_value}</p>
                <p>K/Z: <span class="${result.gain_loss === null ? '' : (result.gain_loss >= 0 ? 'positive' : 'negative')}">$${result.gain_loss} (${result.gain_loss_percent}%)</span></p>
            `;
        }
    } catch (e) {
        document.getElementById('scenario-result').textContent = e.message;
    }
});

loadAssets();
loadAnalytics();

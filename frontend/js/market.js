async function loadMarket() {
    const assets = await API.assets();
    const tbody = document.querySelector('#market-table tbody');
    tbody.innerHTML = '';
    for (const a of assets) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${a.symbol}</td><td>${a.name}</td><td>${a.asset_type}</td><td id="price-${a.symbol}">Yükleniyor...</td><td id="src-${a.symbol}">-</td>`;
        tbody.appendChild(tr);
        API.price(a.symbol, a.asset_type).then(data => {
            document.getElementById(`price-${a.symbol}`).textContent = '$' + data.price.toFixed(2);
            document.getElementById(`src-${a.symbol}`).textContent = data.source;
        }).catch(err => {
            document.getElementById(`price-${a.symbol}`).textContent = 'N/A';
            document.getElementById(`src-${a.symbol}`).textContent = 'Hata';
            console.error(`Price fetch failed for ${a.symbol}:`, err.message);
        });
    }
}
loadMarket();

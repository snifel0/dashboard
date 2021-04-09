function changeState(params) {
    window.history.replaceState({}, '', `${location.pathname}?${params}`);
    location.reload();
}
function Position(ticker, shares) {
    this.ticker = ticker;
    this.shares = shares;
}
function getPositions() {
    const urlParams = new URLSearchParams(window.location.search);
    var cash = 0;
    var positions = [];
    var count = 0;
    for (const key of urlParams.keys()) {
        if (key == "$$CASH$$") {
            cash = urlParams.get(key);
        } else {
            positions[count] = new Position(key, urlParams.get(key));
            count++;
        }
    }
    return [positions, cash];
}
function getNewQueryURI(positions, cash) {
    var new_urlParams = new URLSearchParams();
    new_urlParams
    for (var i = 0; i < positions.length; i++) {
        new_urlParams.append(positions[i].ticker, positions[i].shares.toString());
    }
    new_urlParams.append("$$CASH$$", cash.toString());
    return new_urlParams.toString();
}
function applyTransaction() {
    var [old_positions, old_cash] = getPositions();
    var ticker = document.getElementById("ticker").value;
    var price_per_share = document.getElementById("price-per-share").value;
    var commission = parseFloat(document.getElementById("commission").value);
    if (document.getElementById("buy").checked) {
        var shares = document.getElementById("shares").value;
    } else if (document.getElementById("sell").checked) {
        var shares = - document.getElementById("shares").value;
    } else {
        return;
    }
    cost = shares * price_per_share;
    var new_cash = old_cash - cost - commission;
    var old_shares = 0;
    var new_positions = [];
    var new_i = 0;
    for (let i = 0; i < old_positions.length; i++) {
        if (old_positions[i].ticker == ticker) {
            old_shares += old_positions[i].shares;
        } else {
            new_positions[new_i] = old_positions[i];
            new_i++;
        }
    }
    var new_shares = parseInt(old_shares) + parseInt(shares);
    if (new_shares != 0) {
        new_positions[new_i] = new Position(ticker, new_shares);
    }
    changeState(getNewQueryURI(new_positions, new_cash));
}
function applyCashInOut() {
    var [old_positions, old_cash] = getPositions();
    if (document.getElementById("deposit").checked) {
        var amount = document.getElementById("amount").value;
    } else if (document.getElementById("withdrawal").checked) {
        var amount = - document.getElementById("amount").value;
    } else {
        return;
    }
    var new_cash = parseFloat(old_cash) + parseFloat(amount);
    changeState(getNewQueryURI(old_positions, new_cash.toString()));
}
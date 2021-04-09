var usd_formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2
});
var int_formatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0
});

var usds = document.getElementsByClassName("usd");
for (var i = 0; i < usds.length; i++) {
    var amount = parseFloat(usds.item(i).innerText);
    usds.item(i).innerText = usd_formatter.format(amount)
}
var ints = document.getElementsByClassName("int");
for (var i = 0; i < ints.length; i++) {
    var amount = parseFloat(ints.item(i).innerText);
    ints.item(i).innerText = int_formatter.format(amount)
}
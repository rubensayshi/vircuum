/**
 * @jsx React.DOM
 */


var inherit = function(from, construct) {
    var cls = construct;
    cls.prototype = new from();

    return cls;
};


VirCu.Currency = function(value) {
    var self = this;
    self.value = value;
};

VirCu.Currency.prototype.display = function() {
    return this.value + " " + this.symbol;
}


VirCu.Currency.GHS = inherit(VirCu.Currency, function(value) {
    VirCu.Currency.call(this, value);

    this.symbol = 'GHS';
});


VirCu.Currency.BTC = inherit(VirCu.Currency, function(value) {
    VirCu.Currency.call(this, value);

    this.symbol = 'BTC';
});


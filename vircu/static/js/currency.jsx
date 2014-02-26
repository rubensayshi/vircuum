/**
 * @jsx React.DOM
 */

VirCu.Currency = function(data) {
    var self = this;

    self.value  = data.value;
    self.symbol = data.symbol;
};

VirCu.Currency.prototype.display = function() {
    var self   = this;
    return self.value + " " + self.symbol;
};
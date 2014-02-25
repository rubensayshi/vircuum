/**
 * @jsx React.DOM
 */

VirCu.Order = function(data) {
    var self = this;

    self.id      = data.id;
    self.type    = data.type;
    self.price   = data.price;
    self.amount  = data.amount;
    self.status  = data.status;
    self.pending = data.pending;
    self.time    = data.time;
};

VirCu.Order.STATUS_OPEN      = 0;
VirCu.Order.STATUS_PARTIAL   = 1;
VirCu.Order.STATUS_DONE      = 2;
VirCu.Order.STATUS_PROCESSED = 3;
VirCu.Order.STATUS_RESET     = 99;

VirCu.Order.prototype.is_open = function() {
    return this.status <= VirCu.Order.STATUS_PARTIAL;
};

VirCu.Order.prototype.is_done = function() {
    return this.status >= VirCu.Order.STATUS_DONE;
};

VirCu.Order.prototype.is_processed = function() {
    return this.status >= VirCu.Order.STATUS_PROCESSED;
};

VirCu.Order.prototype.is_reset = function() {
    return this.status >= VirCu.Order.STATUS_RESET;
};

VirCu.Order.prototype.status_text = function() {
    switch (this.status) {
        case VirCu.Order.STATUS_OPEN:      return 'open';
        case VirCu.Order.STATUS_PARTIAL:   return 'partial';
        case VirCu.Order.STATUS_DONE:      return 'done';
        case VirCu.Order.STATUS_PROCESSED: return 'processed';
        case VirCu.Order.STATUS_RESET:     return 'reset';
    }

    return 'unknown';
};

/**
 * @jsx React.DOM
 */

WEB_SOCKET_SWF_LOCATION = "../WebSocketMain.swf";
WEB_SOCKET_DEBUG = true;

function Trader(container) {
    var self = this;

    self.socket = null;
    self.container = container;

    self.traderView = null;

    self.buy_orders = [];
    self.sell_orders = [];
    self.price_log = [];
    self.msg_log = [];

    self.connect();
    self.initDOM();
}

Trader.prototype.log = function(msg) {
    console.log(msg);
};

Trader.prototype.msg = function(msg, status) {
    console.log(msg, status);
};

Trader.prototype.order_container = function(type) {
    var self = this;

    if (type == 'buy') {
        return self.buy_orders;
    } else if (type == 'sell') {
        return self.sell_orders;
    } 
};

Trader.prototype.pushState = function() {
    var self = this;

    var current_buy_orders = self.buy_orders.filter(function(order) {
        return order.status < 99;
    });
    var current_sell_orders = self.sell_orders.filter(function(order) {
        return order.status < 99;
    });

    current_buy_orders.sort(function(orderA, orderB) {
        return orderA.price - orderB.price;
    });
    current_sell_orders.sort(function(orderA, orderB) {
        return orderA.price - orderB.price;
    });

    self.traderView.setState({
        buy_orders : current_buy_orders, 
        sell_orders : current_sell_orders,
        price_log : self.price_log,
        msg_log : self.msg_log
    });
    //self.traderView.forceUpdate(null);
}

Trader.prototype.connect = function() {
    var self = this;

    // socket.io specific code
    self.socket = io.connect('/trader');

    $(window).bind("beforeunload", function() {
        self.socket.disconnect();
    });

    self.socket.on('connect', function() {
        self.log('connect');
        self.socket.emit('init'); // triggers other events that will update out state
    });

    self.socket.on('msg', function(msg, status, ts) {
        self.msg_log.unshift({status : status, msg : msg, ts : ts || new Date()})
        self.pushState();
    });

    self.socket.on('tick', function(price, ts) {
        self.price_log.unshift({price : price, ts : ts});
        self.pushState();
    });

    self.socket.on('order', function(order) {
        var orders = self.order_container(order.type);

        var idx = -1;
        $.grep(orders, function(_order, _idx) {
            if (order.id == _order.id) {
                idx = _idx;
            }
        });

        if (idx !== -1) {
            orders[idx] = order;
        } else {
            orders.push(order);
        }

        self.pushState();
    });

    self.socket.on('reconnect', function () {
        self.log('reconnect');
    });

    self.socket.on('reconnecting', function () {
        self.log('reconnecting');
    });

    self.socket.on('error', function (e) {
        self.log('error', e ? e : 'unknown');
    });
};

Trader.prototype.initDOM = function() {
    var self = this;
    var Trader = VirCu.templates.Trader;

    self.traderView = React.renderComponent(
        <Trader />,
        self.container
    );
};

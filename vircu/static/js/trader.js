WEB_SOCKET_SWF_LOCATION = "../WebSocketMain.swf";
WEB_SOCKET_DEBUG = true;

function Trader() {
    var self = this;

    self.socket = null;

    self.connect();
}

Trader.prototype.log = function(msg) {
    console.log(msg);
};

Trader.prototype.msg = function(msg, status) {
    console.log(msg, status);
};

Trader.prototype.connect = function() {
    var self = this;

    // socket.io specific code
    self.socket = io.connect('/trader');

    $(window).bind("beforeunload", function() {
        self.socket.disconnect();
    });

    self.socket.on('connect', function() {
        self.log('connect');
    });

    self.socket.on('msg', function(msg, status) {
        self.msg(msg, status);
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

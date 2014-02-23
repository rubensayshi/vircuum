WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf";
WEB_SOCKET_DEBUG = true;

// socket.io specific code
var socket = io.connect('/trader');

$(window).bind("beforeunload", function() {
    socket.disconnect();
});

socket.on('connect', function() {
    console.log('connect');
});

socket.on('msg', function(msg, status) {
    console.log(status || 'msg', msg);
});

socket.on('reconnect', function () {
    console.log('reconnect');
});

socket.on('reconnecting', function () {
    console.log('reconnecting');
});

socket.on('error', function (e) {
    console.log('error', e ? e : 'unknown');
});


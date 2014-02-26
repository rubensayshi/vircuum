/**
 * @jsx React.DOM
 */


VirCu.templates.Price = React.createClass({
    render: function() {
        var MyDate   = VirCu.templates.Date,
            cx       = React.addons.classSet;

        var trClasses = {'price-log' : true}; trClasses = cx(trClasses);

        return (
    <tr className={trClasses}>
        <td><MyDate format="YYYY-MM-DD HH:mm:ss" timestamp={this.props.timestamp} /></td>
        <td>{this.props.price}</td>
    </tr>
        );
    }
});


VirCu.templates.Trader = React.createClass({
    getInitialState : function() {
        return {buy_orders : [], sell_orders : [], price_log : [], msg_log : []};
    },
    render : function() {
        var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;
        var Orders = VirCu.templates.Orders,
            Price = VirCu.templates.Price,
            LogMessage = VirCu.templates.LogMessage;

        var priceNodes = this.state.price_log.map(function(price) {
            return (<Price key={price.ts} timestamp={price.ts} price={price.price} />);
        });

        var logMessageNodes = this.state.msg_log.map(function(msg) {
            msg.key = "" + msg.ts + msg.status + msg.msg;
            return (<LogMessage key={msg.key} timestamp={msg.ts} status={msg.status} msg={msg.msg} />);
        });

        return (
    <div className="row">
        <div className="col-md-12">
            <div className="row">
                <div className="col-md-6">
                    <Orders title="Buy Orders" ref="buy_orders" orders={this.state.buy_orders} />
                </div>
                <div className="col-md-6">
                    <Orders title="Sell Orders" ref="sell_orders" orders={this.state.sell_orders} />
                </div>
            </div>
            <div className="row">
                <div className="col-md-8">
                    <div className="panel panel-default">
                        <div className="panel-heading">
                            <h2 className="panel-title"><i className="fa fa-fw fa-list"></i> Message Log</h2>
                        </div>
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Status</th>
                                    <th>Message</th>
                                </tr>
                            </thead>
                            <ReactCSSTransitionGroup component={React.DOM.tbody} transitionName="order">
                                {logMessageNodes}
                            </ReactCSSTransitionGroup>
                        </table>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="panel panel-default">
                        <div className="panel-heading">
                            <h2 className="panel-title"><i className="fa fa-fw fa-list"></i> Price Log</h2>
                        </div>
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <ReactCSSTransitionGroup component={React.DOM.tbody} transitionName="order">
                                {priceNodes}
                            </ReactCSSTransitionGroup>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
        );
    }
});
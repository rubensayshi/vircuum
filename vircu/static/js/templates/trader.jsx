/**
 * @jsx React.DOM
 */


VirCu.templates.Price = React.createClass({
    render : function() {
        var MyDate = VirCu.templates.Date;

        return (
            <li className="list-group-item">
                <MyDate timestamp={this.props.timestamp} format="YYYY-MM-DD HH:mm:ss" /> | <span>{this.props.price}</span>
            </li>
        );
    },
});


VirCu.templates.LogMessage = React.createClass({
    render : function() {
        var MyDate = VirCu.templates.Date;

        return (
            <li className="list-group-item">
                <MyDate timestamp={this.props.timestamp} format="YYYY-MM-DD HH:mm:ss" /> | <span>{this.props.status}</span> | <span>{this.props.msg}</span>
            </li>
        );
    },
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
                        <ReactCSSTransitionGroup component={React.DOM.ul} className="list-group" transitionName="order">
                            {logMessageNodes}
                        </ReactCSSTransitionGroup>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="panel panel-default">
                        <div className="panel-heading">
                            <h2 className="panel-title"><i className="fa fa-fw fa-list"></i> Price Log</h2>
                        </div>
                        <ReactCSSTransitionGroup component={React.DOM.ul} className="list-group" transitionName="order">
                            {priceNodes}
                        </ReactCSSTransitionGroup>
                    </div>
                </div>
            </div>
        </div>
    </div>
        );
    }
});
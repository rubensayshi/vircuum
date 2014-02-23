/**
 * @jsx React.DOM
 */

VirCu.templates.Trader = React.createClass({
    getInitialState: function() {
        return {buy_orders : [], sell_orders : []};
    },
    render: function() {
        var Orders = VirCu.templates.Orders;

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
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="panel panel-default">
                        <div className="panel-heading">
                            <h2 className="panel-title"><i className="fa fa-fw fa-list"></i> Price Log</h2>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
        );
    }
});
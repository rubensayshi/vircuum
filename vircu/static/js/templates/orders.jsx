/**
 * @jsx React.DOM
 */

VirCu.templates.Orders = React.createClass({
    render: function() {
        var Order = VirCu.templates.Order;
        var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

        var orderNodes = this.props.orders.map(function(order) {
            return <Order key={order.id} order={order} />;
        });

        return (
    <div className="panel panel-default">
        <div className="panel-heading">
            <h2 className="panel-title"><i className="fa fa-fw fa-list"></i> {this.props.title}</h2>
        </div>

        <table className="table">
            <thead>
                <tr>
                    <th>Amount</th>
                    <th>Price</th>
                    <th>Age</th>
                    <th>Status</th>
                </tr>
            </thead>
            <ReactCSSTransitionGroup component={React.DOM.tbody} transitionName="order">
                {orderNodes}
            </ReactCSSTransitionGroup>
        </table>
    </div>
        );
    }
});
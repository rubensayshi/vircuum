/**
 * @jsx React.DOM
 */

VirCu.templates.Order = React.createClass({
    render: function() {
        var MyDate   = VirCu.templates.Date,
            Currency = VirCu.templates.Currency,
            cx = React.addons.classSet;

        var trClasses = {'order' : true}; trClasses['order-' + this.props.order.status_text()] = true; trClasses = cx(trClasses);

        return (
    <tr className={trClasses}>
        <td><Currency currency={this.props.order.amount} /></td>
        <td><Currency currency={this.props.order.price} /></td>
        <td><MyDate timestamp={this.props.order.time} from_now={true} /></td>
        <td>{this.props.order.status_text()}</td>
    </tr>
        );
    }
});
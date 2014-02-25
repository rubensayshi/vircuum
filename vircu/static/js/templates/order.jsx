/**
 * @jsx React.DOM
 */

VirCu.templates.Order = React.createClass({
    render: function() {
        var MyDate = VirCu.templates.Date,
            cx = React.addons.classSet;

        var trClasses = {'order' : true}; trClasses['order-' + this.props.order.status_text()] = true; trClasses = cx(trClasses);

        return (
    <tr className={trClasses}>
        <td>{this.props.order.amount} GHS</td>
        <td>{this.props.order.price} <i className="fa fa-fw fa-btc"></i></td>
        <td><MyDate timestamp={this.props.order.time} from_now={true} /></td>
        <td>{this.props.order.status_text()}</td>
    </tr>
        );
    }
});
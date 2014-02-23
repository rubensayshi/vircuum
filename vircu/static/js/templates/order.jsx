/**
 * @jsx React.DOM
 */

VirCu.templates.Order = React.createClass({
    render: function() {
        var MyDate = VirCu.templates.Date;

        return (
    <tr>
        <td>{this.props.order.amount} GHS</td>
        <td>{this.props.order.price} <i className="fa fa-fw fa-btc"></i></td>
        <td><MyDate timestamp={this.props.order.time} from_now={true} /></td>
        <td>{this.props.order.status}</td>
    </tr>
        );
    }
});
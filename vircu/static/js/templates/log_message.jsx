/**
 * @jsx React.DOM
 */

VirCu.templates.LogMessage = React.createClass({
    render: function() {
        var MyDate   = VirCu.templates.Date,
            cx       = React.addons.classSet;

        var trClasses = {'log-message' : true}; trClasses = cx(trClasses);

        return (
    <tr className={trClasses}>
        <td><MyDate format="YYYY-MM-DD HH:mm:ss" timestamp={this.props.timestamp} /></td>
        <td>{this.props.status}</td>
        <td>{this.props.msg}</td>
    </tr>
        );
    }
});
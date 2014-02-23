/**
 * @jsx React.DOM
 */

VirCu.templates.Date = React.createClass({
    getInitialState : function() {
        return {dateStr: this.getDateStr()};
    },
    getDateStr : function() {
        var mom = moment(parseInt(this.props.timestamp, 10) * 1000);

        if (this.props.from_now) {
            return mom.fromNow();
        } else {
            return mom.format("LLL");
        }

    },
    update : function() {
        this.setState({dateStr: this.getDateStr()});
    },
    componentWillMount : function() {
        setInterval(this.update, this.props.interval || 3000);
    },
    render: function() {
        return <span>{this.state.dateStr}</span>;
    }
});
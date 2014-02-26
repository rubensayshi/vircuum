/**
 * @jsx React.DOM
 */

VirCu.templates.Symbol = React.createClass({
    render: function() {
        var symbol = this.props.symbol;
        if (symbol == 'BTC') {
            return (
            <i className="fa fa-btc" title={symbol}></i>
            );

        } else {
            return (
            <span>{symbol}</span>
            );
        }
    }
});

VirCu.templates.Currency = React.createClass({
    render: function() {
        var Symbol = VirCu.templates.Symbol;

        return (
        <span>{this.props.currency.value}{' '}<Symbol symbol={this.props.currency.symbol} /></span>
        );
    }
});

VirCu.LastUpdated = function(_el, _options) {
    var options = $.extend({}, {
            'old_threshold' : 60 * 1000
        }, _options, true);

    var $el     = $(_el),
        ts      = parseInt($el.data('date-last-updated'), 10) * 1000,
        mom     = moment(ts),
        date    = VirCu.Date($el.find('[data-date-last-updated-display]'), {'timestamp' : ts});

    var check = function() {
        var old = ts < ((new Date()).getTime() - options.old_threshold);

        if (old) {
            $el.removeClass('label-success').addClass('label-danger');
        }

        return old;
    };

    check();

    setInterval(function() {
        check();
    }, 30 * 1000);

    return {
        check : check,
        updateTs : function(_ts) {
            ts  = _ts;
            date.updateTs(_ts);
            check();
        }
    };
};

VirCu.Date = function(_el, _options) {
    var options = $.extend({}, {
            'timestamp': null,
            'from_now' : false,
            'format'   : 'LLL'
        }, _options, true);

    var $el     = $(_el),
        ts      = options.timestamp || parseInt($el.data('date'), 10) * 1000,
        mom     = moment(ts);

    var display = function() {
        if (options.from_now) {
            $el.html(mom.fromNow());
        } else {
            $el.html(mom.format(options.format));
        }
    };

    display();

    return {
        display : display,
        updateTs : function(_ts) {
            ts  = _ts;
            mom = moment(ts);
            display();
        }
    };
};

VirCu.DateManager = (function() {
    var old_threshold = 60 * 1000;
    var options = {
        'old_threshold' : 60 * 1000
    };

    var init = function(_options) {
        options = $.extend({}, options, _options, true);

        scan();
    };

    var scan = function() {
        scan_dates();
        scan_last_updated();
    };

    var scan_dates = function() {
        $('[data-date]').each(function() {
            var $el = $(this);

            if ($el.data('data-date-init')) {
                return;
            }

            $el.data('data-date-init', VirCu.Date(this));
        });
    };

    var scan_last_updated = function() {
        $('[data-date-last-updated]').each(function() {
            var $el = $(this);

            if ($el.data('data-date-last-updated-init')) {
                return;
            }

            $el.data('data-date-last-updated-init', VirCu.LastUpdated(this, {'old_threshold' : options.old_threshold}));
        });
    };

    return {
        init : init,
        scan : scan,
        scan_dates : scan_dates,
        scan_last_updated : scan_last_updated
    };
})();
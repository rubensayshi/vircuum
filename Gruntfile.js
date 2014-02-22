module.exports = function (grunt) {
    grunt.initConfig({
        /*
         * jshint
         */
        jshint : {
            gruntfile : ['Gruntfile.js'],
            all : ['vircu/static/js/*.js',
                   'vircu/static/js/**/*.js',
                   /* ignores: */
                   '!vircu/static/js/lib/*.js',
                   '!vircu/static/libs/*',
                   ],
            options : {
                globals : {
                    es5     : true,
                    browser : true,
                    indent  : 4,
                    undef   : true,
                    unused  : true
                },
                '-W065'  : true,
                '-W069'  : true
            }
        },

        /*
         * Javascript concatenation
         */
        concat : {
            jquery : {
                src : ['vircu/static/js/lib/jquery-1.8.2.min.js'],
               dest : 'vircu/static/compiled/jquery.js'
            },
            desktop: {
                src : ['vircu/static/libs/bootstrap-3.0.3/js/transition.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/alert.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/button.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/carousel.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/collapse.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/dropdown.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/modal.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/tooltip.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/popover.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/scrollspy.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/tab.js',
                       'vircu/static/libs/bootstrap-3.0.3/js/affix.js',
                       'vircu/static/libs/bootstrap-switch/build/js/bootstrap-switch.js',
                       'vircu/static/js/lib/bootstrapx-clickover.js',
                       'vircu/static/js/lib/jquery.scrollto.js',
                       'vircu/static/js/lib/jquery.localScroll.js',
                       'vircu/static/js/lib/jquery.cookie.js',
                       'vircu/static/js/lib/jquery.inview.js',
                       'vircu/static/js/lib/jquery.placeholder.js',
                       'vircu/static/js/lib/jquery.ba-dotimeout.js',
                       'vircu/static/js/lib/jquery.lazyload.js',
                       'vircu/static/js/lib/purl.js',
                       'vircu/static/js/lib/moment.js',

                       'vircu/static/js/init.js',
                       'vircu/static/js/date.js',
                       ],
                dest : 'vircu/static/compiled/desktop.js'
            },
            highstock: {
                src : ['vircu/static/libs/highstock-v1.3.7/highstock.src.js',
                       'vircu/static/libs/highstock-v1.3.7/highcharts-more.src.js'
                       ],
                dest : 'vircu/static/compiled/highstock.js'
            }
        },

        /*
         * Javascript uglifying
         */
        uglify : {
            dist : {
                files : {
                    'vircu/static/compiled/jquery.min.js'        : ['<%= concat.jquery.dest %>'],
                    'vircu/static/compiled/desktop.min.js'       : ['<%= concat.desktop.dest %>'],
                    'vircu/static/compiled/highstock.min.js'     : ['<%= concat.highstock.dest %>'],
                }
            }
        },


        less : {
            /*
             * Less processing
             *
             * !@!@ IMPORTANT; CHANGES TO THIS CONFIG ALSO HAS TO BE MADE TO THE MINIFIED CONFIG BELOW @!@!
             */
            dev : {
                options : {
                    paths : ['vircu/static/libs', 'vircu/static/less', 'vircu/static/css', 'vircu/static/compiled']
                },
                files : {
                    'vircu/static/compiled/desktop.css'      : ['vircu/static/less/desktop.less'],
                }
            },
            /*
             * Less uglifying
             */
            dist : {
                options : {
                    yuicompress : true,
                    paths       : ['vircu/static/libs', 'vircu/static/less', 'vircu/static/css', 'vircu/static/compiled']
                },
                files : {
                    'vircu/static/compiled/desktop.min.css'  : ['vircu/static/less/desktop.less'],
                }
            }
        },

        /*
         * Watch
         */
        watch : {
            options : {},
            gruntfile : {
                files : ['Gruntfile.js'],
                tasks : ['jshint:gruntfile', 'default']
            },
            less : {
                files : ['vircu/static/css/*.less', 'vircu/static/less/*.less', 'vircu/static/less/**/*.less'],
                tasks : ['less:dev']
            },
            js : {
                files : ['vircu/static/js/*.js', 'vircu/static/js/**/*.js'],
                tasks : ['jshint:all', 'concat']
            }
        },
    });

    grunt.loadNpmTasks('grunt-smushit');
    grunt.loadNpmTasks("grunt-image-embed");
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-casperjs');
    grunt.loadNpmTasks('grunt-notify');

    grunt.registerTask('default', ['jshint', 'concat', 'uglify', 'less']);
};
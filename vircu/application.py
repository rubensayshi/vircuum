from vircu.common import is_frame_request
def create_app(full = True):
    from flask import Flask
    from vircu import constants
    import sys
    sys.path.append('vircu')

    app = Flask(__name__)
    app.static_path = app.static_folder

    _setup_config(app)
    _setup_version(app)
    _setup_db(app)
    _setup_tldextract(app)
    
    _setup_statics(app)
    _setup_menu(app)
    _setup_blueprints(app)
    
    from vircu.view.jinja_helpers import setup_jinja_helpers
    setup_jinja_helpers(app)

    _setup_clicontext(app)

    return app


def get_environment():
    import os
    """return the environment from an environment variable,
    should be development|test|staging|production"""
    return os.environ.get('ENVIRONMENT', 'development')


def _setup_config(app):
    from vircu.config import config
    app.config.update(config)


def _setup_version(app):
    from vircu.config import MAIN_VERSION, STATIC_VERSION

    app.config['MAIN_VERSION']   = MAIN_VERSION
    app.config['STATIC_VERSION'] = STATIC_VERSION


def _setup_db(app):
    from flask_sqlalchemy import SQLAlchemy
    from vircu.models import db

    db.init_app(app)
    db.app = app
    app.db = db


def _setup_tldextract(app):
    import tldextract
    app.tldextract = tldextract.TLDExtract(cache_file = app.config['TMP_DIR'] + "/.tld_set")


def _setup_menu(app):
    from vircu.view.menu import MenuManager
    from vircu.view.vircu_menus import MainMenu

    try:
        app.menu = MenuManager(app)

        app.main_menu = MainMenu()

    finally:
        # dispose of the engines connection pool because we're most likely in a main thread instead of a local worker thread
        #  and the engine shouldn't be shared between threads
        app.db.session.close_all()
        app.db.engine.dispose()


def _setup_statics(app):
    from flask import redirect, url_for
    from vircu.util.statics_cache import static_url
    
    """create our custom static route replacing the default from flask completely.
    we do this to add any custom headers we'd like in there
    and so that we can have versioned URLs

    we leave the old unversioned static URL in place as fallback,
     but if you ever have an URL like /static/v<dirname-10-chars-long>/mystatic.img then it will fail
    """

    @app.route('/static/vDEBUG/<path:filename>')
    @app.route('/static/<path:filename>')
    @app.route('/static/v<string(length='+str(app.config['VERSION_STRING_LENGTH'])+'):version>/<path:filename>')
    def static(filename, version = None):
        from flask.helpers import send_from_directory
        r = send_from_directory(app.config['STATIC_DIR'], filename)

        if version and version != app.config['STATIC_VERSION']:
            return redirect(static_url(url_for('static', filename = filename, version = app.config['STATIC_VERSION'])))

        r.headers['Access-Control-Allow-Origin'] = '*'

        return r


def _setup_blueprints(app):
    from vircu.view.blueprints.main import main

    app.register_blueprint(main)


def _setup_clicontext(app):
    def get_cli_context(**kwargs):
        from flask import _request_ctx_stack
        
        # return the current request context if possible
        if _request_ctx_stack.top is not None:
            return _request_ctx_stack.top
        # need to specify port 80 here, otherwise (if left empty) werkzeug's routing.py adds ":port" to urls
        options = {'SERVER_NAME' : app.config['DEFAULT_SERVER_NAME'],
                   'SERVER_PORT' : '80',
                   'REQUEST_METHOD' : 'GET',
                   'wsgi.url_scheme' : 'http'}
        options.update(kwargs or {})

        return app.request_context(options)

    app.cli_request_context = get_cli_context



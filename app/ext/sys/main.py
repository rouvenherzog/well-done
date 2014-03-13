# -*- coding:utf-8 -*-
from flask import request, send_file
from ext.sys.database import db
from flask import Flask, render_template, Blueprint
from config import ConfigBase

# TODO: clear all view related logic,

def __import_blueprint(blueprint_str):
    split = blueprint_str.split('.')
    module_path = '.'.join(split[0: len(split) - 1])
    variable_name = split[-1]
    mod = __import__(module_path, fromlist=[variable_name])
    return getattr(mod, variable_name)


def app_factory(config, app_name=None, blueprints=None):
    if type(config) == str:
        modules = '.'.join(config.split('.')[0:-1])
        classname = config.split('.')[-1]
        config = getattr(__import__(modules), classname )

    app_name = config.PROJECT_NAME or __name__
    app = Flask(app_name)
    configure_app(app, config)

    all_blueprints = ConfigBase.BLUEPRINTS
    all_blueprints.extend(blueprints or config.BLUEPRINTS)
    configure_blueprints(app, all_blueprints)
    configure_error_handlers(app)
    configure_database(app)
    configure_context_processors(app)
    configure_template_filters(app)
    configure_extensions(app)
    configure_before_request(app)
    configure_views(app)
    configure_apps(app)
    return app


def configure_app(app, config):
    from config import ConfigDefault as default
    app.config.from_object(default)
    app.config.from_object(config)
    app.config.from_envvar("APP_CONFIG", silent=True)  # avaiable in the server
    app.url_map.strict_slashes = False # No trailing slashes

def configure_blueprints(app, blueprints):
    app.admins = {}
    # register nebula blueprint

    for blueprint_config in blueprints:
        blueprint = None
        kw = {}

        if isinstance(blueprint_config, basestring):
            blueprint = blueprint_config
        elif isinstance(blueprint_config, tuple):
            blueprint = blueprint_config[0]
            kw = blueprint_config[1]

        # check and import admin if configured in blueprint
        blueprint = __import_blueprint(blueprint)
        if isinstance(blueprint, Blueprint):
            try:
                app.register_blueprint(blueprint, **kw)
            except:
                if app.debug:
                    raise

def configure_error_handlers(app):
    pass

def configure_database(app):
    "Database configuration should be set here"
    # uncomment for sqlalchemy support
    db.app = app
    db.init_app(app)


def configure_context_processors(app):
    "Modify templates context here"
    pass


def configure_apps(app):
    pass


def configure_template_filters(app):
    "Configure filters and tags for jinja"

    def nl2br(value):
        from jinja2 import Markup, escape
        import re
        _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
        result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                              for p in _paragraph_re.split(escape(value)))
        return Markup(result)

    app.jinja_env.globals.update(nl2br=nl2br)


def configure_extensions(app):
    "Configure extensions like mail and login here"
    from flask.ext.security import Security, SQLAlchemyUserDatastore
    from ext.sys.database import db
    from models.models import User, Role
    from flask_security.forms import RegisterForm, TextField, Required

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    class ExtendedRegisterForm(RegisterForm):
        name = TextField('name', [Required()])

    # Setup Flask-Security
    app.security = Security(
        app,
        user_datastore,
        register_form=ExtendedRegisterForm
    )

    # if not app.debug:
    if app.config['CLOUDFILES_ENABLED']:
        from utils.cloud import cloudfiles
        cloudfiles.init_app(app)

    # import nebula
    # from flask.ext.login import LoginManager
    # from nebula.shops.models.customer import Customer
    # nebula.login_manager = LoginManager()
    # nebula.login_manager.init_app( app )

    # from flask.ext.mail import Mail
    # nebula.mail = Mail(app)

    # @nebula.login_manager.user_loader
    # def load_customer( customer_id ):
    #     return Customer.query.get( customer_id )

    # nebula.user_datastore = user_datastore
    # nebula.security = security
    # app.users = user_datastore

    # init cache lib
    # nebula.cache.init_app(app)
    # if app.debug:
    #     toolbar = DebugToolbarExtension(app)

def configure_before_request(app):
    pass

def configure_views(app):
    @app.route('/media/<path:file_path>')
    def render_media( file_path ):
        print file_path
        return send_file( app.config['MEDIA_LOCATION'] + '/' + file_path, mimetype='image/gif')
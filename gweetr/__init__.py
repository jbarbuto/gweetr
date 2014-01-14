"""__init__.py"""

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from gweetr.database import db


def create_app():
    """Create the app using the factory pattern."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('settings.cfg')
    app.config.from_envvar('GWEETR_CONFIG_PATH', silent=True)
    app.secret_key = app.config['APP_SECRET_KEY']
    if app.config['USE_PROXY']:
        app.wsgi_app = ProxyFix(app.wsgi_app)

    db.init_app(app)
    with app.app_context():
        from . import controllers
        db.create_all()

    return app

def main():
    """Run the app."""
    app = create_app()
    app.run(debug=app.debug)

if __name__ == '__main__':
    main()

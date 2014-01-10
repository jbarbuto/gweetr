"""__init__.py"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('settings.cfg')
app.config.from_envvar('GWEETR_CONFIG_PATH', silent=True)
app.secret_key = app.config['APP_SECRET_KEY']
if app.config['USE_PROXY']:
    app.wsgi_app = ProxyFix(app.wsgi_app)

db = SQLAlchemy(app)

import gweetr.controllers


def main():
    """Run the app."""
    app.run(debug=app.debug)

if __name__ == '__main__':
    main()

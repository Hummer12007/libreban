from sanic import Sanic
from sanic_jinja2 import SanicJinja2

from gino.ext.sanic import Gino

app = Sanic(__name__)
app.config.from_pyfile('config')

jinja = SanicJinja2(app, pkg_path=f'../{app.config.FRONTEND_PATH}/templates')

db = Gino()
db.init_app(app)

app.static('static', app.config.FRONTEND_PATH)

import libreban.routes
import libreban.model

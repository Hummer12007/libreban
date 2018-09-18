from sys import argv
from libreban.app import app, db
from libreban.socket import *

if __name__ == '__main__':
    if '-n' in argv:
        exit(0)
    if '-p' in argv:
        @app.listener('before_server_start')
        async def drop_tables(app, loop):
            import inspect, libreban
            await db.gino.drop_all(tables=
                (obj.__table__ for name, obj in inspect.getmembers(libreban.model) if inspect.isclass(obj)))
    if '-c' in argv:
        @app.listener('before_server_start')
        async def create_db(app, loop):
            await db.gino.create_all()
    app.run(debug=app.config.DEBUG,
            host=app.config.HOST,
            port=app.config.PORT,
            workers=app.config.WORKERS)

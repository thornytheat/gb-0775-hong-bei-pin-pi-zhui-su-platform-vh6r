import os

from flask import Flask,jsonify

from app.api import api
from app.config import PORT
from app.errors import RoastError
from app.modules.runs.cabinet import Cabinet
from app.web import station


def create_app(database=None):
    app=Flask(__name__)
    app.config['MAX_CONTENT_LENGTH']=3_000_000
    app.extensions['lot_cabinet']=Cabinet(database or os.environ.get('ROAST_CABINET','var/cabinet'))
    app.register_blueprint(api)
    app.register_blueprint(station)
    app.register_error_handler(RoastError,lambda e:(jsonify(code=e.code,message=str(e)),e.status))
    app.register_error_handler(413,lambda _:(jsonify(code='TOO_LARGE',message='秤单体积超限'),413))
    app.add_url_rule('/health',view_func=lambda:jsonify(status='ok'))
    return app


if __name__=='__main__':
    create_app().run(host='127.0.0.1',port=PORT)

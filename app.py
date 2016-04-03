import os
from fbook import create_app
from config import config as app_conf

conf = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(app_conf[conf])


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Accept, Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)

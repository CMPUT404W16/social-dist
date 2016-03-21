import os
from fbook import create_app
from config import config as app_conf

conf = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(app_conf[conf])


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)


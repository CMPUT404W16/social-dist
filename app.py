import os
from fbook import create_app
from config import config as app_conf
from fbook.db import db

conf = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(app_conf[conf])
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)


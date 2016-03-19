try:
    from fbook import create_app, db, models
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(".."))

from fbook import create_app, db, models
from config import config as app_conf
testing_app = create_app(app_conf['testing'])